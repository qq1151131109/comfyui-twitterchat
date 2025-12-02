# TwitterChat 人设编写指南

## 📚 分层信息架构设计理念

为了避免 LLM 上下文爆炸，同时确保信息完整可用，我们采用**分层按需加载**的架构设计。

---

## 🗂️ 信息分层结构

### **第一层：根级必选字段**
这些字段总是被加载，是人设的核心身份。

```json
{
  "spec": "chara_card_v2",
  "spec_version": "2.0",
  "data": {
    "name": "角色姓名",
    "备注": "人设简介和用途说明",
    "tags": ["标签1", "标签2"],
    "character_version": "1.0",

    "description": "1-2句话的角色简介",
    "personality": "性格关键词，逗号分隔"
  }
}
```

**用途：**
- `name`: LLM 生成时的自我称呼
- `description`: 快速了解角色定位
- `personality`: 决定语气和行为风格

---

### **第二层：场景配置**
根据一期（Twitter）或二期（WhatsApp）**按场景加载**。

#### **2.1 Twitter 推文场景** - `twitter_scenario`

```json
"twitter_scenario": {
  "scene_description": "场景描述文字",
  "content_strategy_guide": "内容分布策略",

  "tweet_examples": [
    {
      "type": "内容类型",
      "text": "推文示例文本",
      "context": "发布场景",
      "scene_hint": "图片场景描述（给 ImagePromptBuilder）"
    }
  ],

  "alternate_tweet_openings": [
    "开场白1",
    "开场白2"
  ]
}
```

**加载时机：** 一期推文生成时
**用途：**
- LLM 学习推文风格
- 提供 Few-shot 示例
- scene_hint 传递给 ImagePromptBuilder

---

#### **2.2 WhatsApp 聊天场景** - `whatsapp_scenario`

```json
"whatsapp_scenario": {
  "scene_description": "聊天场景描述",
  "conversation_strategy_guide": "对话策略指导",

  "first_message": "首次欢迎消息",

  "alternate_greetings": [
    "早安问候",
    "晚安问候"
  ],

  "chat_examples": [
    {
      "scenario": "聊天场景",
      "exchange": "<START>\n{{user}}: 用户消息\n{{char}}: 角色回复"
    }
  ]
}
```

**加载时机：** 二期 WhatsApp 聊天时
**用途：**
- LLM 学习对话风格
- Few-shot 聊天示例
- 首次欢迎消息模板

---

### **第三层：知识库** - `character_book`
基于**关键词检索**，按需注入。

```json
"character_book": {
  "name": "知识库名称",
  "entries": [
    {
      "keys": ["关键词1", "关键词2"],
      "content": "相关知识内容",
      "priority": 10,
      "enabled": true
    }
  ]
}
```

**工作原理：**
1. 用户消息/推文话题包含 `keys` 中的关键词
2. 自动将 `content` 注入到 LLM prompt
3. `priority` 越高越优先注入
4. 最多注入 2-3 个条目（避免上下文过长）

**示例：**
```
推文话题："今天练腿"
→ 检测到关键词 "腿"、"练"
→ 检索到条目：
   {
     "keys": ["leg", "腿部", "训练"],
     "content": "Emily 的腿部训练包括深蹲、硬拉...",
     "priority": 10
   }
→ 注入到 prompt
→ LLM 生成专业且一致的内容
```

---

### **第四层：扩展信息** - `extensions`
分为多个子层，**按需加载**。

#### **4.1 核心层** - `core_info` ✅ 总是加载

```json
"extensions": {
  "core_info": {
    "age": 23,
    "birthday": "2001-04-12",
    "zodiac": "Aries",
    "location": {
      "city": "城市",
      "state/province": "州/省",
      "country_code": "国家代码"
    }
  }
}
```

**用途：**
- 基础身份信息
- ContextGatherer 自动读取 location
- 推文/聊天中提及年龄、生日等

---

