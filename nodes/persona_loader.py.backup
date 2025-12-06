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
                    "tooltip": "选择输入模式：file=从文件加载，json_string=直接在下方输入JSON"
                }),
                "persona_file": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "path/to/persona.json (仅在file模式下使用)"
                }),
                "persona_json": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "完整的Persona JSON字符串 (仅在json_string模式下使用)\n\n在这里直接粘贴JSON内容，无需Text Multiline节点",
                    "dynamicPrompts": False  # 禁用动态提示符处理
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

                # 预处理：去除常见的格式问题
                persona_json_cleaned = persona_json.lstrip('\ufeff').strip()  # 去除BOM和空白

                if not persona_json_cleaned:
                    raise ValueError("清理后的 JSON 字符串为空")

                # 解析JSON字符串
                try:
                    persona = json.loads(persona_json_cleaned)
                    print(f"[PersonaLoader] 从JSON字符串加载人设 (user_id={user_id}, {len(persona_json_cleaned)} 字符)")

                except json.JSONDecodeError as e:
                    # 提供详细的错误信息帮助调试
                    error_pos = e.pos if hasattr(e, 'pos') else 0
                    context_start = max(0, error_pos - 100)
                    context_end = min(len(persona_json_cleaned), error_pos + 100)
                    error_context = persona_json_cleaned[context_start:context_end]

                    error_msg = (
                        f"JSON解析失败: {str(e)}\n"
                        f"错误位置: line {e.lineno}, column {e.colno} (position {error_pos})\n"
                        f"错误附近内容: ...{repr(error_context)}...\n\n"
                        f"提示:\n"
                        f"- 检查JSON格式是否正确（使用在线JSON验证工具）\n"
                        f"- 确保开头是 '{{' 结尾是 '}}'\n"
                        f"- 检查引号、逗号、括号是否匹配\n"
                        f"- 原始输入长度: {len(persona_json)} 字符，清理后: {len(persona_json_cleaned)} 字符"
                    )
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
