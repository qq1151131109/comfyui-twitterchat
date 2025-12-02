# 快速开始指南

## 1. 安装

依赖已自动安装完成 ✅

## 2. 配置 API Keys

### OpenWeatherMap (天气功能，可选)
1. 访问 https://openweathermap.org/api
2. 注册免费账号
3. 获取 API key
4. 在 ContextGatherer 节点中填入 `weather_api_key`

### OpenAI/Claude (推文生成，必需)
在 TweetGenerator 节点中配置:
- `api_key`: 你的 API key
- `api_base`:
  - OpenAI: `https://api.openai.com/v1`
  - Claude: `https://api.anthropic.com/v1`
- `model`: `gpt-4` 或 `claude-3-sonnet`

## 3. 准备人设文件

使用提供的示例人设:
```
examples/fitness_girl_emily.json
```

或创建自己的人设（参考 README.md 中的格式说明）。

## 4. 创建工作流

### 最简工作流（不使用上下文）

```
[PersonaLoader] → [ImagePromptBuilder]
                ↘ [TweetGenerator]
```

1. 添加 `PersonaLoader` 节点
   - `persona_file`: `examples/fitness_girl_emily.json`

2. 添加 `ImagePromptBuilder` 节点
   - 连接 `persona` 输出
   - `emphasis`: sexy
   - `intensity`: medium

3. 添加 `TweetGenerator` 节点
   - 连接 `persona` 输出
   - 填入 API key 和 model
   - `topic_type`: 身材展示类

4. 运行！

### 完整工作流（使用上下文）

```
[PersonaLoader] → [ContextGatherer] → [TweetGenerator]
                ↘ [ImagePromptBuilder]
```

在上面基础上添加:

1. 添加 `ContextGatherer` 节点
   - 连接 `persona` 输出
   - `enable_weather`: true
   - `weather_api_key`: 你的天气 API key
   - `city`: Los Angeles
   - `country_code`: US

2. 将 `context` 输出连接到 `TweetGenerator`

这样生成的推文会结合日期和天气信息！

## 5. 测试结果

### 图像提示词示例
```
masterpiece, best quality, 8k uhd, professional photography,
25 years old beautiful caucasian woman, blonde hair, blue eyes,
tall, slim, long legs, fair skin,
perfect hourglass figure, curvy body, sexy proportions, attractive figure,
seductive pose, alluring stance,
seductive expression, alluring eyes,
revealing outfit, tight clothes,
professional photography, dramatic lighting
```

### 推文示例
```
Today's leg day was INTENSE! 💪🔥
My glutes are gonna hate me tomorrow 😅
But the pump was worth it!
Who else crushed their workout today? 💕
#LegDay #FitnessMotivation #GymLife
```

## 6. 常见问题

### Q: 节点没有显示？
A: 重启 ComfyUI

### Q: 推文生成失败？
A: 检查 API key 是否正确，API base URL 是否匹配

### Q: 天气信息获取失败？
A: 检查 weather_api_key 是否有效，城市名是否正确

### Q: 想调整推文风格？
A: 修改 `topic_type` 或使用 `custom_topic` 自定义话题

## 7. 下一步

- 创建更多自定义人设
- 尝试不同的 `emphasis` 和 `intensity` 组合
- 调整 `temperature` 参数获得不同的推文风格
- 探索 Character Book 功能增强知识库

祝使用愉快！🚀