#### **4.2 背景层** - `background_info` ⚠️ 按需加载

```json
"background_info": {
  "education": {
    "school": "学校名称",
    "major": "专业",
    "year/graduation_year": "年级/毕业年份"
  },
  "career": {
    "current_job": "当前工作",
    "previous_jobs": ["过往工作1", "工作2"]
  },
  "family": {
    "hometown": "家乡",
    "parents": "父母情况",
    "siblings": "兄弟姐妹",
    "relationship_status": "感情状态"
  },
  "living": {
    "residence": "居住情况",
    "roommate": "室友/家人"
  }
}
```

**加载时机：**
- 一期：话题涉及学校/工作/家庭时加载
- 二期：聊天涉及背景信息时加载

**用途：**
- 提供具体细节
- 增强真实感
- 聊天时有话可说

---

#### **4.3 生活细节层** - `lifestyle_details` 📝 按话题加载

```json
"lifestyle_details": {
  "daily_routine": {
    "wake_up": "起床时间",
    "morning/afternoon/evening": "各时段安排"
  },
  "hobbies": ["爱好1", "爱好2"],
  "favorite_things": {
    "music": "音乐偏好",
    "movies": "电影偏好",
    "food": "食物偏好",
    "drink": "饮品偏好"
  },
  "quirks": ["个人癖好1", "癖好2"],
  "social_media_habits": "社交媒体习惯（一期用）"
}
```

**加载时机：**
- 话题相关时动态加载
- 例如：用户问"你喜欢什么音乐" → 加载 favorite_things.music

**用途：**
- 丰富对话内容
- 展现个性
- 建立亲密感

---

#### **4.4 场景专属配置**

##### **Twitter 专属** - `twitter_persona` (一期)

```json
"twitter_persona": {
  "social_accounts": {
    "twitter_handle": "@用户名",
    "display_name": "显示名",
    "bio": "简介",
    "follower_count": "粉丝数"
  },
  "tweet_preferences": {
    "emoji_usage": "emoji 使用风格",
    "hashtag_count": "每条推文标签数",
    "common_hashtags": ["#标签1", "#标签2"],
    "avg_length": "推文长度",
    "tone_distribution": {
      "语气1": 0.4,
      "语气2": 0.3
    }
  },
  "content_themes": {
    "主题1": {
      "frequency": "比例",
      "examples": ["示例1", "示例2"],
      "goal": "目的"
    }
  },
  "posting_strategy": {
    "best_times": ["时间段1", "时间段2"],
    "frequency": "每天发推数"
  },
  "sales_funnel": {
    "cta_frequency": 0.15,
    "cta_examples": ["引流文案1", "引流文案2"]
  }
}
```

---

##### **WhatsApp 专属** - `whatsapp_scenario` (二期)

```json
"whatsapp_scenario": {
  // (已在第二层场景配置中说明)

  "community_info": {
    "group_name": "群名称",
    "platform": "WhatsApp",
    "price": "价格",
    "benefits": ["福利1", "福利2"]
  },

  "conversation_style": {
    "intimacy_level": "亲密程度",
    "response_time": "回复时间",
    "emoji_usage": "emoji 风格"
  },

  "sales_techniques": {
    // 销售技巧详细配置
  },

  "boundary_settings": {
    "appropriate_topics": ["合适话题"],
    "boundary_responses": {
      "too_personal": "边界回复话术"
    }
  }
}
```

---

#### **4.5 技术配置层**

##### **LoRA 配置** - `lora` (一期)

```json
"lora": {
  "model_name": "lora 模型名",
  "trigger_words": ["触发词1", "触发词2"],
  "recommended_weight": 0.8,
  "notes": "使用说明"
}
```

---

##### **内容限制** - `content_restrictions` (通用)

```json
"content_restrictions": {
  "nsfw_level": "尺度级别",
  "allowed": ["允许内容1"],
  "prohibited": ["禁止内容1"],
  "tone_guideline": "总体风格指导"
}
```

