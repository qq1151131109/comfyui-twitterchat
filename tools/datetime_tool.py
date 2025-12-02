"""日期时间工具（支持多国节假日）"""
import holidays
from datetime import datetime


class DateTimeTool:
    """日期时间工具"""

    def __init__(self, country: str = "US", compact: bool = True):
        """
        初始化

        参数:
            country: 国家代码 (US, GB, CA, AU, JP, KR, etc.)
            compact: 是否返回精简模式（默认 True）
                     True: 只返回 formatted, formatted_special 等关键字段
                     False: 返回所有原始字段
        """
        self.country = country
        self.compact = compact
        try:
            self.holidays = holidays.country_holidays(country)
        except:
            # 如果国家代码无效，默认使用 US
            self.holidays = holidays.country_holidays("US")

    def execute(self) -> dict:
        """
        获取当前日期时间信息

        返回 (compact=True):
            {
                "formatted": "2025-12-01 Monday",
                "special": None  # 或 "节假日: Christmas" / "周末" / "节假日: Christmas, 周末"
            }

        返回 (compact=False):
            {
                "date": "2025-11-28",
                "weekday": "Thursday",
                "weekday_cn": "周四",
                "time": "14:30",
                "is_holiday": False,
                "holiday_name": None,
                "is_weekend": False,
                "formatted": "2025-11-28 Thursday",
                "formatted_special": None
            }
        """
        now = datetime.now()
        date = now.date()

        # 判断是否节假日
        is_holiday = date in self.holidays
        holiday_name = self.holidays.get(date)

        # 判断是否周末
        is_weekend = now.weekday() >= 5

        # 构建智能的特殊信息描述（只包含有意义的信息）
        special_notes = []
        if is_holiday and holiday_name:
            special_notes.append(f"节假日: {holiday_name}")
        if is_weekend:
            special_notes.append("周末")

        formatted_special = ", ".join(special_notes) if special_notes else None
        formatted = now.strftime("%Y-%m-%d %A")

        # 根据模式返回不同的数据结构
        if self.compact:
            # 精简模式：只返回关键字段
            return {
                "formatted": formatted,
                "special": formatted_special  # 简化字段名
            }
        else:
            # 完整模式：返回所有字段（向后兼容）
            weekday_cn_map = {
                0: "周一", 1: "周二", 2: "周三", 3: "周四",
                4: "周五", 5: "周六", 6: "周日"
            }

            return {
                "date": now.strftime("%Y-%m-%d"),
                "weekday": now.strftime("%A"),
                "weekday_cn": weekday_cn_map[now.weekday()],
                "time": now.strftime("%H:%M"),
                "is_holiday": is_holiday,
                "holiday_name": holiday_name,
                "is_weekend": is_weekend,
                "formatted": formatted,
                "formatted_special": formatted_special
            }
