"""运营日历管理工具"""
import os
import json
from datetime import datetime
from typing import Dict, Optional


class CalendarManager:
    """运营日历管理器"""

    def __init__(self, calendar_dir: str = "calendars"):
        """
        初始化日历管理器

        Args:
            calendar_dir: 日历文件存储目录
        """
        self.calendar_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            calendar_dir
        )

        # 确保目录存在
        os.makedirs(self.calendar_dir, exist_ok=True)

    def get_calendar_path(self, persona_name: str, year_month: str) -> str:
        """
        获取日历文件路径

        Args:
            persona_name: 人设名称
            year_month: 年月，格式 YYYY-MM

        Returns:
            日历文件路径
        """
        filename = f"{persona_name}_{year_month}.json"
        return os.path.join(self.calendar_dir, filename)

    def calendar_exists(self, persona_name: str, year_month: str) -> bool:
        """
        检查日历文件是否存在

        Args:
            persona_name: 人设名称
            year_month: 年月，格式 YYYY-MM

        Returns:
            是否存在
        """
        path = self.get_calendar_path(persona_name, year_month)
        return os.path.exists(path)

    def load_calendar(self, persona_name: str, year_month: str) -> Optional[Dict]:
        """
        加载日历文件

        Args:
            persona_name: 人设名称
            year_month: 年月，格式 YYYY-MM

        Returns:
            日历数据，如果不存在返回 None
        """
        path = self.get_calendar_path(persona_name, year_month)

        if not os.path.exists(path):
            return None

        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载日历失败: {e}")
            return None

    def save_calendar(self, persona_name: str, year_month: str, calendar_data: Dict) -> bool:
        """
        保存日历文件

        Args:
            persona_name: 人设名称
            year_month: 年月，格式 YYYY-MM
            calendar_data: 日历数据

        Returns:
            是否保存成功
        """
        path = self.get_calendar_path(persona_name, year_month)

        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(calendar_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存日历失败: {e}")
            return False

    def get_today_plan(self, persona_name: str, date: Optional[str] = None) -> Optional[Dict]:
        """
        获取指定日期的运营计划

        Args:
            persona_name: 人设名称
            date: 日期，格式 YYYY-MM-DD，默认为今天

        Returns:
            当日运营计划，如果不存在返回 None
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        year_month = date[:7]  # YYYY-MM

        calendar = self.load_calendar(persona_name, year_month)
        if calendar is None:
            return None

        return calendar.get("calendar", {}).get(date)

    def generate_calendar_prompt(self, persona: Dict, year_month: str, days_to_generate: int = 15) -> str:
        """
        生成日历生成的 LLM prompt

        Args:
            persona: 人设数据
            year_month: 年月，格式 YYYY-MM
            days_to_generate: 要生成的天数，默认15天

        Returns:
            LLM prompt
        """
        data = persona["data"]
        name = data.get("name", "Unknown")

        # 提取人设信息
        description = data.get("description", "")
        personality = data.get("personality", "")

        # 获取月份和天数
        year, month = year_month.split("-")

        # 计算当月天数
        import calendar
        _, days_in_month = calendar.monthrange(int(year), int(month))

        # 限制生成天数不超过当月实际天数
        actual_days = min(days_to_generate, days_in_month)

        # ⭐ 根据人设的国家代码获取节假日（问题4修复）
        import holidays

        # 从人设中读取国家代码
        core_info = data.get("core_info") or data.get("extensions", {}).get("core_info", {})
        location = core_info.get("location", {})
        country_code = location.get("country_code", "US")

        # 使用对应国家的节假日
        try:
            country_holidays = holidays.country_holidays(country_code, years=int(year))
        except Exception:
            # 如果国家代码无效，fallback 到 US
            country_holidays = holidays.country_holidays("US", years=int(year))

        month_holidays = []
        for i in range(1, actual_days + 1):
            date = f"{year_month}-{i:02d}"
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            if date_obj in country_holidays:
                holiday_name = country_holidays.get(date_obj)
                month_holidays.append(f"{date}: {holiday_name}")

        holidays_info = "\n".join(month_holidays) if month_holidays else "无特殊节日"

        # 格式化年月显示（2025-12 → 2025 年 12 月）
        year_month_display = f"{year} 年 {month} 月"

        prompt = f"""你是一位专业的社交媒体运营专家，为 {name} 规划 {year_month_display} 的推文运营日历。

人设信息：
- 名称：{name}
- 描述：{description}
- 性格：{personality}

运营目标：
- 内容多样化但符合人设
- 保持真实感和一致性
- 引导粉丝互动

本月特殊日期（前 {actual_days} 天）：
{holidays_info}

要求：
1. 规划 {year_month}-01 到 {year_month}-{actual_days:02d} 共 {actual_days} 天的内容
2. 根据人设特点设计一周节奏（周一到周日的内容类型）
3. 特殊日期要有特殊主题（节日、纪念日）
4. 内容类型要多样化，避免连续3天相同类型
5. topic_type 要符合人设特点（不要使用通用类型，要具体化）
6. suggested_scene 用英文描述，简洁明了

输出格式（严格 JSON，不要有其他说明文字）：
{{
  "{year_month}-01": {{
    "weekday": "Monday",
    "topic_type": "根据人设定义的内容类型（如：采茶日常/传统文化/健身打卡/日常分享等）",
    "theme": "具体的推文主题",
    "content_direction": "内容方向和要点",
    "keywords": ["关键词1", "关键词2", "关键词3"],
    "suggested_scene": "场景描述（英文）",
    "special_event": null
  }},
  "{year_month}-{actual_days:02d}": {{
    "weekday": "...",
    "topic_type": "...",
    "theme": "...",
    "content_direction": "...",
    "keywords": [...],
    "suggested_scene": "...",
    "special_event": null
  }}
}}

重要提示：
- topic_type 应该根据人设特点自定义，不要使用固定模板
- 内容类型要符合角色的职业、兴趣、生活方式
- 保持风格一致性，符合人设的语言习惯和行为特点

请直接输出 JSON，不要包含任何 ```json 标记或其他说明。
"""

        return prompt

    def parse_calendar_response(self, response: str, persona_name: str, year_month: str) -> Dict:
        """
        解析 LLM 返回的日历数据

        Args:
            response: LLM 响应
            persona_name: 人设名称
            year_month: 年月

        Returns:
            完整的日历数据结构
        """
        # 清理可能的 markdown 标记
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()

        # 尝试修复常见的 JSON 格式问题
        # 1. 替换中文引号为英文引号
        response = response.replace('"', '"').replace('"', '"')
        response = response.replace(''', "'").replace(''', "'")

        # 2. 如果 JSON 不完整（被截断），尝试补全
        if not response.endswith("}"):
            # 找到最后一个完整的日期条目
            lines = response.split('\n')
            # 从后往前找，直到找到一个完整的 }
            for i in range(len(lines) - 1, -1, -1):
                if '}' in lines[i]:
                    # 截取到这里
                    response = '\n'.join(lines[:i+1])
                    # 添加闭合括号
                    if not response.strip().endswith("}"):
                        response += "\n}"
                    break

        # 解析 JSON
        try:
            calendar_dict = json.loads(response)
        except json.JSONDecodeError as e:
            # 显示更多错误信息
            error_line = e.lineno if hasattr(e, 'lineno') else 'unknown'
            error_col = e.colno if hasattr(e, 'colno') else 'unknown'

            # 显示错误位置附近的内容
            lines = response.split('\n')
            if hasattr(e, 'lineno') and e.lineno <= len(lines):
                context_start = max(0, e.lineno - 3)
                context_end = min(len(lines), e.lineno + 2)
                context = '\n'.join([f"{i+1}: {lines[i]}" for i in range(context_start, context_end)])

                raise ValueError(
                    f"无法解析 LLM 返回的 JSON:\n"
                    f"错误位置: 第 {error_line} 行，第 {error_col} 列\n"
                    f"错误信息: {str(e)}\n\n"
                    f"错误附近内容:\n{context}\n\n"
                    f"完整响应长度: {len(response)} 字符\n"
                    f"响应开头:\n{response[:500]}...\n\n"
                    f"响应结尾:\n...{response[-500:]}"
                )
            else:
                raise ValueError(
                    f"无法解析 LLM 返回的 JSON: {e}\n"
                    f"响应长度: {len(response)} 字符\n"
                    f"响应内容:\n{response[:1000]}..."
                )

        # 构建完整数据结构
        # 计算内容分布
        topic_counts = {}
        for date_data in calendar_dict.values():
            topic_type = date_data.get("topic_type", "日常分享")
            topic_counts[topic_type] = topic_counts.get(topic_type, 0) + 1

        total = len(calendar_dict)
        content_ratio = {
            topic: round(count / total * 100, 1)
            for topic, count in topic_counts.items()
        }

        calendar_data = {
            "persona_name": persona_name,
            "month": year_month,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "calendar": calendar_dict,
            "monthly_strategy": {
                "content_ratio": content_ratio,
                "total_days": total
            }
        }

        return calendar_data
