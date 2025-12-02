# 人设模板 V2.1 更新说明

## 📅 更新时间
2025-12-01

## 🎯 主要改进

### 1. 增强了 `system_prompt` 字段说明

**之前**：简单的一句话模板
```json
"system_prompt": "你是{角色名}，{年龄}岁..."
```

**现在**：包含完整的编写指南
```json
"system_prompt": "⭐ 改进建议：这个字段应该包含完整的角色身份定义和基本行为准则。

示例模板：
你是{角色名}，{年龄}岁，{地点}人，{职业/学生}。你{性格特点详细描述，至少3-4个维度}。你喜欢{爱好和日常，具体举例}。你在社交媒体上{内容定位、风格、目标}。你的语气{语言风格、用词特点、情绪表达}。

⚠️ 建议至少包含：
1. 基本身份（年龄、地点、职业）
2. 性格特征（3-5个维度）
3. 兴趣爱好（具体的）
4. 社交媒体定位（目标、风格、内容）
5. 语言风格（语气、用词、emoji倾向）"
```

### 2. 新增 `tweet_guidance` 字段 ⭐

**位置**：`extensions.tweet_guidance`

**作用**：提供完整的推文生成指导，会被 TweetGenerator 优先使用

**示例**：
```json
{
  "extensions": {
    "tweet_guidance": "你的推文目标是吸引25-45岁有消费力男性粉丝。

内容风格要求:
- 清纯邻家女孩形象，温柔亲切
- 适度暧昧但不露骨，保持真诚感
- 多用互动性话题，引导粉丝评论
- emoji 偏向清纯可爱类: 🌸🍵✨💕🥰😊🌿
- 分享真实生活细节增加亲切感
- 完全避免商业化，保持自然

内容类型分布:
- 60% 个人生活/日常分享
- 25% 特色背景（工作/兴趣/传统文化）
- 15% 暧昧互动（温柔撒娇/情感连接）

重要禁忌:
- 禁止内容1
- 禁止内容2"
  }
}
```

**优先级**：`tweet_guidance` > tags 自动匹配 > 默认风格

### 3. 增强了 `tags` 字段说明

**之前**：只有普通标签
```json
"tags": ["标签1", "标签2"]
```

**现在**：包含自动风格匹配的说明
```json
"tags": [
  "标签1",
  "标签2",
  "⭐ 重要：如果是清纯风格，添加：cute, innocent, girl-next-door, traditional 中的一个或多个",
  "⭐ 这些标签会影响 TweetGenerator 自动选择的推文风格！"
]
```

**自动匹配规则**：
- 包含 `cute`, `innocent`, `girl-next-door`, `traditional` → **清纯风格**
- 其他 → **性感风格**

### 4. 更新了 `tweet_preferences` 字段说明

**改进**：明确标注哪些字段会被 TweetGenerator 读取

```json
"tweet_preferences": {
  "emoji_usage": "emoji 使用风格描述（会被 TweetGenerator 读取）",
  "avg_tweet_length": "推文长度（如 60-120字，会被 TweetGenerator 读取）",
  "hashtag_style": "标签风格（如：生活化+传统文化，会被 TweetGenerator 读取）"
}
```

### 5. 添加了顶部使用说明

```json
{
  "_README": "=== ComfyUI TwitterChat 人设模板 V2 ===",
  "_使用说明": "1. 复制此文件并重命名；2. 填写所有必要字段；3. 删除带⭐的说明文字；4. 参考示例",
  "_重点字段": {
    "system_prompt": "⚠️ 必填！",
    "tags": "⚠️ 重要！会触发自动风格匹配",
    "extensions.tweet_guidance": "⭐ 推荐填写！优先级最高"
  },
  "_更新日志": "v2.1 (2025-12-01): ..."
}
```

---

## 📖 使用指南

### 快速开始

1. **复制模板文件**
   ```bash
   cp persona_template_v2.json my_persona.json
   ```

2. **填写必要字段**
   - ✅ `name` - 角色名称
   - ✅ `system_prompt` - 完整的角色定义（参考模板中的建议）
   - ✅ `tags` - 添加合适的标签（注意清纯风格标签）
   - ⭐ `extensions.tweet_guidance` - 推荐填写完整的推文指导

3. **删除说明文字**
   - 删除所有带 `⭐` 的说明文字
   - 删除 `_README`, `_使用说明` 等元数据字段

4. **测试**
   - 在 ComfyUI 中加载人设
   - 查看生成的推文是否符合预期
   - 根据需要调整 `tweet_guidance`

---

## 🎯 三种配置方式对比

### 方式 1：仅使用 tags 自动匹配（最简单）

```json
{
  "tags": ["tea", "girl-next-door", "traditional", "cute"],
  "system_prompt": "基本的角色定义..."
}
```

**效果**：TweetGenerator 自动使用清纯风格

**适合**：快速测试、风格明确的人设

---

### 方式 2：使用 tweet_guidance 自定义（推荐）⭐

```json
{
  "tags": ["tea", "traditional"],
  "system_prompt": "详细的角色定义...",
  "extensions": {
    "tweet_guidance": "完整的推文生成指导..."
  }
}
```

**效果**：使用自定义的完整指导

**适合**：需要精确控制风格的人设

---

### 方式 3：在节点中使用 override（最灵活）

不修改人设文件，直接在 **Generate Tweet** 节点的 `system_prompt_override` 参数中输入完整提示词。

**效果**：完全覆盖所有自动生成的提示词

**适合**：快速测试、临时调整

---

## 📚 参考示例

### 清纯风格示例
- `examples/tea_girl_meilin_v1.json` - 茶园女孩林美灵

### 性感风格示例
- `examples/fitness_girl_emily.json` - 健身网红 Emily

---

## ⚙️ TweetGenerator 的提示词构建逻辑

### 优先级（从高到低）

1. **节点参数 `system_prompt_override`**（最高优先级）
   - 如果填写，直接使用，跳过所有自动生成

2. **人设文件 `extensions.tweet_guidance`**
   - 如果存在，使用作为风格指导

3. **tags 自动匹配**
   - 检查 tags 是否包含清纯风格标签
   - 选择对应的风格模板

4. **默认性感风格**（最低优先级）
   - 如果以上都没有，使用默认性感风格

### 组合结果

最终的 system_prompt 由以下部分组成：

```
[人设的 system_prompt]
+
[风格指导：tweet_guidance 或 自动匹配的风格]
+
[上下文信息：日期、天气]
+
[推文风格要求：tweet_preferences]
+
[重要原则]
```

---

## 🔧 故障排除

### 问题：生成的推文风格不对

**检查**：
1. 是否在 tags 中添加了正确的风格标签？
2. 是否填写了 `tweet_guidance`？
3. 是否在节点中错误使用了 `system_prompt_override`？

**解决**：
- 清纯风格：确保 tags 包含 `cute`, `innocent`, `girl-next-door`, 或 `traditional`
- 精确控制：填写完整的 `tweet_guidance`

### 问题：system_prompt 太简单

**解决**：参考模板中的建议，至少包含5个维度：
1. 基本身份
2. 性格特征（3-5个）
3. 兴趣爱好（具体的）
4. 社交媒体定位
5. 语言风格

---

**参考完整文档**：`docs/OPTIMIZE_SYSTEM_PROMPT.md`
