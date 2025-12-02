"""上下文收集节点"""
# 使用相对导入
from ..tools.datetime_tool import DateTimeTool
from ..tools.weather_tool import WeatherTool
from ..tools.trending_tool import TrendingTopicsTool
from ..utils.persona_utils import get_persona_location


class ContextGatherer:
    """上下文收集器（日期、天气、热搜）"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "persona": ("PERSONA",),
            },
            "optional": {
                # 天气设置
                "enable_weather": ("BOOLEAN", {"default": True}),
                "weather_api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "OpenWeatherMap API key"
                }),

                # 热搜设置
                "enable_trending": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("CONTEXT",)
    RETURN_NAMES = ("context",)
    FUNCTION = "gather"
    CATEGORY = "TwitterChat"
    DESCRIPTION = "Gather context information (date, weather, trending) automatically from persona location"

    def gather(self, persona, enable_weather=True, weather_api_key="",
               enable_trending=False):
        """
        收集上下文信息（完全从人设中读取地理位置）

        返回:
            context 字典
        """
        context = {}

        # 从人设获取城市和国家代码
        city, country_code = get_persona_location(persona)

        # 1. 日期时间（必选，使用精简模式）
        try:
            # 使用人设的国家代码检测节假日，启用精简模式
            date_tool = DateTimeTool(country=country_code, compact=True)
            context["date"] = date_tool.execute()
        except Exception as e:
            context["date"] = {"error": str(e)}

        # 2. 天气（可选）
        if enable_weather:
            try:
                if weather_api_key and city:
                    weather_tool = WeatherTool(weather_api_key)
                    context["weather"] = weather_tool.execute(city, country_code)
                elif not weather_api_key:
                    context["weather"] = {"error": "未配置 weather_api_key"}
                else:
                    context["weather"] = {"error": "人设中未配置城市信息"}
            except Exception as e:
                context["weather"] = {"error": str(e)}

        # 3. 热搜（可选）
        if enable_trending:
            try:
                # 使用人设的国家代码获取热搜
                trending_tool = TrendingTopicsTool(geo=country_code)
                context["trending"] = trending_tool.execute(top_n=5)
            except Exception as e:
                context["trending"] = {"error": str(e)}

        return (context,)


# 节点注册
NODE_CLASS_MAPPINGS = {
    "ContextGatherer": ContextGatherer
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ContextGatherer": "Gather Context (Date/Weather/Trending)"
}
