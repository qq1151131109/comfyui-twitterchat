# 提示词调试功能使用指南

## 更新内容

现在 ComfyUI TwitterChat 插件支持在前端查看和调试提示词了！

### 新增/更新的节点

#### 1. **TweetGenerator** (已更新)
- **新增输出**：
  - `system_prompt`: 完整的系统提示词
  - `user_prompt`: 完整的用户提示词
- **原有输出**：
  - `tweet`: 生成的推文
  - `scene_hint`: 场景描述

现在你可以在前端直接看到生成推文时使用的完整提示词！

#### 2. **PromptBuilder** (新增，调试用)
- **分类**: TwitterChat/Debug
- **功能**: 只构建提示词，不调用 LLM
- **输出**：
  - `system_prompt`: 系统提示词
  - `user_prompt`: 用户提示词
  - `few_shot_examples`: Few-shot 示例文本

用于预览和调试提示词，无需消耗 API 额度。

#### 3. **PromptEditor** (新增，调试用)
- **分类**: TwitterChat/Debug
- **功能**: 在前端直接编辑提示词
- **输入**：
  - `system_prompt_input`: 从其他节点连接的系统提示词（可选）
  - `user_prompt_input`: 从其他节点连接的用户提示词（可选）
  - `system_prompt_override`: 手动编辑的系统提示词（多行文本框）⭐
  - `user_prompt_override`: 手动编辑的用户提示词（多行文本框）⭐
- **输出**：
  - `system_prompt`: 最终的系统提示词（优先使用 override）
  - `user_prompt`: 最终的用户提示词（优先使用 override）

用于在前端可视化编辑提示词，提供大文本框输入。

#### 4. **TweetGeneratorFromPrompt** (新增，调试用)
- **分类**: TwitterChat/Debug
- **功能**: 从手动编辑的提示词生成推文
- **输入**：
  - `system_prompt`: 自定义系统提示词（强制连接）
  - `user_prompt`: 自定义用户提示词（强制连接）
  - `few_shot_examples`: 可选的 Few-shot 示例
  - API 配置参数
- **输出**：
  - `tweet`: 生成的推文
  - `scene_hint`: 场景描述
  - `llm_response`: 完整的 LLM 原始响应

用于测试修改后的提示词效果。

---

## 使用场景

### 场景 1: 查看默认提示词（最简单）

**工作流**：
```
PersonaLoader → TweetGenerator
```

**操作**：
1. 连接 PersonaLoader 和 TweetGenerator
2. 运行工作流
3. 在 TweetGenerator 的输出中查看：
   - `tweet`: 生成的推文
   - `scene_hint`: 场景描述
   - `system_prompt`: 完整系统提示词 ⭐
   - `user_prompt`: 完整用户提示词 ⭐

**说明**：现在可以直接在前端看到提示词内容，方便分析和理解生成逻辑。

---

### 场景 2: 预览提示词（不消耗 API）

**工作流**：
```
PersonaLoader → PromptBuilder
```

**操作**：
1. 连接 PersonaLoader 到 PromptBuilder
2. 设置 topic_type（如"身材展示类"）
3. 运行工作流
4. 在前端查看输出的提示词

**好处**：
- 不调用 LLM API，不消耗额度
- 可以快速迭代测试不同的话题类型
- 查看 Few-shot 示例是否符合预期

---

### 场景 3: 在前端可视化编辑提示词（推荐！⭐）

**工作流**：
```
PersonaLoader → PromptBuilder → PromptEditor → TweetGeneratorFromPrompt
```

**操作步骤**：

1. **生成初始提示词**：
   - PersonaLoader → PromptBuilder
   - 运行查看生成的提示词

2. **连接到编辑器**：
   - PromptBuilder 的 `system_prompt` 连接到 PromptEditor 的 `system_prompt_input`
   - PromptBuilder 的 `user_prompt` 连接到 PromptEditor 的 `user_prompt_input`

3. **在前端直接编辑**：
   - 运行工作流后，PromptEditor 节点会显示两个大文本框
   - 在 `system_prompt_override` 文本框中直接编辑系统提示词
   - 在 `user_prompt_override` 文本框中直接编辑用户提示词
   - **提示**：留空则使用来自 PromptBuilder 的原始内容

4. **测试效果**：
   - PromptEditor 的输出连接到 TweetGeneratorFromPrompt
   - 配置 API 参数
   - 运行并查看生成结果

**优势**：
- 不需要复制粘贴！直接在节点上编辑
- 可以看到原始提示词（来自 input）
- 可以逐步修改（override）
- 支持多行文本，编辑舒适

---

### 场景 4: 调试和优化提示词（手动复制方式）

**工作流**：
```
PersonaLoader → PromptBuilder → [手动复制/编辑] → TweetGeneratorFromPrompt
```

**操作步骤**：

1. **生成初始提示词**：
   ```
   PersonaLoader → PromptBuilder
   ```
   - 运行后查看 `system_prompt` 和 `user_prompt`

2. **手动编辑提示词**：
   - 在前端复制 system_prompt 和 user_prompt 内容
   - 新建两个 "Primitive String" 节点（或使用文本编辑器）
   - 粘贴内容并根据需求修改：
     - 调整语气
     - 增加约束条件
     - 修改格式要求
     - 添加示例

