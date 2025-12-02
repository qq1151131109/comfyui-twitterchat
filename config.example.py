# API 配置文件
# 复制此文件为 config.py 并填入你的 API keys

# ===== LLM API 配置 (必需) =====

# OpenAI 配置
OPENAI_API_KEY = "sk-your-openai-api-key-here"
OPENAI_API_BASE = "https://api.openai.com/v1"
OPENAI_MODEL = "gpt-4"

# 或者使用 Claude
CLAUDE_API_KEY = "sk-ant-your-claude-api-key-here"
CLAUDE_API_BASE = "https://api.anthropic.com/v1"
CLAUDE_MODEL = "claude-3-sonnet-20240229"

# 选择使用哪个 LLM (推荐 OpenAI)
USE_LLM = "openai"  # 可选: "openai" 或 "claude"


# ===== 天气 API 配置 (可选) =====

# OpenWeatherMap API
# 注册地址: https://openweathermap.org/api
# 免费额度: 60次/分钟, 1,000,000次/月
WEATHER_API_KEY = "your-openweathermap-api-key-here"


# ===== 热搜配置 (可选) =====

# Google Trends 地区
# 可选: US, GB, JP, worldwide
TRENDING_GEO = "US"


# ===== 默认配置 =====

# 默认节假日国家
DEFAULT_HOLIDAY_COUNTRY = "US"

# 默认温度参数
DEFAULT_TEMPERATURE = 0.85

# 默认话题类型
DEFAULT_TOPIC_TYPE = "身材展示类"


# ===== 辅助函数 =====

def get_llm_config():
    """获取 LLM 配置"""
    if USE_LLM == "openai":
        return {
            "api_key": OPENAI_API_KEY,
            "api_base": OPENAI_API_BASE,
            "model": OPENAI_MODEL
        }
    elif USE_LLM == "claude":
        return {
            "api_key": CLAUDE_API_KEY,
            "api_base": CLAUDE_API_BASE,
            "model": CLAUDE_MODEL
        }
    else:
        raise ValueError(f"未知的 LLM 类型: {USE_LLM}")


def validate_config():
    """验证配置是否完整"""
    errors = []

    # 检查 LLM 配置
    llm_config = get_llm_config()
    if "your-" in llm_config["api_key"]:
        errors.append(f"请配置 {USE_LLM.upper()} API key")

    # 检查天气 API (可选)
    if WEATHER_API_KEY and "your-" in WEATHER_API_KEY:
        print("⚠️  天气 API key 未配置（可选功能）")

    if errors:
        raise ValueError("配置错误:\n" + "\n".join(f"  - {e}" for e in errors))

    print("✅ 配置验证通过!")
    return True
