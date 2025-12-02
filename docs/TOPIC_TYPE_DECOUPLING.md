# topic_type 解耦改进说明

## 📅 更新日期
2025-12-01

## 🎯 改进目标
移除 TweetGenerator 对硬编码模板的依赖，使系统能够适配不同风格的人设。

---

## ✅ 已完成的修改

### 1. TweetGenerator 改进 (nodes/tweet_generator.py)

#### 修改前：依赖硬编码模板

```python
# ❌ 旧实现
def _build_template_topic_prompt(...):
    # 从硬编码字典查找模板
    template_example = get_random_template(topic_type)
    # SEXY_TWEET_TEMPLATES["采茶日常"] → 找不到！
    # → fallback 到 "身材展示类"

    filled_example = fill_template_variables(template_example)
    # → "今天穿了{紧身衣}出门😘"

    user_prompt = f"""
    参考模板示例：
    {filled_example}  ← 性感模板！

    要求：
    3. 保持性感暧昧但不露骨  ← 硬编码要求！
    """
```

**问题**：
- 清纯人设被迫使用性感模板
- 无法扩展到新风格

#### 修改后：使用人设文件的 few-shot 示例

```python
# ✅ 新实现
def _build_template_topic_prompt(...):
    # 从人设文件提取相关示例
    few_shot_examples = self._extract_relevant_tweet_examples(
        persona, topic_type, calendar_plan
    )
    # → ["晚上一个人坐在院子里看星星... 🌙✨",
    #     "今天和爷爷在茶山忙了一天..."]

    examples_text = "\n参考以下人设推文示例的风格和语气：\n"
    for example in few_shot_examples:
        examples_text += f"- {example}\n"

    user_prompt = f"""
    {examples_text}  ← 人设自己的示例！

    要求：
    3. 保持人设的语言风格和性格特点  ← 通用要求
    """
```

**优势**：
- ✅ 示例来自人设文件，完全匹配风格
- ✅ 不依赖硬编码模板字典
- ✅ 自动适配所有人设

#### 新增方法：_extract_relevant_tweet_examples()

```python
def _extract_relevant_tweet_examples(self, persona, topic_type, calendar_plan, max_examples=3):
    """
    从人设文件中提取相关推文示例

    数据来源：
    1. persona["data"]["twitter_scenario"]["tweet_examples"]
    2. persona["data"]["extensions"]["twitter_persona"]["tweet_examples"]

    筛选逻辑：
    1. 优先选择 type 匹配 topic_type 的示例
    2. 其次选择包含 calendar_plan 关键词的示例
    3. 按相关性得分排序，取前 N 个
    4. 如果没有匹配，随机选择几个保底
    """
```

**示例效果**：

```
输入：
- topic_type: "采茶日常"
- calendar_plan.keywords: ["采茶", "茶山", "晨光"]
- persona: tea_girl_meilin.json

输出的 few_shot_examples：
1. "今天和爷爷在山上忙了一天，累但很充实~ ☀️🍃"
2. "早上起来第一件事就是去院子里呼吸新鲜空气~"
3. "看着爷爷忙碌的背影，突然很感动... 🥺"

✅ 完全符合茶园女孩的清纯风格！
```

---

### 2. CalendarManager 改进 (utils/calendar_manager.py)

#### 修改前：硬编码示例误导 LLM

```python
# ❌ 旧实现
输出格式示例：
{
  "2025-12-01": {
    "topic_type": "身材展示类",  ← 硬编码示例
    "theme": "新周开始 - 腿部训练日",
    ...
  }
}

要求：
2. 考虑一周节奏：
   - 周一：身材展示类 - 新周动力  ← 固定节奏
   - 周三：生活撒娇类 - 轻松日常
   ...
4. 内容分布：身材展示40%、暧昧互动25%...  ← 硬编码比例
```

**问题**：
- LLM 看到示例，倾向于模仿"身材展示类"等固定类型
- 即使 prompt 前面说"清纯茶园女孩"，示例仍然误导

#### 修改后：通用示例，强调自定义

```python
# ✅ 新实现
输出格式示例：
{
  "2025-12-01": {
    "topic_type": "根据人设定义的内容类型（如：采茶日常/传统文化/健身打卡/日常分享等）",
    "theme": "具体的推文主题",
    ...
  }
}

要求：
2. 根据人设特点设计一周节奏（周一到周日的内容类型）
5. topic_type 要符合人设特点（不要使用通用类型，要具体化）

重要提示：
- topic_type 应该根据人设特点自定义，不要使用固定模板
- 内容类型要符合角色的职业、兴趣、生活方式
- 保持风格一致性
```

**优势**：
- ✅ 不再误导 LLM 使用固定类型
- ✅ 明确要求 LLM 根据人设自定义
- ✅ 示例更加通用和灵活

---

## 🔄 数据流对比

### 优化前

```
CalendarManager 生成日历
  ↓ LLM 看到硬编码示例
  ↓ "身材展示类"、"福利互动类"
  ↓
生成：topic_type: "采茶日常"（勉强符合人设，但 LLM 不太敢偏离示例）
  ↓
TweetGenerator 接收
  ↓ 查找 SEXY_TWEET_TEMPLATES["采茶日常"]
  ↓ 找不到！
  ↓ fallback 到 "身材展示类"
  ↓
使用模板："今天穿了{紧身衣}出门😘 被说很{性感}哦💕"
  ↓
❌ 清纯茶园女孩推文变成性感风格
```