3. **测试修改后的提示词**：
   - 连接编辑后的提示词到 TweetGeneratorFromPrompt
   - 填入 API 配置
   - 运行并查看生成结果

4. **对比和迭代**：
   - 查看 `llm_response` 查看原始输出
   - 对比修改前后的效果
   - 继续调整提示词直到满意

---

### 场景 5: 结合运营日历调试

**工作流**：
```
PersonaLoader → CalendarManager → PromptBuilder → PromptEditor → TweetGeneratorFromPrompt
              ↘ ContextGatherer ↗
```

**说明**：
- CalendarManager 提供今日计划
- ContextGatherer 提供日期/天气信息
- PromptBuilder 生成包含这些信息的提示词
- PromptEditor 允许你查看和修改提示词
- TweetGeneratorFromPrompt 生成最终结果

---

## 调试技巧

### 1. 查看 Few-shot 示例
PromptBuilder 会输出 `few_shot_examples`，可以检查：
- 示例数量是否正确
- 示例质量是否符合预期
- 是否需要在人设文件中添加更多示例

### 2. 对比不同话题类型
创建多个 PromptBuilder 节点，设置不同的 topic_type：
- 身材展示类
- 暧昧互动类
- 生活撒娇类
- 福利互动类

对比它们的提示词差异。

### 3. 测试自定义模板
在 PromptBuilder 或 TweetGenerator 中使用 `custom_user_prompt_template` 参数：

```
请以 {name} 的身份撰写推文。
{plan_guidance}
{kb_info}

你的自定义要求...
```

支持的变量：
- `{name}`: 人设名称
- `{topic}`: 话题
- `{plan_guidance}`: 运营计划（如果有）
- `{template_example}`: 模板示例
- `{kb_info}`: 知识库信息

### 4. 检查 LLM 原始输出
TweetGeneratorFromPrompt 输出 `llm_response`，包含：
- 完整的原始响应
- 可以看到 LLM 是否正确遵循了格式
- 可以检查是否有额外的输出被截断

---

## 常见问题

### Q: PromptBuilder 和 TweetGenerator 有什么区别？
A:
- **PromptBuilder**: 只生成提示词，不调用 LLM，免费，用于调试
- **TweetGenerator**: 生成提示词 + 调用 LLM 生成推文，消耗 API 额度

### Q: 如何在前端编辑提示词？
A: **推荐方式**（使用 PromptEditor）：
1. 使用 PromptBuilder 生成提示词
2. 连接到 PromptEditor 节点
3. 在 PromptEditor 的 `system_prompt_override` 和 `user_prompt_override` 文本框中直接编辑
4. 连接到 TweetGeneratorFromPrompt 生成

**备用方式**（手动复制）：
1. 使用 PromptBuilder 生成提示词
2. 复制输出内容
3. 创建 "Primitive String" 节点粘贴并编辑
4. 连接到 TweetGeneratorFromPrompt

### Q: 提示词太长，前端显示不全？
A:
1. 使用 "Show Text" 或 "Display Text" 节点（如果安装了相关插件）
2. 或者连接到 "Save Text" 节点保存到文件查看
3. 或者在 ComfyUI 后端日志中查看

### Q: 修改后的提示词不生效？
A:
- 检查是否使用了 TweetGeneratorFromPrompt（不是 TweetGenerator）
- 确认提示词节点正确连接
- 检查提示词内容格式是否正确

---

## 最佳实践

1. **先用 PromptBuilder 预览**：在消耗 API 前先看看提示词是否符合预期

2. **保存有效的提示词模板**：找到好用的提示词后，保存为 custom_user_prompt_template

3. **A/B 测试**：创建两个并行的生成分支，对比不同提示词的效果

4. **逐步优化**：
   - 第1轮：使用默认提示词，查看结果
   - 第2轮：微调提示词，对比效果
   - 第3轮：大幅修改，测试极端情况

5. **利用 Few-shot**：如果生成效果不好，先检查 Few-shot 示例是否充足

---

## 示例工作流配置

### 简单调试流程
```
[PersonaLoader]
    ↓
[PromptBuilder] → [显示/查看提示词]
```

### 可视化编辑流程（推荐！⭐）
```
[PersonaLoader] → [PromptBuilder] → [PromptEditor] → [TweetGeneratorFromPrompt]
                       ↓                  ↓                    ↓
                  [查看原始提示词]   [编辑提示词]         [生成推文]
```

### 完整调试流程（带日历和上下文）
```
[PersonaLoader] → [CalendarManager] → [PromptBuilder] → [PromptEditor]
              ↘ [ContextGatherer] ↗        ↓                  ↓
                                    [查看提示词]      [编辑提示词]
                                                           ↓
                                              [TweetGeneratorFromPrompt]
                                                    ↓         ↓
                                                 [tweet]  [scene_hint]
```

### 生产环境流程（不需要编辑）
```
[PersonaLoader] → [CalendarManager] → [TweetGenerator]
              ↘ [ContextGatherer] ↗        ↓
                                    [tweet + 提示词输出]
```

---

**提示**：重启 ComfyUI 后，新节点会出现在 TwitterChat 和 TwitterChat/Debug 分类下！
