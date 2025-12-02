"""图像提示词生成节点"""


class ImagePromptBuilder:
    """图像提示词生成器（使用 LLM 生成的场景描述）"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "scene_hint": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "从 TweetGenerator 连接",
                    "forceInput": True  # 强制作为输入连接
                }),
                "persona": ("PERSONA",),  # 添加人设输入
            },
            "optional": {
                "prepend_prompt": ("STRING", {
                    "default": "masterpiece, best quality, 8k uhd, professional photography",
                    "multiline": True,
                    "placeholder": "前置提示词（放在场景描述之前，如：质量词、LoRA等）"
                }),
                "append_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "后置提示词（放在场景描述之后，如：人物特征、画面氛围等）"
                }),
                "auto_lora": ("BOOLEAN", {
                    "default": True
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("positive_prompt",)
    FUNCTION = "build"
    CATEGORY = "TwitterChat"
    DESCRIPTION = "Build image prompts from scene hints with auto LoRA extraction"

    def build(self, scene_hint, persona, prepend_prompt="masterpiece, best quality, 8k uhd, professional photography",
              append_prompt="", auto_lora=True):
        """
        构建图像提示词（使用 LLM 生成的场景描述）

        参数:
            scene_hint: 从 TweetGenerator 连接的场景提示
            persona: Character Card 数据
            prepend_prompt: 前置提示词（放在场景之前）
            append_prompt: 后置提示词（放在场景之后）
            auto_lora: 是否自动从人设提取 LoRA 触发词（会插入到最前面）

        返回:
            (positive_prompt,)
        """
        # 组装提示词（优先级顺序）
        positive_parts = []

        # 1. 自动 LoRA 触发词（如果开启，放在最前面）
        if auto_lora:
            lora_triggers = self._extract_lora_triggers(persona)
            if lora_triggers:
                positive_parts.append(lora_triggers)

        # 2. 前置提示词（质量词、手动LoRA等）
        if prepend_prompt:
            positive_parts.append(prepend_prompt)

        # 3. 场景描述（LLM 生成）
        if scene_hint:
            positive_parts.append(scene_hint)

        # 4. 后置提示词（人物特征、画面氛围等）
        if append_prompt:
            positive_parts.append(append_prompt)

        positive_prompt = ", ".join(filter(None, positive_parts))

        return (positive_prompt,)

    def _extract_lora_triggers(self, persona: dict) -> str:
        """
        从人设中提取 LoRA 触发词

        参数:
            persona: Character Card 数据

        返回:
            LoRA 触发词字符串，格式：trigger_word1, trigger_word2
        """
        data = persona.get("data", {})

        # 尝试从多个位置读取 lora 配置
        lora_config = data.get("lora") or data.get("extensions", {}).get("lora")

        if not lora_config:
            return ""

        # 提取触发词
        trigger_words = lora_config.get("trigger_words", [])

        if not trigger_words:
            return ""

        # 只返回触发词（不包含 LoRA 标签）
        if isinstance(trigger_words, list):
            return ", ".join(trigger_words)
        else:
            return str(trigger_words)


# 节点注册
NODE_CLASS_MAPPINGS = {
    "ImagePromptBuilder": ImagePromptBuilder
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImagePromptBuilder": "Build Image Prompt"
}