---

##### **目标受众** - `target_audience` (通用)

```json
"target_audience": {
  "primary_demographics": {
    "gender": "性别分布",
    "age_range": "年龄范围",
    "interests": ["兴趣1", "兴趣2"]
  },
  "psychological_appeal": ["心理诉求1", "诉求2"],
  "engagement_goals": {
    "likes_per_post": "目标点赞数"
  }
}
```

---

## 🎯 按需加载策略

### **一期：Twitter 推文生成**

```
加载顺序：
1. 根级字段 (name, description, personality) ✅ 总是
2. twitter_scenario ✅ 总是
3. core_info ✅ 总是
4. twitter_persona ✅ 总是
5. character_book → 关键词检索 🔍 按需
6. background_info → 话题相关 🔍 按需
7. lifestyle_details → 话题相关 🔍 按需
```

**示例：**
```
话题："周末海滩运动"
→ 加载 core_info.location (确认在海边城市)
→ 加载 lifestyle_details.hobbies (周末去海滩)
→ 不加载 background_info.education (无关)
→ 检索 character_book (无匹配关键词)
→ 生成推文："周末的海边跑步太舒服了 🌊☀️"
```

---

### **二期：WhatsApp 聊天**

```
加载顺序：
1. 根级字段 ✅ 总是
2. whatsapp_scenario ✅ 总是
3. core_info ✅ 总是
4. background_info ✅ 总是（聊天需要更多背景）
5. character_book → 关键词检索 🔍 按需
6. lifestyle_details → 话题相关 🔍 按需
7. whatsapp_scenario.sales_techniques → 销售时 🔍 按需
```

**示例：**
```
粉丝问："你平时喜欢做什么？"
→ 加载 lifestyle_details.hobbies
→ 加载 lifestyle_details.daily_routine
→ 回复："我大部分时间都在茶园帮爷爷 🍃 早上采茶，晚上泡茶看书..."
```

---

## 📝 编写建议

### **1. 信息完整性 vs 上下文控制**

- **完整性**：所有可能用到的信息都要写进去
- **控制**：通过分层和按需加载避免全部塞给 LLM

### **2. 细节真实性**

- 具体 > 抽象（"福建农林大学茶学专业" > "大学生"）
- 有温度 > 无感情（"爷爷16岁学做茶" > "家族茶园"）

### **3. 一致性检查**

- 年龄与毕业年份匹配
- 地理位置一致（城市、气候、文化）
- 性格与行为一致

### **4. 商业目标明确**

- 一期：吸引 → 建立信任 → 引流
- 二期：深度互动 → 促成购买 → 维护复购

---

## 🎨 人设类型模板

### **健身/身材展示类**（参考 Sophia）
- 重点：`lifestyle_details`（训练、饮食）
- 风格：性感活力、学生感
- 商业模式：会员订阅制

### **产品销售类**（参考美灵）
- 重点：`character_book`（产品知识）+ `sales_techniques`
- 风格：清纯温柔、传统美
- 商业模式：实物销售 + 复购

### **知识付费类**
- 重点：专业背景 + 知识库
- 风格：专业权威 + 亲和力
- 商业模式：课程/咨询

---

## ✅ 人设质量检查清单

- [ ] 根级字段完整（name, description, personality）
- [ ] 场景配置完整（twitter_scenario 和/或 whatsapp_scenario）
- [ ] character_book 至少 3-5 个条目
- [ ] core_info 包含年龄、生日、位置
- [ ] background_info 包含教育、职业、家庭、居住
- [ ] lifestyle_details 包含作息、爱好、喜好
- [ ] 场景专属配置完整
- [ ] 所有示例（tweet_examples, chat_examples）真实自然
- [ ] 信息之间无矛盾
- [ ] 商业策略清晰

---

## 📄 空白模板

见下一个文件：`persona_template_v2.json`