### 优化后

```
CalendarManager 生成日历
  ↓ LLM 看到通用示例和明确指示
  ↓ "topic_type 要符合人设特点"
  ↓
生成：topic_type: "采茶日常"（完全符合人设，LLM 自由发挥）
  ↓
TweetGenerator 接收
  ↓ 不查找硬编码模板
  ↓ 调用 _extract_relevant_tweet_examples()
  ↓ 从人设文件提取相关示例
  ↓
few_shot_examples = [
  "今天和爷爷在茶山忙了一天...",
  "早上采茶，看到晨光洒在茶叶上..."
]
  ↓
传递给 LLM："参考以下人设推文示例的风格和语气..."
  ↓
✅ 生成符合清纯茶园女孩风格的推文
```

---

## 📊 改进效果

| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| **模板来源** | 硬编码字典（4个固定类型） | 人设文件（无限扩展） | ✅ 完全灵活 |
| **风格匹配** | 强制性感风格 | 自动匹配人设风格 | ✅ 准确匹配 |
| **扩展性** | 新人设需修改代码 | 新人设无需修改代码 | ✅ 零代码扩展 |
| **topic_type 自由度** | 受限于4个固定类型 | 完全自定义 | ✅ 无限制 |
| **代码耦合** | 高度耦合 | 完全解耦 | ✅ 架构优化 |

---

## 🧪 如何测试

### 测试场景 1: 茶园女孩（林美灵）

#### 步骤：
1. 加载 tea_girl_meilin.json 人设
2. 生成 12月日历（CalendarManager）
3. 使用日历生成推文（TweetGenerator）

#### 预期结果：

**日历生成**：
```json
{
  "2025-12-01": {
    "topic_type": "采茶日常",  // ✅ 符合茶园人设
    "theme": "清晨采茶 - 茶山劳作",
    "keywords": ["采茶", "茶山", "晨光", "传统"],
    "suggested_scene": "tea mountain, morning light, traditional clothes, picking tea"
  },
  "2025-12-03": {
    "topic_type": "传统文化",  // ✅ 符合人设标签
    "theme": "茶艺展示 - 传统手工制茶",
    ...
  }
}
```

**推文生成**：
```
使用的 few-shot 示例：
1. "今天和爷爷在山上忙了一天，累但很充实~ ☀️🍃"
2. "早上起来第一件事就是去院子里呼吸新鲜空气~"

生成的推文：
"清晨五点就和爷爷上山采茶了~ ☀️🍃 茶叶上还挂着露珠呢，晶莹剔透的好美！
最喜欢这种和大自然亲近的感觉了💕 你们起这么早会做什么呀？ #采茶日常 #茶山生活"

场景描述：
"tea mountain, early morning, wearing casual clothes, picking tea leaves, peaceful atmosphere"

✅ 完全符合清纯茶园女孩风格！
```

### 测试场景 2: 健身女孩（Emily）

#### 预期结果：

**日历生成**：
```json
{
  "2025-12-01": {
    "topic_type": "健身打卡",  // ✅ 符合健身人设
    "theme": "新周训练 - 腿部日",
    "keywords": ["健身", "训练", "腿部", "动力"],
    "suggested_scene": "gym, leg workout, after training"
  }
}
```

**推文生成**：
```
使用的 few-shot 示例：
1. "Just finished an amazing workout session. Feeling pumped! 💪🔥"
2. "Leg day = best day! 💪 Who else loves that post-workout burn?"

生成的推文：
"Monday motivation! 💪 Just crushed leg day and feeling SO good! 🔥
My glutes are gonna hate me tomorrow 😅 Who's training with me today? #FitnessMotivation #LegDay"

✅ 符合健身网红风格！
```

---

## 🚀 向后兼容性

### ✅ 完全向后兼容

1. **旧人设文件仍然可用**
   - 如果没有 tweet_examples，系统会优雅降级
   - 不会崩溃或报错

2. **SEXY_TWEET_TEMPLATES 保留但不使用**
   - 代码仍然存在（templates/sexy_templates.py）
   - 但 TweetGenerator 不再调用
   - 可以后续删除

3. **topic_type 仍然保留**
   - 用于内容分类和统计
   - 但不再用于模板查找

---

## 📝 后续优化建议

### 短期（可选）

1. **优化 few-shot 示例选择算法**
   - 当前使用简单的关键词匹配
   - 可以改用语义相似度（embedding）

2. **添加缓存机制**
   - 缓存提取的 few-shot 示例
   - 避免重复解析人设文件

### 长期（待讨论）

1. **完全废弃 topic_type**
   - 改用更灵活的标签系统
   - 或者只用 theme 字段

2. **删除 SEXY_TWEET_TEMPLATES**
   - 清理死代码
   - 简化代码库

---

## 🎉 总结

这次改进成功解决了 topic_type 不灵活的核心问题：

✅ **解耦了模板系统**：TweetGenerator 不再依赖硬编码模板
✅ **提升了灵活性**：自动适配所有人设风格
✅ **改善了质量**：使用人设自己的示例，风格更准确
✅ **保持了兼容性**：旧系统仍然可用
✅ **架构更清晰**：职责分离，易于维护

现在，林美灵可以生成符合清纯茶园女孩风格的推文了！🍵✨
