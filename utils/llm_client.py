"""LLM API 客户端"""
try:
    from openai import OpenAI, AzureOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("[LLM Client] 警告: 未安装 openai 库，将使用 requests 回退模式")

import requests
import json
import time


class LLMClient:
    """通用 LLM API 客户端（支持 OpenAI/Claude/本地模型）"""

    def __init__(self, api_key: str, api_base: str = "https://api.openai.com/v1", model: str = "gpt-4"):
        self.api_key = api_key
        self.api_base = api_base.rstrip('/')
        self.model = model

        # 优先使用 OpenAI SDK（更稳定，自带重试机制）
        self.use_sdk = HAS_OPENAI and not self._is_non_openai_endpoint(api_base)

        if self.use_sdk:
            # 初始化 OpenAI 客户端
            if "openai.azure.com" in api_base:
                # Azure OpenAI
                api_version = api_base.split("=")[-1].split("/")[0]
                azure_endpoint = "https://" + api_base.split("//")[1].split("/")[0]
                self.client = AzureOpenAI(
                    api_key=api_key,
                    api_version=api_version,
                    azure_endpoint=azure_endpoint,
                    max_retries=3,  # 自动重试3次
                    timeout=180.0   # 默认超时3分钟
                )
            else:
                # 标准 OpenAI 或兼容端点
                self.client = OpenAI(
                    api_key=api_key,
                    base_url=api_base,
                    max_retries=3,  # 自动重试3次
                    timeout=180.0   # 默认超时3分钟
                )
            print(f"[LLM Client] 使用 OpenAI SDK 模式（自带重试机制）")
        else:
            self.client = None
            print(f"[LLM Client] 使用 Requests 模式")

    def _is_non_openai_endpoint(self, base_url: str) -> bool:
        """检查是否为非 OpenAI 兼容端点"""
        # 一些已知的非兼容端点
        non_openai_endpoints = [
            "anthropic.com",  # Claude 官方 API 格式不同
        ]
        return any(endpoint in base_url for endpoint in non_openai_endpoints)

    def generate(self, messages: list, temperature: float = 0.7, max_tokens: int = 300,
                 timeout: int = 180, max_retries: int = 3) -> str:
        """
        调用 LLM 生成内容（带重试机制）

        参数:
            messages: 消息列表 [{"role": "system", "content": "..."}, ...]
            temperature: 温度参数 (0.0-2.0)
            max_tokens: 最大 token 数
            timeout: 超时时间（秒），默认 180 秒
            max_retries: 最大重试次数（仅在 requests 模式有效）

        返回:
            生成的文本
        """
        if self.use_sdk:
            # 使用 OpenAI SDK（推荐，自带重试）
            return self._generate_with_sdk(messages, temperature, max_tokens, timeout)
        else:
            # 回退到 requests（手动重试）
            return self._generate_with_requests(messages, temperature, max_tokens, timeout, max_retries)

    def _generate_with_sdk(self, messages: list, temperature: float, max_tokens: int, timeout: int) -> str:
        """使用 OpenAI SDK 生成（推荐方式）"""
        try:
            # OpenAI SDK 自动处理重试和超时
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout
            )

            return response.choices[0].message.content

        except Exception as e:
            # OpenAI SDK 的异常已经很详细了
            error_msg = str(e)

            # 提供更友好的错误提示
            if "timeout" in error_msg.lower():
                raise RuntimeError(f"LLM API 调用超时（超过 {timeout} 秒）。建议增加 timeout 参数或检查 API 服务状态。")
            elif "rate_limit" in error_msg.lower():
                raise RuntimeError(f"API 速率限制：{error_msg}")
            elif "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
                raise RuntimeError(f"API 认证失败，请检查 API Key 是否正确：{error_msg}")
            elif "connection" in error_msg.lower():
                raise RuntimeError(f"网络连接失败：{error_msg}")
            else:
                raise RuntimeError(f"LLM API 调用失败: {error_msg}")

    def _generate_with_requests(self, messages: list, temperature: float, max_tokens: int,
                                timeout: int, max_retries: int) -> str:
        """使用 requests 生成（回退方式，手动重试）"""
        url = f"{self.api_base}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        last_error = None

        for attempt in range(max_retries):
            try:
                # 根据 max_tokens 动态调整超时
                adjusted_timeout = timeout
                if max_tokens > 2000:
                    adjusted_timeout = int(timeout * 1.5)

                print(f"[LLM] 尝试 {attempt + 1}/{max_retries}，超时: {adjusted_timeout}s...")

                response = requests.post(url, headers=headers, json=payload, timeout=adjusted_timeout)
                response.raise_for_status()
                data = response.json()

                # 成功返回
                return data["choices"][0]["message"]["content"]

            except requests.exceptions.Timeout:
                last_error = f"请求超时（超过 {adjusted_timeout} 秒）"
                print(f"[LLM] 尝试 {attempt + 1} 超时: {last_error}")

                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    print(f"[LLM] {wait_time} 秒后重试...")
                    time.sleep(wait_time)

            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if e.response else "unknown"

                # 4xx 客户端错误通常不需要重试
                if 400 <= status_code < 500:
                    try:
                        error_detail = e.response.json()
                        last_error = f"HTTP {status_code}: {error_detail.get('error', {}).get('message', str(e))}"
                    except:
                        last_error = f"HTTP {status_code}: {str(e)}"

                    print(f"[LLM] 客户端错误（不重试）: {last_error}")
                    break

                # 5xx 服务器错误可以重试
                else:
                    last_error = f"HTTP {status_code}: {str(e)}"
                    print(f"[LLM] 尝试 {attempt + 1} 失败: {last_error}")

                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"[LLM] {wait_time} 秒后重试...")
                        time.sleep(wait_time)

            except requests.exceptions.ConnectionError as e:
                last_error = f"网络连接失败: {str(e)}"
                print(f"[LLM] 尝试 {attempt + 1} 连接失败: {last_error}")

                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"[LLM] {wait_time} 秒后重试...")
                    time.sleep(wait_time)

            except KeyError as e:
                last_error = f"API 响应格式错误，缺少字段: {str(e)}"
                print(f"[LLM] 响应格式错误（不重试）: {last_error}")
                break

            except Exception as e:
                last_error = f"未知错误: {str(e)}"
                print(f"[LLM] 尝试 {attempt + 1} 出现未知错误: {last_error}")

                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"[LLM] {wait_time} 秒后重试...")
                    time.sleep(wait_time)

        # 所有重试都失败
        raise RuntimeError(f"LLM API 调用失败（已重试 {max_retries} 次）: {last_error}")
