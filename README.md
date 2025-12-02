# ComfyUI TwitterChat

美女人设推文生成系统 - 基于 SillyTavern Character Card 的智能内容生成工具

## 功能特性

- ✅ **SillyTavern 人设支持** - 兼容 Character Card V2 格式
- ✅ **智能图像提示词** - 从人设动态生成优化的 SD 提示词
- ✅ **上下文感知推文** - 结合日期、天气、热搜生成真实内容
- ✅ **擦边内容优化** - 专为吸引男性粉丝设计的内容策略
- ✅ **灵活可扩展** - 模块化设计，易于定制

## 节点说明

### 1. PersonaLoader (人设加载器)
从 JSON 或 PNG 文件加载 SillyTavern Character Card

**输入**:
- `persona_file`: JSON 文件路径
- `load_from_png`: PNG 文件路径（可选）

**输出**:
- `persona`: PERSONA 对象
- `summary`: 人设摘要文本

### 2. ContextGatherer (上下文收集器)
收集日期、天气、热搜等上下文信息

**输入**:
- `persona`: PERSONA 对象
- `enable_weather`: 是否启用天气 (默认 True)
- `weather_api_key`: OpenWeatherMap API key
- `city`: 城市名称（留空则从人设获取）
- `country_code`: 国家代码 (默认 US)
- `holiday_country`: 节假日国家 (US/GB/CA/AU/JP/KR/FR/DE)
- `enable_trending`: 是否启用热搜 (默认 False)
- `trending_geo`: 热搜地区 (US/GB/JP/worldwide)

**输出**:
- `context`: CONTEXT 对象

**注意**: 此节点是可选的，可以直接将 persona 连接到 TweetGenerator

### 3. ImagePromptBuilder (图像提示词生成器)
从人设动态构建图像生成提示词

**输入**:
- `persona`: PERSONA 对象
- `emphasis`: 风格强调 (normal/sexy/cute/elegant)
- `intensity`: 强度 (light/medium/strong)
- `scene`: 场景描述（可选）
- `custom_positive`: 自定义正面提示词
- `custom_negative`: 自定义负面提示词

**输出**:
- `positive_prompt`: 正面提示词
- `negative_prompt`: 负面提示词

### 4. TweetGenerator (推文生成器)
生成符合人设的推文内容

**输入**:
- `persona`: PERSONA 对象
- `api_key`: OpenAI/Claude API key
- `api_base`: API base URL (默认 OpenAI)
- `model`: 模型名称 (默认 gpt-4)
- `context`: CONTEXT 对象（可选）
- `topic_type`: 话题类型 (身材展示类/暧昧互动类/生活撒娇类/福利互动类)
- `custom_topic`: 自定义话题（覆盖 topic_type）
- `temperature`: 温度参数 (默认 0.85)

**输出**:
- `tweet`: 推文文本

## 安装步骤

1. 克隆或下载到 ComfyUI 的 custom_nodes 目录:
```bash
cd ComfyUI/custom_nodes
git clone <repo_url> comfyui-twitterchat
```

2. 安装依赖:
```bash
cd comfyui-twitterchat
pip install -r requirements.txt
```

3. 重启 ComfyUI

## 使用示例

### 场景 1: 简单工作流（不使用上下文）

```
PersonaLoader → ImagePromptBuilder
              ↘ TweetGenerator
```

1. PersonaLoader 加载人设
2. ImagePromptBuilder 生成图像提示词
3. TweetGenerator 生成推文（不连接 context）

### 场景 2: 完整工作流（使用上下文）

```
PersonaLoader → ContextGatherer → TweetGenerator
              ↘ ImagePromptBuilder
```

1. PersonaLoader 加载人设
2. ContextGatherer 收集日期/天气
3. ImagePromptBuilder 生成图像提示词
4. TweetGenerator 生成推文（连接 context，内容会结合天气和日期）

## SillyTavern Character Card 格式

本系统使用 SillyTavern Character Card V2 格式。人设 JSON 文件应包含以下结构:

```json
{
  "spec": "chara_card_v2",
  "spec_version": "2.0",
  "data": {
    "name": "角色名",
    "description": "角色描述",
    "personality": "性格特征",
    "scenario": "场景设定",
    "system_prompt": "系统提示词",
    "mes_example": "对话示例",
    "character_book": {
      "entries": [
        {
          "keys": ["关键词"],
          "content": "知识内容",
          "enabled": true,
          "priority": 10
        }
      ]
    },
    "extensions": {
      "twitter_persona": {
        "appearance": {
          "age": "25",
          "gender": "女",
          "ethnicity": "Asian",
          "face": "瓜子脸, 大眼睛, 高鼻梁",
          "eyes": "棕色大眼睛",
          "hair": "栗棕色长发, 微卷",
          "skin": "白皙光滑",
          "body": "高挑纤细, 170cm, 长腿",
          "bust": "C cup",
          "clothing": "时尚高级",
          "makeup": "精致自然"
        },
        "tweet_preferences": {
          "emoji_usage": "适度使用",
          "hashtag_style": "时尚+生活化",
          "avg_tweet_length": "60-120字"
        }
      },
      "location": {
        "city": "New York",
        "country_code": "US"
      }
    }
  }
}
```

## API 配置

### OpenWeatherMap (天气 API)
1. 注册免费账号: https://openweathermap.org/api
2. 获取 API key
3. 在 ContextGatherer 节点中填入 `weather_api_key`

免费额度: 60 calls/minute, 1,000,000 calls/month

### OpenAI/Claude (LLM API)
在 TweetGenerator 节点中配置:
- `api_key`: 你的 API key
- `api_base`: API 端点
  - OpenAI: `https://api.openai.com/v1`
  - Claude: `https://api.anthropic.com/v1`
  - 其他兼容 OpenAI API 的服务
- `model`: 模型名称
  - OpenAI: `gpt-4`, `gpt-3.5-turbo`
  - Claude: `claude-3-opus`, `claude-3-sonnet`

## 内容策略

本系统专为吸引男性粉丝设计，推文内容分布:

- **40% 身材展示类** - 健身、穿搭、自拍
- **30% 生活日常类** - 带点性感暗示的日常分享
- **20% 互动福利类** - 抽奖、答疑、撒娇互动
- **10% 工作花絮类** - 拍摄、活动幕后

## 常见问题

### Q: 如何创建自己的人设？
A: 按照 SillyTavern Character Card V2 格式创建 JSON 文件，或使用 SillyTavern 工具导出 PNG 文件。

### Q: 不想使用天气功能怎么办？
A: 在 ContextGatherer 中将 `enable_weather` 设为 False，或者直接跳过 ContextGatherer 节点。

### Q: 推文生成需要付费 API 吗？
A: 是的，TweetGenerator 需要 OpenAI 或 Claude API。也可以使用本地 LLM（需要兼容 OpenAI API 格式）。

### Q: 图像提示词可以直接用于 SD 吗？
A: 可以！ImagePromptBuilder 输出的提示词可以直接连接到 CLIPTextEncode 节点。

## 开发者

- 基于 ComfyUI 框架开发
- 支持 SillyTavern Character Card V2 标准
- 遵循 ComfyUI 节点开发规范

## 许可证

MIT License

## 更新日志

### v1.0.0 (2025-11-28)
- ✅ 初始版本发布
- ✅ 4个核心节点实现
- ✅ SillyTavern 格式支持
- ✅ 海外 API 集成 (OpenWeatherMap, Google Trends)
- ✅ 擦边内容优化
