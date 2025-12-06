"""从人设自动加载 LoRA 节点"""
import comfy.sd
import comfy.utils
import folder_paths


class LoraLoaderFromPersona:
    """从人设中自动加载 LoRA 模型"""

    def __init__(self):
        self.loaded_lora = None

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL", {
                    "tooltip": "The diffusion model the LoRA will be applied to."
                }),
                "clip": ("CLIP", {
                    "tooltip": "The CLIP model the LoRA will be applied to."
                }),
                "persona": ("PERSONA", {
                    "tooltip": "Persona data containing LoRA configuration"
                }),
            },
            "optional": {
                "strength_model": ("FLOAT", {
                    "default": 1.0,
                    "min": -100.0,
                    "max": 100.0,
                    "step": 0.01,
                    "tooltip": "How strongly to modify the diffusion model (uses persona recommended_weight if not specified)"
                }),
                "strength_clip": ("FLOAT", {
                    "default": 1.0,
                    "min": -100.0,
                    "max": 100.0,
                    "step": 0.01,
                    "tooltip": "How strongly to modify the CLIP model"
                }),
                "lora_name_override": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Override LoRA model name (leave empty to use persona config)"
                }),
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP", "STRING")
    RETURN_NAMES = ("model", "clip", "lora_info")
    FUNCTION = "load_lora_from_persona"
    CATEGORY = "TwitterChat"
    DESCRIPTION = "Load LoRA model automatically from persona configuration"

    def load_lora_from_persona(self, model, clip, persona, strength_model=1.0, strength_clip=1.0, lora_name_override=""):
        """
        从人设中加载 LoRA 模型

        参数:
            model: Diffusion model
            clip: CLIP model
            persona: Character Card 数据
            strength_model: 模型强度（默认使用人设中的 recommended_weight）
            strength_clip: CLIP 强度
            lora_name_override: 手动覆盖 LoRA 名称

        返回:
            (model, clip, lora_info) 修改后的模型、CLIP、LoRA 信息
        """
        # 提取 LoRA 配置
        lora_config = self._extract_lora_config(persona)

        if not lora_config:
            # 如果没有 LoRA 配置，直接返回原模型
            return (model, clip, "No LoRA config found in persona")

        # 获取 LoRA 名称（优先使用 override）
        if lora_name_override.strip():
            lora_name = lora_name_override.strip()
        else:
            # 支持 model_name 和 model_path 两种字段名
            lora_name = lora_config.get("model_name") or lora_config.get("model_path", "")

        if not lora_name:
            return (model, clip, "No LoRA model name specified")

        # 使用人设中的推荐权重（如果 strength_model 是默认值 1.0）
        # 支持 recommended_weight 和 strength 两种字段名
        if strength_model == 1.0:
            strength_model = lora_config.get("recommended_weight") or lora_config.get("strength", 1.0)

        # 检查 LoRA 文件是否存在
        try:
            lora_path = folder_paths.get_full_path_or_raise("loras", lora_name)
        except Exception as e:
            error_msg = f"LoRA file not found: {lora_name}"
            print(f"[LoraLoaderFromPersona] {error_msg}")
            print(f"[LoraLoaderFromPersona] Available LoRAs: {folder_paths.get_filename_list('loras')[:10]}")
            return (model, clip, error_msg)

        # 如果强度为 0，直接返回
        if strength_model == 0 and strength_clip == 0:
            return (model, clip, f"LoRA skipped (strength=0): {lora_name}")

        # 加载 LoRA（使用缓存机制）
        lora = None
        if self.loaded_lora is not None:
            if self.loaded_lora[0] == lora_path:
                lora = self.loaded_lora[1]
            else:
                self.loaded_lora = None

        if lora is None:
            try:
                lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
                self.loaded_lora = (lora_path, lora)
            except Exception as e:
                error_msg = f"Failed to load LoRA: {str(e)}"
                print(f"[LoraLoaderFromPersona] {error_msg}")
                return (model, clip, error_msg)

        # 应用 LoRA 到模型
        try:
            model_lora, clip_lora = comfy.sd.load_lora_for_models(
                model, clip, lora, strength_model, strength_clip
            )

            # 构建信息字符串
            trigger_words = lora_config.get("trigger_words", [])
            trigger_str = ", ".join(trigger_words) if isinstance(trigger_words, list) else str(trigger_words)
            lora_info = f"✓ Loaded: {lora_name} (strength: {strength_model:.2f})\nTriggers: {trigger_str}"

            return (model_lora, clip_lora, lora_info)
        except Exception as e:
            error_msg = f"Failed to apply LoRA: {str(e)}"
            print(f"[LoraLoaderFromPersona] {error_msg}")
            return (model, clip, error_msg)

    def _extract_lora_config(self, persona: dict) -> dict:
        """
        从人设中提取 LoRA 配置

        参数:
            persona: Character Card 数据

        返回:
            LoRA 配置字典
        """
        data = persona.get("data", {})

        # 尝试从多个位置读取 lora 配置
        lora_config = data.get("lora") or data.get("extensions", {}).get("lora")

        return lora_config or {}


# 节点注册
NODE_CLASS_MAPPINGS = {
    "LoraLoaderFromPersona": LoraLoaderFromPersona
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoraLoaderFromPersona": "Load LoRA from Persona"
}
