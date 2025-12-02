"""推文生成节点"""
# 使用相对导入
from ..utils.llm_client import LLMClient
from ..utils.persona_utils import extract_few_shot_examples, search_character_book


class TweetGenerator:
    """推文生成器（结合人设+上下文）"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "persona": ("PERSONA",),
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
                "calendar_plan": ("CALENDAR_PLAN",),  # 从 CalendarManager 连接
                "context": ("CONTEXT",),  # 可选！
                "is_batch_mode": ("BOOLEAN",),  # 批量模式标记（从 CalendarManager 连接）
                "custom_topic": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Custom topic (overrides calendar plan theme)"
                }),
                "temperature": ("FLOAT", {
                    "default": 0.85,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.05
                }),
                "custom_user_prompt_template": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "自定义用户提示词模板（留空使用默认）。支持变量：{name}, {topic}, {plan_guidance}, {template_example}, {kb_info}"
                }),
                "system_prompt_override": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "⭐ 直接编辑完整系统提示词（留空则自动生成）"
                }),
                "user_prompt_override": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "⭐ 直接编辑完整用户提示词（留空则自动生成）"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("tweet", "scene_hint", "system_prompt", "user_prompt")
    FUNCTION = "generate"
    CATEGORY = "TwitterChat"
    DESCRIPTION = "Generate tweets and scene hints based on persona, calendar plan and context"

    def generate(self, persona, api_key, api_base, model,
                 calendar_plan=None, context=None, is_batch_mode=False, custom_topic="",
                 temperature=0.85, custom_user_prompt_template="",
                 system_prompt_override="", user_prompt_override=""):
        """
        生成推文和场景提示

        参数:
            persona: Character Card 数据
            api_key: LLM API key
            api_base: API base URL
            model: 模型名称
            calendar_plan: 运营日历计划（可选）
            context: 上下文信息（可选）
            is_batch_mode: 批量模式（True 时清空天气等实时信息）
            custom_topic: 自定义话题（覆盖 calendar_plan theme）
            temperature: 温度参数
            custom_user_prompt_template: 自定义用户提示词模板
            system_prompt_override: 直接覆盖系统提示词（优先级最高）
            user_prompt_override: 直接覆盖用户提示词（优先级最高）

        返回:
            (tweet, scene_hint, system_prompt, user_prompt) 推文、场景、系统提示词、用户提示词
        """
        # 如果没有 context，使用空字典
        context = context or {}

        # 如果是批量模式，清空实时上下文信息（天气等）
        if is_batch_mode:
            context = self._clean_realtime_context(context)

        # 如果有 calendar_plan，优先使用计划中的信息
        if calendar_plan:
            # custom_topic 优先级：用户输入 > calendar_plan.theme
            if not custom_topic:
                custom_topic = calendar_plan.get("theme", "")
            # 将 calendar_plan 信息添加到 context
            context["calendar_plan"] = calendar_plan

        # 构建 system prompt
        system_prompt = self._build_system_prompt(persona, context)

        # 构建 user prompt（统一使用一个方法）
        user_prompt = self._build_user_prompt(persona, context, custom_topic, calendar_plan, custom_user_prompt_template)

        # ⭐ 如果有 override，使用 override（优先级最高）
        if system_prompt_override.strip():
            system_prompt = system_prompt_override
        if user_prompt_override.strip():
            user_prompt = user_prompt_override

        # 提取 few-shot 示例
        examples = extract_few_shot_examples(persona, max_examples=2)

        # 组装消息
        messages = [{"role": "system", "content": system_prompt}]

        # 添加 few-shot
        for example in examples:
            messages.append({"role": "assistant", "content": example})

        messages.append({"role": "user", "content": user_prompt})

        # 调用 LLM
        try:
            llm = LLMClient(api_key, api_base, model)
            response = llm.generate(messages, temperature=temperature, max_tokens=400)

            # 解析 LLM 输出，提取推文和场景提示
            tweet, scene_hint = self._parse_response(response, calendar_plan)

            return (tweet, scene_hint, system_prompt, user_prompt)
        except Exception as e:
            raise RuntimeError(f"推文生成失败: {str(e)}")

    def _parse_response(self, response: str, calendar_plan=None) -> tuple:
        """
        解析 LLM 响应，提取推文和场景提示

        格式：
        TWEET: 推文内容...
        SCENE: gym, sporty outfit
        """
        tweet = ""
        scene_hint = ""

        lines = response.strip().split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if line.startswith('TWEET:'):
                current_section = 'tweet'
                tweet = line.replace('TWEET:', '').strip()
            elif line.startswith('SCENE:'):
                current_section = 'scene'
                scene_hint = line.replace('SCENE:', '').strip()
            elif current_section == 'tweet' and line:
                tweet += '\n' + line
            elif current_section == 'scene' and line:
                scene_hint += ' ' + line

        # 如果没有按格式输出，尝试简单分割
        if not tweet and not scene_hint:
            # 假设第一行是推文，最后一行是场景
            parts = response.strip().split('\n')
            if len(parts) >= 2:
                tweet = '\n'.join(parts[:-1]).strip()
                scene_hint = parts[-1].strip()
            else:
                tweet = response.strip()
                scene_hint = "casual, daily life"  # 默认场景

        # 如果场景提示为空，且有运营日历计划，使用计划中的建议场景
        if not scene_hint and calendar_plan:
            scene_hint = calendar_plan.get("suggested_scene", "casual, daily life")

        return tweet.strip(), scene_hint.strip()

    def _build_system_prompt(self, persona: dict, context: dict) -> str:
        """构建 system prompt"""
        data = persona["data"]
        name = data.get("name", "")

        # ===== 1. 今日背景信息（放在最前面）=====
        background_info = ""
        if context:
            date_info = context.get("date", {})
            weather_info = context.get("weather", {})

            bg_parts = []

            # 日期和星期
            if date_info.get('formatted'):
                bg_parts.append(f"今天是 {date_info['formatted']}")

            # 特殊日期（节假日/周末）
            special_info = date_info.get('special') or date_info.get('formatted_special')
            if special_info:
                bg_parts.append(f"特殊日期：{special_info}")

            # 天气
            if weather_info.get('formatted'):
                bg_parts.append(f"天气：{weather_info['formatted']}")

            if bg_parts:
                background_info = "【今日背景】\n" + "，".join(bg_parts) + "。\n\n"

        # ===== 2. 基础人设 =====
        base_system = data.get("system_prompt", "")

        # ===== 3. 推文风格指导 =====
        # 推文特定指导（支持新扁平结构和旧 extensions 结构）
        twitter_ext = data.get("twitter_persona") or data.get("extensions", {}).get("twitter_persona", {})
        tweet_prefs = twitter_ext.get("tweet_preferences", {})

        # ⭐ 检查人设中是否有自定义的推文风格指导
        custom_guidance = data.get("tweet_style_guide") or data.get("extensions", {}).get("tweet_style_guide", "")

        # 如果有自定义指导，使用自定义；否则使用默认
        if custom_guidance:
            style_guidance = custom_guidance
        else:
            # 默认指导（可根据人设标签自动调整）
            tags = data.get("tags", [])

            # 根据标签判断风格
            if any(tag in ["cute", "innocent", "girl-next-door", "traditional"] for tag in tags):
                # 清纯风格
                style_guidance = """
