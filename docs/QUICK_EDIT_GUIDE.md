# 快速开始：提示词编辑功能

## 最简单的使用方式 ⭐

### 工作流
```
PersonaLoader → PromptBuilder → PromptEditor → TweetGeneratorFromPrompt
```

### 操作步骤

1. **添加节点**（在 ComfyUI 前端）：
   - 添加 `Load Persona` 节点
   - 添加 `Build Prompts (Debug)` 节点
   - 添加 `Edit Prompts` 节点
   - 添加 `Generate Tweet From Prompts (Debug)` 节点

2. **连接节点**：
   ```
   Load Persona.persona → Build Prompts.persona
   Build Prompts.system_prompt → Edit Prompts.system_prompt_input
   Build Prompts.user_prompt → Edit Prompts.user_prompt_input
   Edit Prompts.system_prompt → Generate Tweet From Prompts.system_prompt
   Edit Prompts.user_prompt → Generate Tweet From Prompts.user_prompt
   ```

3. **配置参数**：
   - `Load Persona`: 填入人设文件路径（如 `examples/fitness_girl_emily.json`）
   - `Build Prompts`: 选择 topic_type（如 "身材展示类"）
   - `Generate Tweet From Prompts`: 填入 API key、api_base、model

4. **第一次运行**（查看默认提示词）：
   - 点击 "Queue Prompt"
   - 查看 `Edit Prompts` 节点的输出，这是默认生成的提示词

5. **编辑提示词**：
   - 在 `Edit Prompts` 节点的两个大文本框中编辑：
     - `system_prompt_override`: 编辑系统提示词
     - `user_prompt_override`: 编辑用户提示词
   - **提示**：文本框留空则使用默认值

6. **重新运行**：
   - 点击 "Queue Prompt"
   - 查看使用修改后提示词生成的推文

---

## 示例：修改提示词以获得更具体的输出

### 场景：想让推文更简短、更有互动性

**原始 user_prompt**（由 PromptBuilder 自动生成）：
```
请以 Emily Carter 的身份撰写一条推文，并描述配图场景。

内容类型: 身材展示类
...
字数 60-150 字
```

**修改后的 user_prompt**（在 PromptEditor 中编辑）：
```
请以 Emily Carter 的身份撰写一条推文，并描述配图场景。

内容类型: 身材展示类
...
字数 40-80 字（更简短！）
必须包含一个提问，引导粉丝回复
```

**效果对比**：
- 修改前：较长的描述性推文
- 修改后：简短、互动性强的推文

---

## 快速技巧

### 技巧 1：只编辑 user_prompt
如果只想调整内容要求，只需编辑 `user_prompt_override`，`system_prompt_override` 留空即可。

### 技巧 2：保存常用修改
找到好用的提示词后，复制保存到文本文件，下次直接粘贴使用。

### 技巧 3：A/B 测试
创建两个并行分支：
```
PromptBuilder → PromptEditor A → TweetGeneratorFromPrompt A
              ↘ PromptEditor B → TweetGeneratorFromPrompt B
```
在 A 中使用默认提示词，在 B 中使用修改后的提示词，对比效果。

### 技巧 4：渐进式调整
- 第1次运行：查看默认提示词和结果
- 第2次运行：小幅修改（如改字数限制）
- 第3次运行：中等修改（如改语气）
- 第4次运行：大幅修改（如完全重写 user_prompt）

---

## 常见修改示例

### 1. 改变推文长度
在 user_prompt 中找到：
```
字数 60-150 字
```
修改为：
```
字数 30-60 字  # 更短
字数 100-200 字  # 更长
```

### 2. 增加特定要求
在 user_prompt 末尾添加：
```
额外要求：
- 必须提到今天的训练项目
- 必须使用至少 3 个 emoji
- 必须包含一个问题
```

### 3. 改变语气
在 system_prompt 中修改：
```
你的推文目标是吸引男性粉丝，内容风格要求:
- 适度性感暧昧，但不要太露骨
```
改为：
```
你的推文目标是吸引健身爱好者，内容风格要求:
- 专业、激励人心，分享健身技巧
```

### 4. 指定场景
在 user_prompt 中添加：
```
场景必须是：gym, wearing pink sports bra, doing squats
```

---

## 完整示例

**目标**：生成一条关于早餐的简短推文

**1. Load Persona**:
```
persona_file: examples/fitness_girl_emily.json
```

**2. Build Prompts**:
```
topic_type: 生活撒娇类
```

**3. Edit Prompts**:

在 `user_prompt_override` 中输入：
```
请以 Emily Carter 的身份撰写一条关于早餐的推文。

要求：
1. 字数 30-50 字
2. 提到具体吃了什么
3. 使用 1-2 个食物 emoji
4. 语气轻松可爱
5. 添加 1 个相关标签

输出格式：
TWEET: [推文内容]
SCENE: [场景描述，如: kitchen, casual clothes, breakfast on table]
```

**4. Generate Tweet From Prompts**:
```
api_key: your-api-key
api_base: https://api.openai.com/v1
model: gpt-4
temperature: 0.85
```

**5. 运行并查看结果！**

---

## 故障排除

### 问题：文本框太小，编辑不方便
- ComfyUI 默认的多行文本框会根据内容自动扩展
- 可以手动拖动节点边框调整大小
- 或者使用外部文本编辑器编辑后粘贴

### 问题：修改后没有效果
- 确认使用的是 `TweetGeneratorFromPrompt`（不是 `TweetGenerator`）
- 确认提示词已正确连接
- 确认文本框中有内容（不是空的）

### 问题：找不到新节点
- 重启 ComfyUI
- 检查节点分类：`TwitterChat` 和 `TwitterChat/Debug`
- 检查终端是否有导入错误

---

**祝使用愉快！有问题请查看完整文档：`PROMPT_DEBUGGING_GUIDE.md`**
