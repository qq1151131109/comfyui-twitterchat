"""人设加载节点"""
# 使用相对导入
from ..utils.persona_utils import (
    load_persona_from_json,
    generate_persona_summary
)
import os
import json


class PersonaLoader:
    """人设加载器（支持文件路径或JSON字符串）"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_mode": (["file", "json_string"], {
                    "default": "file",
                    "tooltip": "选择输入模式：file=从文件加载，json_string=直接传入JSON"
                }),
                "persona_file": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "path/to/persona.json (仅在file模式下使用)"
                }),
            },
            "optional": {
                "persona_json": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "完整的Persona JSON字符串 (仅在json_string模式下使用)",
                    "forceInput": True  # 允许从API传入
                }),
                "user_id": ("STRING", {
                    "default": "",
                    "placeholder": "用户ID（用于日志和输出管理）"
                }),
            }
        }

    RETURN_TYPES = ("PERSONA", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("persona", "summary", "system_prompt", "user_id")
    FUNCTION = "load"
    CATEGORY = "TwitterChat"
    DESCRIPTION = "Load persona from file path or JSON string (multi-user support)"

    def load(self, input_mode, persona_file, persona_json="", user_id=""):
        """
        加载人设 Character Card（支持两种模式）

        参数:
            input_mode: "file" 或 "json_string"
            persona_file: JSON 文件路径（file模式）
            persona_json: JSON 字符串（json_string模式）
            user_id: 用户ID（用于日志和输出）

        返回:
            (persona, summary, system_prompt, user_id)
        """
        try:
            # 根据模式加载人设
            if input_mode == "file":
                if not persona_file or not os.path.exists(persona_file):
                    raise ValueError(f"文件模式：请提供有效的 persona_file 路径: {persona_file}")
                persona = load_persona_from_json(persona_file)
                print(f"[PersonaLoader] 从文件加载人设: {persona_file}")

            elif input_mode == "json_string":
                if not persona_json or persona_json.strip() == "":
                    raise ValueError("JSON字符串模式：persona_json 不能为空")

                # 预处理 JSON 字符串
                # 1. 去除 UTF-8 BOM（如果存在）
                persona_json_cleaned = persona_json.lstrip('\ufeff')

                # 2. 去除前后空白字符
                persona_json_cleaned = persona_json_cleaned.strip()

                # 3. 检查是否有多个 JSON 对象（"Extra data" 的常见原因）
                # 尝试找到第一个完整的 JSON 对象
                if persona_json_cleaned.startswith('{'):
                    # 简单的括号匹配，找到第一个完整的 JSON 对象
                    depth = 0
                    in_string = False
                    escape = False
                    first_json_end = -1

                    for i, char in enumerate(persona_json_cleaned):
                        if escape:
                            escape = False
                            continue
                        if char == '\\':
                            escape = True
                            continue
                        if char == '"' and not escape:
                            in_string = not in_string
                        if not in_string:
                            if char == '{':
                                depth += 1
                            elif char == '}':
                                depth -= 1
                                if depth == 0:
                                    first_json_end = i + 1
                                    break

                    if first_json_end > 0 and first_json_end < len(persona_json_cleaned):
                        # 发现有额外内容
                        extra_content = persona_json_cleaned[first_json_end:].strip()
                        if extra_content:
                            print(f"[PersonaLoader] ⚠️  警告: 检测到JSON对象后有额外内容，已自动截取第一个JSON对象")
                            print(f"[PersonaLoader]    额外内容的前100字符: {repr(extra_content[:100])}")
                            persona_json_cleaned = persona_json_cleaned[:first_json_end]

                # 解析JSON字符串
                try:
                    persona = json.loads(persona_json_cleaned)
                    print(f"[PersonaLoader] 从JSON字符串加载人设 (user_id={user_id}, 长度={len(persona_json_cleaned)}字符)")
                except json.JSONDecodeError as e:
                    # 提供详细的错误信息帮助调试
                    error_pos = e.pos if hasattr(e, 'pos') else 0
                    context_start = max(0, error_pos - 50)
                    context_end = min(len(persona_json_cleaned), error_pos + 50)
                    error_context = persona_json_cleaned[context_start:context_end]

                    error_msg = f"JSON字符串解析失败: {str(e)}\n"
                    error_msg += f"错误位置: line {e.lineno}, column {e.colno}\n"
                    error_msg += f"错误位置附近的内容: {repr(error_context)}\n"
                    error_msg += f"提示: 请检查JSON格式是否正确，是否有多余的字符或重复的JSON对象"
                    raise ValueError(error_msg)

            else:
                raise ValueError(f"不支持的输入模式: {input_mode}")

            # 验证人设结构
            if "data" not in persona:
                raise ValueError("人设JSON缺少'data'字段，请检查格式")

            # 生成摘要
            summary = generate_persona_summary(persona)

            # 提取系统提示词
            system_prompt = persona["data"].get("system_prompt", "")

            # 如果user_id为空，尝试从persona中提取
            if not user_id:
                user_id = persona["data"].get("user_id", "")

            return (persona, summary, system_prompt, user_id)

        except Exception as e:
            raise RuntimeError(f"加载人设失败: {str(e)}")


# 节点注册
NODE_CLASS_MAPPINGS = {
    "PersonaLoader": PersonaLoader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PersonaLoader": "Load Persona"
}