【推文风格要求】
- 清纯邻家女孩形象，温柔亲切
- 适度暧昧但不露骨，保持真诚感
- 多用互动性话题，引导粉丝评论
- 分享真实生活细节增加亲切感
- 避免过于商业化，保持自然
"""
            else:
                # 默认性感风格
                style_guidance = """
【推文风格要求】
- 适度性感暧昧，但不要太露骨
- 展示魅力，使用暗示性语言
- 多用互动性话题，引导粉丝评论
- 偶尔透露生活细节增加真实感
- 避免过于高冷，要有亲和力
"""

        # ===== 4. 推文技术要求 =====
        technical_info = ""
        if tweet_prefs:
            tech_parts = []
            if tweet_prefs.get('emoji_usage'):
                tech_parts.append(f"Emoji: {tweet_prefs.get('emoji_usage')}")
            if tweet_prefs.get('avg_tweet_length'):
                tech_parts.append(f"长度: {tweet_prefs.get('avg_tweet_length')}")
            if tweet_prefs.get('hashtag_style'):
                tech_parts.append(f"标签: {tweet_prefs.get('hashtag_style')}")

            if tech_parts:
                technical_info = "\n【技术要求】\n" + " | ".join(tech_parts) + "\n"

        # 组合
        system_prompt = f"""{background_info}{base_system}

