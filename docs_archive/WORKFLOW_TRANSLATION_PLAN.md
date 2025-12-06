# 🌐 工作流中文翻译任务清单

## 概览

文件: `/home/ubuntu/shenglin/ComfyUI/workflow/自动生成推文-120402.json`
总中文字符: 8266个
中文区域: 8处

---

## 📋 翻译任务列表

### ✅ 任务1: 第576行 - 示例人设描述（可选）
**位置**: widgets_values
**内容**: "你是小猫（Kitten），23岁..."
**操作**: 这是工作流中的示例/占位符，实际使用时会被真实人设替换，可以保留或删除

---

### ✅ 任务2: 第709行 - 日历JSON示例
**位置**: calendar示例
**内容**: `"persona_name": "小猫 (Kitten)"`
**操作**: 替换为 `"Kitten (Sub)"`

---

### ✅ 任务3: 第837行 - 用户提示词
**内容**: "请以 小猫 (Kitten) 的身份撰写..."
**翻译**:
```
Write a tweet in the voice of Kitten about "Weekend Edging Practice".

Today's plan:
- Content type: Edging tease
- Theme: Weekend self-control edging
- Direction: Describe solo edging practice, express desire for Master's permission, playfully admit naughty impulses, encourage followers to share control techniques
- Keywords: edging, teasing, self-control
- Suggested scene: Kitten on bed, blindfolded, hands...
```

---

### 🔥 任务4: 第1114行 - 示例推文（中文）
**内容**: "周五前的小猫忍不住了..."
**翻译**:
```
Kitten couldn't resist before Friday... lying in bed blindfolded, fingers slowly teasing myself, stopping right at the edge, body trembling and wanting to break so badly but have to wait for Master's permission🥺 Naughty impulse almost won, hmph~ #edging #submissive #BDSM
```

---

### ✅ 任务5: 第1157行 - LoRA路径
**内容**: "z-image/樱桃在不在.safetensors"
**操作**: 这是示例LoRA路径，实际使用时会被替换，保留即可

---

### ✅ 任务6: 第1221行 - UI标题
**内容**: "图片"
**翻译**: "Image"

---

### 🔥🔥🔥 任务7: 第1276行 - **核心提示词模板**（最重要！）
**这是TweetGenerator的system_prompt模板，包含所有生成指导**

**内容**: 长达数千字的中文指导，包括：
- 【今日背景】
- 【视觉人格档案】
- 【推文风格指导】
- 【场景描述标准】
- 【真实感核心原则】
等等

**翻译策略**: 需要完整翻译整个模板，保持所有格式、emoji、结构

---

### ✅ 任务8: 第1381行 - 人设JSON示例
**内容**: `"备注": "BDSM sub人设..."`
**翻译**: `"note": "BDSM sub persona..."`

---

## 🎯 优先级

### P0 - 必须翻译（核心功能）
- ✅ **任务7**: 第1276行 system_prompt模板 ← 最关键！

### P1 - 建议翻译（用户可见）
- ✅ 任务3: 第837行用户提示词
- ✅ 任务4: 第1114行示例推文
- ✅ 任务6: 第1221行 UI标题

### P2 - 可选翻译（示例/占位）
- ⏩ 任务1: 第576行示例人设
- ⏩ 任务2: 第709行日历示例
- ⏩ 任务5: 第1157行 LoRA路径
- ⏩ 任务8: 第1381行人设JSON

---

## 🚀 执行计划

### 第一步: 翻译核心提示词模板（任务7）
这是最重要且工作量最大的任务。包含：
- 人设描述模板
- 视觉人格档案格式
- 推文风格指导
- 场景描述标准
- 真实感核心原则
- 技术要求

需要：
1. 提取完整的中文模板
2. 逐段翻译成英文
3. 保持所有标记符号（【】⚠️✅❌）
4. 保持格式和结构

### 第二步: 翻译用户可见内容（任务3,4,6）
- 用户提示词
- 示例推文
- UI标题

### 第三步: 更新示例内容（任务1,2,5,8）
- 替换占位符为英文
- 或直接删除（如果只是示例）

---

## 📝 验证清单

完成后需要验证：
- [ ] 工作流文件可以正常加载
- [ ] 没有JSON语法错误
- [ ] 所有中文字符已翻译或删除
- [ ] 特殊标记符号保留（emoji、【】等）
- [ ] 格式和结构完整
- [ ] 在ComfyUI中测试运行

---

## 💾 文件备份

原文件: `/home/ubuntu/shenglin/ComfyUI/workflow/自动生成推文-120402.json`
备份: `/home/ubuntu/shenglin/ComfyUI/workflow/自动生成推文-120402-backup.json` ✅
新文件: `/home/ubuntu/shenglin/ComfyUI/workflow/auto-tweet-generation-en-US.json`

---

## 📌 注意事项

1. **保持JSON格式**: 翻译时注意引号转义和JSON格式
2. **保留技术术语**: LoRA, BDSM, submissive等保持英文
3. **保留emoji**: 所有emoji原样保留
4. **保留标记符号**: 【】⚠️✅❌等特殊符号保留
5. **测试验证**: 翻译后必须在ComfyUI中测试

---

**准备开始翻译任务7（核心提示词模板）**
