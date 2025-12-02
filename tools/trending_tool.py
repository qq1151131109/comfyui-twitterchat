"""热点话题工具（基于 Google Trends）"""
from pytrends.request import TrendReq


class TrendingTopicsTool:
    """Google Trends 热点话题工具"""

    def __init__(self, geo: str = "US"):
        """
        初始化

        参数:
            geo: 地区代码 (US, GB, JP, worldwide, etc.)
        """
        self.geo = geo
        try:
            self.pytrends = TrendReq(hl='en-US', tz=360)
        except Exception as e:
            print(f"初始化 Google Trends 失败: {e}")
            self.pytrends = None

    def execute(self, top_n: int = 5) -> dict:
        """
        获取实时热搜话题

        参数:
            top_n: 返回前 N 个话题

        返回:
            {
                "topics": [
                    {"rank": 1, "title": "Taylor Swift"},
                    {"rank": 2, "title": "NBA Finals"},
                    ...
                ],
                "formatted": "Taylor Swift, NBA Finals, ..."
            }
        """
        if not self.pytrends:
            return {
                "error": "Google Trends 未初始化",
                "topics": [],
                "formatted": ""
            }

        try:
            # 获取实时热搜
            trending = self.pytrends.trending_searches(pn=self.geo)

            topics = []
            for i, topic in enumerate(trending[0][:top_n]):
                topics.append({
                    "rank": i + 1,
                    "title": topic
                })

            return {
                "topics": topics,
                "formatted": ", ".join([t["title"] for t in topics])
            }

        except Exception as e:
            return {
                "error": f"获取热搜失败: {str(e)}",
                "topics": [],
                "formatted": ""
            }