{style_guidance}{technical_info}

【重要提醒】
- 结合今日背景（日期、天气、节假日）撰写内容
- 保持真实自然，像真人在发社交媒体
- 按照人设特点展示个人魅力，吸引目标粉丝
- 偶尔透露小情绪增加真实感
- 使用 {name} 的语气和个性
"""

        return system_prompt

    def _build_user_prompt(self, persona: dict, context: dict, custom_topic: str = "", calendar_plan=None, custom_template="") -> str:
        """构建 user prompt（统一方法，不依赖 topic_type）"""
        data = persona["data"]
        name = data.get("name", "")

        # 如果有运营日历计划，添加计划指导
        plan_guidance = ""
        if calendar_plan:
            keywords = calendar_plan.get("keywords", [])
            keywords_str = "、".join(keywords) if keywords else ""

            # 显示完整的运营计划信息（包括 topic_type 仅用于分类）
            topic_type_display = calendar_plan.get('topic_type', '')
            plan_guidance = f"""
今日运营计划："""
            if topic_type_display:
                plan_guidance += f"\n- 内容类型：{topic_type_display}"

            plan_guidance += f"""
- 主题：{calendar_plan.get('theme', '')}
- 内容方向：{calendar_plan.get('content_direction', '')}
- 关键词：{keywords_str}
- 建议场景：{calendar_plan.get('suggested_scene', '')}
"""
            # 如果有特殊活动，也要提及
            special_event = calendar_plan.get("special_event")
            if special_event:
                plan_guidance += f"- 特殊活动：{special_event}\n"

        # ⭐ 从人设文件提取 few-shot 示例
        few_shot_examples = self._extract_relevant_tweet_examples(persona, calendar_plan)

        examples_text = ""
        if few_shot_examples:
            examples_text = "\n参考以下人设推文示例的风格和语气（灵活改写，不要照抄）:\n"
            for i, example in enumerate(few_shot_examples, 1):
                examples_text += f"{i}. {example}\n"

        # 检索 character_book（使用 calendar_plan 的 keywords 和 custom_topic）
        search_terms = []
        if calendar_plan:
            search_terms.extend(calendar_plan.get("keywords", []))
            search_terms.append(calendar_plan.get("theme", ""))
        if custom_topic:
            search_terms.append(custom_topic)

        kb_entries = []
        for term in search_terms:
            if term:
                entries = search_character_book(persona, term)
                kb_entries.extend(entries)

        # 去重
        kb_entries = list(dict.fromkeys(kb_entries))[:3]  # 最多3条

        kb_info = ""
        if kb_entries:
            kb_info = "\n\n相关背景知识:\n" + "\n".join([f"- {entry}" for entry in kb_entries])

        # 如果有自定义模板，使用自定义模板
        if custom_template:
            user_prompt = custom_template.format(
                name=name,
                topic=custom_topic or calendar_plan.get('theme', ''),
                plan_guidance=plan_guidance,
                examples_text=examples_text,
                kb_info=kb_info
            )
        else:
            # 构建主题描述
            topic_desc = ""
            if custom_topic:
                topic_desc = f"关于「{custom_topic}」的推文"
            elif calendar_plan and calendar_plan.get('theme'):
                topic_desc = f"推文（主题：{calendar_plan.get('theme')}）"
            else:
                topic_desc = "推文"

            # 使用通用 prompt（适配所有风格）
            user_prompt = f"""请以 {name} 的身份撰写一条{topic_desc}，并描述配图场景。
{plan_guidance}
{examples_text}
{kb_info}

