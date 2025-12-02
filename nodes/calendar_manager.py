"""运营日历管理节点"""
from datetime import datetime
# 使用相对导入
from ..utils.llm_client import LLMClient
from ..utils.calendar_manager import CalendarManager as CalendarManagerUtil


class CalendarManager:
    """运营日历管理节点"""

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
                "days_to_generate": ("INT", {
                    "default": 15,
                    "min": 1,
                    "max": 31,
                    "step": 1
                }),
                "day_offset": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 30,
                    "step": 1,
                    "display": "number"
                }),
                "max_tokens": ("INT", {
                    "default": 10000,
                    "min": 1000,
                    "max": 32000,
                    "step": 100
                }),
                "force_regenerate": ("BOOLEAN", {
                    "default": False
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.05
                }),
                "calendar_prompt_override": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "⭐ 直接编辑日历生成提示词（留空则自动生成）"
                }),
            }
        }

    RETURN_TYPES = ("CALENDAR_PLAN", "STRING", "STRING", "STRING", "BOOLEAN")
    RETURN_NAMES = ("today_plan", "calendar_status", "full_calendar", "calendar_prompt", "is_batch_mode")
    FUNCTION = "manage_calendar"
    CATEGORY = "TwitterChat"
    DESCRIPTION = "Manage content calendar for persona (default: 15 days, use day_offset for batch generation)"

    def manage_calendar(self, persona, api_key, api_base, model,
                        days_to_generate=15, day_offset=0, max_tokens=10000, force_regenerate=False, temperature=0.7, calendar_prompt_override=""):
        """
        管理运营日历

        参数:
            persona: Character Card 数据
            api_key: LLM API key
            api_base: API base URL
            model: 模型名称
            days_to_generate: 生成日历的天数（默认15天，最多31天）
            day_offset: 天数偏移（0=今天，1=明天，2=后天...用于批量生成模式）
            max_tokens: 生成日历的最大token数（默认10000）
            force_regenerate: 强制重新生成
            temperature: 温度参数
            calendar_prompt_override: 直接覆盖日历生成提示词

        返回:
            (today_plan, calendar_status, full_calendar, calendar_prompt, is_batch_mode)
        """
        import json
        from datetime import datetime, timedelta

        # 初始化日历管理器
        cal_manager = CalendarManagerUtil()

        # 获取人设名称
        persona_name = persona["data"].get("name", "Unknown")

        # 计算目标日期（今天 + day_offset）
        target_date = datetime.now() + timedelta(days=day_offset)
        target_date_str = target_date.strftime("%Y-%m-%d")
        year_month = target_date_str[:7]  # YYYY-MM

        # 判断是否为批量模式
        is_batch_mode = (day_offset > 0)

        # 用于保存生成的 prompt
        calendar_prompt = ""

        # 检查是否需要生成日历
        need_generate = force_regenerate or not cal_manager.calendar_exists(persona_name, year_month)

        if need_generate:
            # 生成新日历
            status, calendar_prompt = self._generate_calendar(
                cal_manager, persona, persona_name, year_month,
                api_key, api_base, model, temperature, days_to_generate, max_tokens, calendar_prompt_override
            )
        else:
            status = f"✓ 使用已有日历: {year_month}"
            calendar_prompt = "(使用已有日历，未生成新提示词)"

        # 获取目标日期的计划
        target_plan = cal_manager.get_today_plan(persona_name, target_date_str)

        if target_plan is None:
            # 如果没有目标日期的计划（可能是跨月），尝试生成
            if not need_generate:
                status, calendar_prompt = self._generate_calendar(
                    cal_manager, persona, persona_name, year_month,
                    api_key, api_base, model, temperature, days_to_generate, max_tokens, calendar_prompt_override
                )
                target_plan = cal_manager.get_today_plan(persona_name, target_date_str)

            if target_plan is None:
                raise RuntimeError(f"无法获取 {target_date_str} 的运营计划")

        # 添加日期信息
        target_plan["date"] = target_date_str

        # 如果是批量模式，添加批量模式标记
        if is_batch_mode:
            status = f"✓ 批量模式 (day_offset={day_offset}): {target_date_str}"

        # 读取完整的月度日历
        full_calendar_data = cal_manager.load_calendar(persona_name, year_month)
        if full_calendar_data:
            # 格式化为可读的 JSON 字符串
            full_calendar = json.dumps(full_calendar_data, indent=2, ensure_ascii=False)
        else:
            full_calendar = json.dumps({"error": "无法读取完整日历"}, ensure_ascii=False)

        return (target_plan, status, full_calendar, calendar_prompt, is_batch_mode)

    def _generate_calendar(self, cal_manager, persona, persona_name, year_month,
                           api_key, api_base, model, temperature, days_to_generate, max_tokens, calendar_prompt_override=""):
        """
        生成日历

        参数:
            days_to_generate: 生成天数
            max_tokens: 最大token数
            calendar_prompt_override: 直接覆盖提示词

        返回:
            (状态信息, 使用的提示词)
        """
        try:
            # 构建 prompt
            prompt = cal_manager.generate_calendar_prompt(persona, year_month, days_to_generate)

            # ⭐ 如果有 override，使用 override（优先级最高）
            if calendar_prompt_override.strip():
                prompt = calendar_prompt_override

            # 调用 LLM
            llm = LLMClient(api_key, api_base, model)

            messages = [
                {
                    "role": "system",
                    "content": "你是专业的社交媒体运营专家，擅长规划内容日历。\n\n重要要求：\n1. 必须输出有效的 JSON 格式\n2. 所有字符串必须使用英文双引号 \"，不能使用中文引号 " "\n3. 所有字段必须完整，不能遗漏\n4. 输出必须是完整的 JSON 对象，不能截断\n5. 不要在 JSON 前后添加任何说明文字，直接输出 JSON"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            response = llm.generate(messages, temperature=temperature, max_tokens=max_tokens)

            # 解析并保存日历
            calendar_data = cal_manager.parse_calendar_response(response, persona_name, year_month)

            if cal_manager.save_calendar(persona_name, year_month, calendar_data):
                days_count = len(calendar_data["calendar"])
                return (f"✓ 成功生成 {year_month} 日历 ({days_count} 天)", prompt)
            else:
                raise RuntimeError("保存日历失败")

        except Exception as e:
            raise RuntimeError(f"生成日历失败: {str(e)}")


# 节点注册
NODE_CLASS_MAPPINGS = {
    "CalendarManager": CalendarManager
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CalendarManager": "Manage Content Calendar"
}
