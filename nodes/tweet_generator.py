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

        # ===== 2.5 视觉人格档案（新增：用于场景生成）=====
        visual_profile = self._build_visual_profile(data)

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
- 分享真实生活细节增加亲切感
- 避免过于商业化，保持自然
- 像聊天一样自然表达，不要刻意互动引导
"""
            else:
                # 默认性感风格
                style_guidance = """
【推文风格要求】
- 适度性感暧昧，但不要太露骨
- 展示魅力，使用暗示性语言
- 偶尔透露生活细节增加真实感
- 避免过于高冷，要有亲和力
- 像聊天一样自然表达，不要刻意互动引导
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

        # ===== 5. 输出格式规范 =====
        output_format = """
【输出格式规范】
输出必须严格按照以下格式：
TWEET: [推文内容，包含emoji和标签]
SCENE: [场景描述，用英文自然段落描述]
"""

        # ===== 6. 场景描述标准 =====
        # 根据人设标签动态调整场景指导
        tags = data.get("tags", [])

        # 基础场景描述标准
        scene_guidelines = """
【场景描述标准】
- **必须**：描述的是这个人物独自一人的场景，不要涉及其他人物
- **不要描述**：人物的外貌特征（发型、年龄、肤色、五官等由LoRA控制）
- **服装细节**：具体描述穿着的服饰、配饰、鞋子等
- **姿态动作**：站/坐/躺的具体姿势，手的位置，身体朝向，在做什么动作
- **场景环境**：具体的地点、空间布局
- **光线**：光源类型（阳光/室内灯光/烛光等）、光线效果、色调、阴影
- **氛围感**：整体情绪、氛围（peaceful/elegant/cozy/energetic等）
- **背景细节**：环境中的家具、装饰、植物、建筑等具体元素
- **镜头信息**：拍摄角度（front view/side view）、景别（close-up/medium shot/full body）、焦距效果（shallow depth of field等）

【关键：让图片更吸引人的要素】

⚠️ **避免呆滞和僵硬**：
- ❌ 表情：不要用"focused expression"、"calm expression"等平淡描述
- ❌ 姿态：不要用"hands folded"、"standing upright"等僵硬姿势
- ❌ 氛围：不要用"introspective"、"contemplative"等无聊氛围

✅ **打造生动吸引力的技巧**：

**1. 表情和眼神**（最重要！决定吸引力）
- 使用具体的表情描述，而不是抽象词汇
- 推荐描述：
  * 眼神：gazing with longing, eyes slightly narrowed with desire, half-lidded eyes, looking away shyly then glancing back, eyes glistening with emotion
  * 嘴唇：lips slightly parted, biting lower lip gently, subtle smile playing on lips, pouty lips
  * 脸颊：cheeks flushed with warmth, hint of pink on cheeks
- 根据情绪选择：期待→anticipation in eyes；羞涩→shy but inviting gaze；渴望→yearning expression

**2. 身体语言和姿态**（展示张力和美感）
- 避免僵硬对称的姿势
- 推荐姿态：
  * 触摸：fingers tracing [item], hand gently touching [body part/object], running fingers through...
  * 展示：leaning slightly to reveal..., body turned to show..., posture that accentuates...
  * 动态感：mid-motion of..., caught in the act of..., turning towards/away from...
- 根据性格选择：submissive→kneeling/lowered gaze；confident→chin up/direct gaze；playful→dynamic pose

**3. 服装选择**（匹配人设且有视觉冲击）
- 根据人设标签选择合适的服装风格
- 强调关键配饰或特征（如项圈、耳环、特殊服饰）
- 贴身或有层次感的服装比oversized更有吸引力
- 露出关键部位：锁骨、肩膀、腰线等增加视觉interest

**4. 光线和氛围**（营造情绪）
- 柔和光线比强光更有吸引力：soft lighting, warm glow, gentle illumination
- 色调匹配情绪：warm tones（温暖）、cool tones（冷艳）、dim lighting（私密）
- 阴影增加层次：subtle shadows, light and shadow interplay
"""

        # 根据人设标签添加特定场景指导
        if any(tag in ["bdsm", "submissive", "petplay", "masochist"] for tag in tags):
            scene_guidelines += """
【针对BDSM/Submissive人设的特殊指导】
- **核心特质视觉化**：展示submissive天性，但要有美感和诱惑力，不要显得被动无神
- **关键元素**：
  * 项圈/collar：必须prominently visible，是视觉焦点之一
  * 眼神：longing gaze, yearning expression, eyes showing devotion mixed with desire
  * 姿态：kneeling gracefully (NOT stiffly), leaning forward submissively, body language showing eagerness to please
  * 手部动作：fingers touching collar, hands clasped in pleading gesture, reaching out tentatively
- **氛围**：intimate, sultry, submissive yet alluring, private moment of devotion
- **服装建议**：fitted clothing that shows collar, off-shoulder to reveal collar, lingerie, or simple but form-fitting attire
- **避免**：过于"仪式化"的场景(如hands folded in prayer)、过于遮蔽的服装(oversized sweater)

示例场景：
"A woman kneeling gracefully on soft bedroom carpet. She wears a fitted black tank top that accentuates her collarbones and a delicate black leather collar with silver ring prominently visible around her neck, paired with simple fitted leggings. Her posture is submissive yet elegant—back slightly arched, one hand reaching up to trace the collar with fingertips while the other rests on her thigh. Her eyes are half-lidded with a mix of yearning and shy anticipation, lips slightly parted, a subtle flush on her cheeks. Dim purple-tinted LED lighting from behind casts a sultry glow and soft shadows across her figure, creating an intimate, private atmosphere. Background features a rumpled bed with scattered plushies, fairy lights creating a warm ambient glow. Close-up shot focusing on her face and collar, shallow depth of field, cinematic lighting with cool undertones, 8k quality."
"""
        elif any(tag in ["cute", "innocent", "girl-next-door"] for tag in tags):
            scene_guidelines += """
【针对清纯/可爱人设的特殊指导】
- **核心特质**：甜美、自然、清新，但要有生气和魅力
- **眼神**：bright and expressive eyes, playful glance, gentle smile reaching the eyes
- **姿态**：natural, relaxed poses, slight tilt of head, playful gestures
- **服装**：casual but flattering, soft colors, comfortable yet stylish
- **氛围**：warm, inviting, cheerful, natural sunlight preferred

示例场景：
"A woman sitting casually on a window sill bathed in soft morning sunlight. She wears a comfortable white oversized shirt with one shoulder slightly slipping down, and denim shorts. Her legs are tucked to one side, one hand holding a warm mug while the other plays with a strand of hair. Her expression is bright and playful—eyes sparkling with a gentle smile, a hint of mischief in her gaze. Natural golden sunlight streams through the window, illuminating her face and creating a warm, cheerful atmosphere. Background shows potted plants on the windowsill and sheer white curtains gently swaying. Medium shot from a slight low angle, shallow depth of field, natural lighting, 8k quality."
"""
        else:
            # 默认通用指导
            scene_guidelines += """
示例场景：
"A woman in a cozy home setting. She wears stylish casual attire that flatters her figure. Her expression is engaging and full of personality—eyes showing genuine emotion, a natural smile or intriguing gaze. Her posture is relaxed yet confident, with natural body language that tells a story. Soft lighting creates a welcoming atmosphere, with carefully chosen details in the background that add context without distraction. The overall mood is inviting and captures a genuine moment. Medium shot with shallow depth of field, professional lighting, 8k quality."
"""

        scene_guidelines += """

用这种详细但流畅的自然语言描述，不要用逗号分隔的标签列表。重点描述场景、服装、动作和光线，人物外貌由LoRA控制。

【最终检查清单】
生成场景描述前，确保：
✅ 表情具体生动（不要用"calm"、"peaceful"等平淡词）
✅ 姿态自然有张力（不要僵硬对称）
✅ 眼神有情绪（longing/playful/yearning等）
✅ 服装展示特点（贴身或有层次感）
✅ 光线营造氛围（soft/warm/dim等）
✅ 整体有吸引力和故事感
"""

        # 组合
        system_prompt = f"""{background_info}{base_system}
{visual_profile}
{style_guidance}{technical_info}{output_format}{scene_guidelines}

【真实感核心原则 - 最重要！】
这是真人随手发的推文，不是AI精心编写的文案！

⚠️ **严禁使用的AI特征**：
1. **列表式排版** - ❌ 不要用 "1. 2. 3." 或 "• • •" 列举
   - 真人不会这么工整地列出来
   - 如果要列举，用自然的方式："xxx，然后xxx，还有xxx"

2. **营销式互动话术** - ❌ 严禁以下表达：
   - "你们觉得呢？" / "评论告诉我~" / "有人也是这样吗？"
   - "分享给我看~" / "来聊聊吧" / "双击点赞"
   - 任何刻意引导互动的话术

3. **工整结构化** - ❌ 避免：
   - 每句话长度相似
   - 标点符号使用规律
   - emoji固定在句尾
   - 段落结构对称

4. **文学化描述** - ❌ 避免：
   - "每一下都让心更坚定"（太文艺）
   - "灵魂深处的渴望"（太夸张）
   - "宛如...一般"（太书面）

5. **过度自我分析** - ❌ 真人不会：
   - 详细剖析自己的心理状态
   - 用心理学术语描述感受
   - 完整归纳总结观点

✅ **真实感表达技巧**（根据{name}的人设灵活运用）：

**句式要随意，不要工整**：
- ✅ "早上又在练习了...\n\n跪着的时候一直在想\n\n如果有主人在就好了"
- ✅ "今天有点想调皮\n\n但是没有主人惩罚我\n\n算了...还是乖乖的吧"
- ❌ "今天练习了服从姿势。感受到了内心的平静。期待主人的到来。"（太规整）

**情绪要具体，不要抽象**：
- ✅ "跪得膝盖疼但是心里暖暖的"
- ✅ "看到项圈就想戴上...好想被拥有啊"
- ❌ "内心充满了对服从的渴望和对主人的崇拜"（太抽象）

**表达要口语，不要书面**：
- ✅ "emmm不知道怎么说"
- ✅ "有点...就是那种..."
- ❌ "综上所述" / "由此可见"（太书面）

**如果要表达类似内容，这样改**：
原AI味："每天镜子前默念三次：1. xxx 2. xxx 3. xxx"
改真实感："最近每天都会对着镜子念几句话给自己听...'我想要服从'什么的...有点羞耻但是感觉好安心"

【重要提醒】
- **背景意识**：了解当前日期、天气、节假日，确保内容不违和，但不要刻意在推文中提及（真人不会每条都说"今天XX"）
- **真实自然**：像真人在手机上随手发推，不是精心编写的营销文案
- **人设魅力**：通过真实的情绪和表达展示个性，不是刻意"吸引粉丝"
- **情绪真实**：偶尔透露真实的小情绪、小烦恼、小开心，增加共鸣感
- **语气一致**：始终使用 {name} 的语气和个性
- **杜绝营销**：绝对不要用任何引导互动的话术，只表达自己
"""

        return system_prompt

    def _build_user_prompt(self, persona: dict, context: dict, custom_topic: str = "", calendar_plan=None, custom_template="") -> str:
        """构建 user prompt（统一方法，不依赖 topic_type）"""
        data = persona["data"]
        name = data.get("name", "")

        # 如果有运营日历计划，添加计划指导
        plan_guidance = ""
        # ⭐ 提取新增字段用于后续提示词
        recommended_time = ""
        mood = ""
        strategic_flaw = None

        if calendar_plan:
            keywords = calendar_plan.get("keywords", [])
            keywords_str = "、".join(keywords) if keywords else ""

            # ⭐ 提取新增字段
            recommended_time = calendar_plan.get('recommended_time', '')
            mood = calendar_plan.get('mood', '')
            strategic_flaw = calendar_plan.get('strategic_flaw')

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
            # ⭐ 添加推荐时间段和情绪（如果有）
            if recommended_time:
                plan_guidance += f"- 推荐时间段：{recommended_time}\n"
            if mood:
                plan_guidance += f"- 建议情绪基调：{mood}\n"
            if strategic_flaw:
                plan_guidance += f"- 今日战略性缺陷：{strategic_flaw}\n"

            # 如果有特殊活动，也要提及
            special_event = calendar_plan.get("special_event")
            if special_event:
                plan_guidance += f"- 特殊活动：{special_event}\n"

        # ⭐ 从人设文件提取 few-shot 示例
        few_shot_examples, scene_examples = self._extract_relevant_tweet_examples(persona, calendar_plan)

        examples_text = ""
        if few_shot_examples:
            examples_text = "\n参考以下人设推文示例的风格和语气（灵活改写，不要照抄）:\n"
            for i, example in enumerate(few_shot_examples, 1):
                examples_text += f"{i}. {example}\n"

        # 添加场景示例（如果有）
        scene_examples_text = ""
        if scene_examples:
            scene_examples_text = "\n【参考场景示例】（符合人设的场景风格）:\n"
            for i, scene in enumerate(scene_examples, 1):
                scene_examples_text += f"{i}. {scene}\n"

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
                scene_examples_text=scene_examples_text,
                kb_info=kb_info
            )
        else:
            # 构建主题描述
            topic_desc = ""
            if custom_topic:
                topic_desc = f"关于「{custom_topic}」的推文"
            elif calendar_plan and calendar_plan.get('theme'):
                topic_desc = f"关于「{calendar_plan.get('theme')}」的推文"
            else:
                topic_desc = "推文"

            # 使用简化的 user prompt（通用规则已在系统提示词中）
            user_prompt = f"""请以 {name} 的身份撰写一条{topic_desc}。
{plan_guidance}
{examples_text}
{scene_examples_text}
{kb_info}

【核心要求】
1. 结合当前背景但不要刻意提及
2. 严格遵循今日运营计划的主题和内容方向
3. 保持人设的语言风格和性格特点
4. 像真人一样自然表达，绝对不要刻意引导互动
5. 使用合适的 emoji 和标签（1-3个）
6. 字数控制在 60-150 字

【特别强调 - 针对本次任务】
❌ 严禁使用列表式排版（"1. 2. 3." 或 "• • •"）
❌ 严禁使用营销式互动话术（"你们觉得呢？"/"分享给我看~"等）
❌ 严禁工整对称的结构（真人推文是随意的）
❌ 严禁文学化表达（"心灵"/"灵魂"/"宛如"等）

✅ 用自然口语表达：就像在跟朋友聊天一样
✅ 情绪要具体：不要抽象描述，说真实感受
✅ 句式要随意：不要每句都工整
✅ 如果要列举：用"然后"/"还有"等自然衔接，不要编号
"""

        return user_prompt

    def _extract_relevant_tweet_examples(self, persona: dict, calendar_plan=None, max_examples: int = 3) -> tuple:
        """
        从人设文件中提取相关的推文示例和场景示例

        参数:
            persona: 人设数据
            calendar_plan: 日历计划（用于提取关键词匹配）
            max_examples: 最多返回的示例数

        返回:
            (tweet_examples, scene_examples) 推文文本列表和场景描述列表
        """
        data = persona["data"]
        tweet_examples = []
        scene_examples = []

        # 1. 从 twitter_scenario.tweet_examples 提取
        twitter_scenario = data.get("twitter_scenario", {})
        tweet_examples_raw = twitter_scenario.get("tweet_examples", [])

        if not tweet_examples_raw:
            # 如果没有找到，尝试从 extensions 读取（向后兼容）
            extensions = data.get("extensions", {})
            twitter_persona = extensions.get("twitter_persona", {})
            tweet_examples_raw = twitter_persona.get("tweet_examples", [])

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

        for example in tweet_examples_raw:
            example_type = example.get("type", "")
            example_text = example.get("text", "")
            example_context = example.get("context", "")
            example_scene = example.get("scene_hint", "")

            # 计算相关性得分
            relevance_score = 0

            # 如果关键词匹配
            example_content = f"{example_type} {example_text} {example_context}".lower()
            for keyword in search_keywords:
                if keyword and keyword.lower() in example_content:
                    relevance_score += 2

            if relevance_score > 0:
                relevant_examples.append((relevance_score, example_text, example_scene))

        # 3. 按相关性排序，取前 N 个
        relevant_examples.sort(key=lambda x: x[0], reverse=True)
        tweet_examples = [text for _, text, _ in relevant_examples[:max_examples] if text]
        scene_examples = [scene for _, _, scene in relevant_examples[:max_examples] if scene]

        # 4. 如果没有找到相关示例，随机选择几个
        if not tweet_examples and tweet_examples_raw:
            import random
            sample_size = min(max_examples, len(tweet_examples_raw))
            sampled = random.sample(tweet_examples_raw, sample_size)
            tweet_examples = [ex.get("text", "") for ex in sampled if ex.get("text")]
            scene_examples = [ex.get("scene_hint", "") for ex in sampled if ex.get("scene_hint")]

        return tweet_examples, scene_examples

    def _build_visual_profile(self, data: dict) -> str:
        """
        构建视觉人格档案（用于场景生成）

        从人设的lifestyle_details.favorite_things等字段提取视觉偏好信息

        参数:
            data: Character Card data字段

        返回:
            视觉人格档案文本
        """
        visual_parts = []

        # 从 lifestyle_details.favorite_things 提取
        lifestyle_details = data.get("lifestyle_details", {})
        favorite_things = lifestyle_details.get("favorite_things", {})

        if favorite_things:
            visual_parts.append("【视觉人格档案】（生成场景时参考）")

            # 服装偏好
            clothing = favorite_things.get("clothing", "")
            if clothing:
                visual_parts.append(f"- 常穿服装：{clothing}")

            # BDSM道具
            bdsm_items = favorite_things.get("bdsm_items", "")
            if bdsm_items:
                visual_parts.append(f"- 常用道具：{bdsm_items}")

            # Petplay道具
            petplay_items = favorite_things.get("petplay_items", "")
            if petplay_items:
                visual_parts.append(f"- Petplay元素：{petplay_items}")

            # 配色偏好
            colors = favorite_things.get("colors", "")
            if colors:
                visual_parts.append(f"- 配色偏好：{colors}")

            # 痛觉偏好（可能影响场景中的痕迹展示）
            pain_preference = favorite_things.get("pain_preference", "")
            if pain_preference:
                visual_parts.append(f"- 可能出现的痕迹：{pain_preference}的痕迹")

        # 从 extensions.visual_preferences 提取（兼容旧格式）
        extensions = data.get("extensions", {})
        visual_prefs = extensions.get("visual_preferences", {})
        if visual_prefs and not visual_parts:
            # 如果没有从新格式提取到，尝试旧格式
            visual_parts.append("【视觉人格档案】")
            for key, value in visual_prefs.items():
                if value:
                    visual_parts.append(f"- {key}: {value}")

        if visual_parts:
            return "\n" + "\n".join(visual_parts) + "\n"
        else:
            return ""

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