要求:
1. 结合当前天气和日期（如果上下文有提供）
2. 严格遵循今日运营计划的主题和内容方向
3. 保持人设的语言风格和性格特点
4. 引导粉丝互动（点赞/评论）
5. 使用合适的 emoji
6. 字数 60-150 字
7. 添加 1-3 个相关标签

输出格式（严格按照此格式）:
TWEET: [推文内容，包含 emoji 和标签]
SCENE: [场景描述，如: traditional courtyard, wearing hanfu, afternoon sunlight]

场景描述要求:
- 用英文描述，简洁明了
- 包含地点和氛围
- 包含服装/姿态（如果推文中提到）
- 与推文内容和人设完全匹配
"""

        return user_prompt

    def _extract_relevant_tweet_examples(self, persona: dict, calendar_plan=None, max_examples: int = 3) -> list:
        """
        从人设文件中提取相关的推文示例

        参数:
            persona: 人设数据
            calendar_plan: 日历计划（用于提取关键词匹配）
            max_examples: 最多返回的示例数

        返回:
            示例文本列表
        """
        data = persona["data"]
        examples = []

        # 1. 从 twitter_scenario.tweet_examples 提取
        twitter_scenario = data.get("twitter_scenario", {})
        tweet_examples = twitter_scenario.get("tweet_examples", [])

        if not tweet_examples:
            # 如果没有找到，尝试从 extensions 读取（向后兼容）
            extensions = data.get("extensions", {})
            twitter_persona = extensions.get("twitter_persona", {})
            tweet_examples = twitter_persona.get("tweet_examples", [])

        # 2. 根据相关性筛选示例
        relevant_examples = []

        # 提取关键词用于匹配
        search_keywords = set()
        if calendar_plan:
            search_keywords.update(calendar_plan.get("keywords", []))
            theme = calendar_plan.get("theme", "")
            if theme:
                search_keywords.update(theme.split())
            # 也使用 topic_type 作为搜索关键词
            topic_type = calendar_plan.get("topic_type", "")
            if topic_type:
                search_keywords.update(topic_type.split())

        for example in tweet_examples:
            example_type = example.get("type", "")
            example_text = example.get("text", "")
            example_context = example.get("context", "")

            # 计算相关性得分
            relevance_score = 0

            # 如果关键词匹配
            example_content = f"{example_type} {example_text} {example_context}".lower()
            for keyword in search_keywords:
                if keyword and keyword.lower() in example_content:
                    relevance_score += 2

            if relevance_score > 0:
                relevant_examples.append((relevance_score, example_text))

        # 3. 按相关性排序，取前 N 个
        relevant_examples.sort(key=lambda x: x[0], reverse=True)
        examples = [text for _, text in relevant_examples[:max_examples]]

        # 4. 如果没有找到相关示例，随机选择几个
        if not examples and tweet_examples:
            import random
            sample_size = min(max_examples, len(tweet_examples))
            sampled = random.sample(tweet_examples, sample_size)
            examples = [ex.get("text", "") for ex in sampled if ex.get("text")]

        return examples

    def _clean_realtime_context(self, context: dict) -> dict:
        """
        清空实时上下文信息（用于批量模式）

        参数:
            context: 原始上下文

        返回:
            清理后的上下文（移除天气等实时信息）
        """
        cleaned_context = context.copy()

        # 清空天气信息
        if "weather" in cleaned_context:
            cleaned_context["weather"] = {}

        # 保留日期信息中的 formatted，但清空 special 和 formatted_special
        if "date" in cleaned_context:
            date_info = cleaned_context["date"].copy()
            # 清空特殊日期信息（因为是提前生成的，不一定准确）
            date_info["special"] = None
            date_info["formatted_special"] = None
            cleaned_context["date"] = date_info

        return cleaned_context


# 节点注册
NODE_CLASS_MAPPINGS = {
    "TweetGenerator": TweetGenerator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TweetGenerator": "Generate Tweet"
}
