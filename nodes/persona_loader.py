"""人设加载节点"""
# 使用相对导入
from ..utils.persona_utils import (
    load_persona_from_json,
    generate_persona_summary
)
import os


class PersonaLoader:
    """人设加载器"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "persona_file": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "path/to/persona.json"
                }),
            }
        }

    RETURN_TYPES = ("PERSONA", "STRING", "STRING")
    RETURN_NAMES = ("persona", "summary", "system_prompt")
    FUNCTION = "load"
    CATEGORY = "TwitterChat"
    DESCRIPTION = "Load persona from JSON file"

    def load(self, persona_file):
        """
        加载人设 Character Card

        参数:
            persona_file: JSON 文件路径

        返回:
            (persona, summary, system_prompt)
        """
        try:
            if persona_file and os.path.exists(persona_file):
                persona = load_persona_from_json(persona_file)
            else:
                raise ValueError("请提供有效的 persona_file 路径")

            # 生成摘要
            summary = generate_persona_summary(persona)

            # 提取系统提示词
            system_prompt = persona["data"].get("system_prompt", "")

            return (persona, summary, system_prompt)

        except Exception as e:
            raise RuntimeError(f"加载人设失败: {str(e)}")


# 节点注册
NODE_CLASS_MAPPINGS = {
    "PersonaLoader": PersonaLoader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PersonaLoader": "Load Persona"
}
