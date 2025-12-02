"""批量推文生成节点"""
from ..utils.llm_client import LLMClient
from ..utils.persona_utils import extract_few_shot_examples, search_character_book
from datetime import datetime, timedelta


class BatchTweetGenerator:
    """批量生成多天推文（一次执行生成多天内容）"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "persona": ("PERSONA",),
                "calendar_plan": ("CALENDAR_PLAN",),  # 从 CalendarManager 连接
                "num_days": ("INT", {
                    "default": 7,
                    "min": 1,
                    "max": 31,
                    "tooltip": "要生成的天数"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "OpenAI/Claude API key"
                }),
                "api_base": ("STRING", {
                    "default": "https://api.openai.com/v1",
                    "multiline": False
                }),
                "model": ("STRING", {
                    "default": "gpt-4",
                    "multiline": False
                }),
            },
            "optional": {
                "start_day_offset": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 30,
                    "tooltip": "起始日期偏移（0=今天，1=明天）"
                }),
                "temperature": ("FLOAT", {
                    "default": 0.85,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.05
                }),
            }
        }

    RETURN_TYPES = ("LIST", "LIST", "LIST")  # 返回列表
    RETURN_NAMES = ("tweets", "scene_hints", "dates")
    FUNCTION = "generate_batch"
    CATEGORY = "TwitterChat"
    DESCRIPTION = "Generate multiple days of tweets in one execution"

    def generate_batch(
        self,
        persona,
        calendar_plan,
        num_days,
        api_key,
        api_base,
        model,
        start_day_offset=0,
        temperature=0.85
    ):
        """
        批量生成多天推文

        参数:
            persona: Character Card 数据
            calendar_plan: 运营日历（包含多天计划）
            num_days: 要生成的天数
            api_key: LLM API key
            api_base: API base URL
            model: 模型名称
            start_day_offset: 起始日期偏移
            temperature: 温度参数

        返回:
            (tweets, scene_hints, dates) 推文列表、场景列表、日期列表
        """
        print(f"[BatchTweetGenerator] 开始批量生成 {num_days} 天的内容")

        tweets = []
        scene_hints = []
        dates = []

        # 初始化LLM客户端
        llm_client = LLMClient(api_key=api_key, api_base=api_base, model=model)

        # 从人设获取时区
        timezone = self._get_timezone(persona)

        # 循环生成每一天的内容
        for day in range(num_days):
            day_offset = start_day_offset + day

            try:
                # 计算当天日期
                date_str = self._calculate_date(day_offset, timezone)

                print(f"[BatchTweetGenerator] 生成第 {day+1}/{num_days} 天内容 (日期: {date_str})")

                # 从日历获取当天计划
                day_plan = calendar_plan.get(date_str, {})

                # 生成推文
                tweet, scene_hint = self._generate_single_day(
                    persona=persona,
                    day_plan=day_plan,
                    date_str=date_str,
                    llm_client=llm_client,
                    temperature=temperature
                )

                tweets.append(tweet)
                scene_hints.append(scene_hint)
                dates.append(date_str)

                print(f"[BatchTweetGenerator] ✓ {date_str} 生成完成")

            except Exception as e:
                error_msg = f"生成失败: {str(e)}"
                print(f"[BatchTweetGenerator] ✗ {date_str} {error_msg}")
                tweets.append(f"[ERROR] {error_msg}")
                scene_hints.append("")
                dates.append(date_str)

        print(f"[BatchTweetGenerator] 批量生成完成: {len(tweets)}/{num_days} 天成功")

        return (tweets, scene_hints, dates)

    def _generate_single_day(self, persona, day_plan, date_str, llm_client, temperature):
        """生成单天内容（复用 TweetGenerator 的逻辑）"""
        # 构建系统提示词
        system_prompt = self._build_system_prompt(persona)

        # 构建用户提示词
        user_prompt = self._build_user_prompt(persona, day_plan, date_str)

        # 调用LLM
        response = llm_client.chat_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature
        )

        # 解析响应
        tweet, scene_hint = self._parse_response(response)

        return tweet, scene_hint

    def _build_system_prompt(self, persona):
        """构建系统提示词"""
        system_prompt = persona["data"].get("system_prompt", "")
        if not system_prompt:
            name = persona["data"].get("name", "Unknown")
            system_prompt = f"你是{name}，请根据要求生成推文。"

        return system_prompt

    def _build_user_prompt(self, persona, day_plan, date_str):
        """构建用户提示词"""
        name = persona["data"].get("name", "Unknown")
        topic = day_plan.get("theme", "日常分享")
        content_direction = day_plan.get("content_direction", "")
        scene_suggestion = day_plan.get("suggested_scene", "")

        # 提取示例推文
        tweet_examples = extract_few_shot_examples(persona, count=1)
        example_text = tweet_examples[0] if tweet_examples else "今天的生活真美好~"

        user_prompt = f"""请以 {name} 的身份撰写一条关于「{topic}」的推文，并描述配图场景。

日期：{date_str}

今日运营计划：
- 主题：{topic}
- 内容方向：{content_direction}
- 建议场景：{scene_suggestion}

参考推文示例（风格和语气）：
{example_text}

要求：
1. 结合日期和主题撰写内容
2. 保持人设的语言风格和性格特点
3. 引导粉丝互动（点赞/评论）
4. 使用合适的 emoji
5. 字数 60-150 字
6. 添加 1-3 个相关标签

输出格式（严格按照此格式）：
TWEET: [推文内容，包含 emoji 和标签]
SCENE: [场景描述，如: traditional courtyard, wearing hanfu, afternoon sunlight]

场景描述要求：
- 用英文描述，简洁明了
- 包含地点和氛围
- 包含服装/姿态（如果推文中提到）
- 与推文内容和人设完全匹配
"""
        return user_prompt

    def _parse_response(self, response):
        """解析LLM响应"""
        tweet = ""
        scene_hint = ""

        lines = response.strip().split('\n')
        for line in lines:
            if line.startswith("TWEET:"):
                tweet = line.replace("TWEET:", "").strip()
            elif line.startswith("SCENE:"):
                scene_hint = line.replace("SCENE:", "").strip()

        if not tweet:
            tweet = response.strip()

        return tweet, scene_hint

    def _get_timezone(self, persona):
        """从人设获取时区"""
        try:
            location = persona.get("data", {}).get("core_info", {}).get("location", {})
            return location.get("timezone")
        except:
            return None

    def _calculate_date(self, day_offset, timezone):
        """计算日期字符串"""
        if timezone:
            from zoneinfo import ZoneInfo
            now = datetime.now(ZoneInfo(timezone))
        else:
            now = datetime.now()

        target_date = now + timedelta(days=day_offset)
        return target_date.strftime("%Y-%m-%d")


# 节点注册
NODE_CLASS_MAPPINGS = {
    "BatchTweetGenerator": BatchTweetGenerator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BatchTweetGenerator": "Batch Tweet Generator"
}
