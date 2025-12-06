# 更新说明 - 提示词可视化调试功能

## 版本：v1.1.0
**更新日期**: 2025-12-01

---

## 🎉 新功能

### 1. TweetGenerator 节点增强
**文件**: `nodes/tweet_generator.py`

**新增输出**：
- `system_prompt` (STRING): 完整的系统提示词
- `user_prompt` (STRING): 完整的用户提示词

**说明**：现在你可以直接在前端看到生成推文时使用的完整提示词，无需查看代码！

---

### 2. 新节点：PromptBuilder（提示词构建器）
**文件**: `nodes/prompt_builder.py`
**分类**: TwitterChat/Debug

**功能**：
- 构建提示词但不调用 LLM
- 免费预览提示词内容
- 用于调试和分析

**输出**：
- `system_prompt`: 系统提示词
- `user_prompt`: 用户提示词
- `few_shot_examples`: Few-shot 示例文本

**使用场景**：
- 想看看提示词长什么样
- 不想浪费 API 额度
- 需要快速测试不同话题类型的提示词

---

### 3. 新节点：PromptEditor（提示词编辑器）⭐
**文件**: `nodes/prompt_editor.py`
**分类**: TwitterChat/Debug

**功能**：
- 在前端提供大文本框直接编辑提示词
- 支持连接输入（自动填充）
- 支持手动覆盖（override）

**输入**：
- `system_prompt_input`: 从其他节点连接（可选）
- `user_prompt_input`: 从其他节点连接（可选）
- `system_prompt_override`: 手动编辑框（优先）⭐
- `user_prompt_override`: 手动编辑框（优先）⭐

**输出**：
- `system_prompt`: 最终提示词（优先使用 override）
- `user_prompt`: 最终提示词（优先使用 override）

**使用场景**：
- 需要修改提示词但不想复制粘贴
- 需要可视化编辑界面
- 需要保留原始提示词的同时进行修改

---

### 4. 新节点：TweetGeneratorFromPrompt（从提示词生成推文）
**文件**: `nodes/tweet_generator_from_prompt.py`
**分类**: TwitterChat/Debug

**功能**：
- 接收自定义提示词
- 调用 LLM 生成推文
- 返回完整的 LLM 原始响应

**输入**：
- `system_prompt`: 自定义系统提示词（强制连接）
- `user_prompt`: 自定义用户提示词（强制连接）
- `few_shot_examples`: Few-shot 示例（可选）
- API 配置参数

**输出**：
- `tweet`: 生成的推文
- `scene_hint`: 场景描述
- `llm_response`: 完整 LLM 响应（用于调试）⭐

**使用场景**：
- 测试修改后的提示词效果
- 调试提示词格式
- 对比不同提示词的输出

---

## 📖 新文档

### 1. 提示词调试完整指南
**文件**: `docs/PROMPT_DEBUGGING_GUIDE.md`

包含：
- 所有节点的详细说明
- 5个使用场景示例
- 调试技巧
- 常见问题解答
- 示例工作流配置

### 2. 快速开始指南
**文件**: `docs/QUICK_EDIT_GUIDE.md`

包含：
- 最简单的使用方式
- 分步操作说明
- 修改示例
- 快速技巧
- 故障排除

---

## 🔄 推荐工作流

### 查看提示词（生产环境）
```
PersonaLoader → TweetGenerator
```
现在可以直接看到 system_prompt 和 user_prompt 输出！

### 预览提示词（不消耗 API）
```
PersonaLoader → PromptBuilder
```
免费查看提示词内容。

### 编辑和测试提示词（推荐！⭐）
```
PersonaLoader → PromptBuilder → PromptEditor → TweetGeneratorFromPrompt
```
在前端可视化编辑，实时测试效果。

---

## 🚀 如何使用

### 方式 1: 快速查看（无需编辑）
1. 使用现有的 `TweetGenerator` 节点
2. 运行后查看新增的 `system_prompt` 和 `user_prompt` 输出
3. 了解提示词内容，优化人设文件

### 方式 2: 预览提示词（免费）
1. 添加 `PromptBuilder` 节点
2. 连接 `PersonaLoader`
3. 设置 topic_type
4. 运行查看提示词

### 方式 3: 可视化编辑（推荐！）
1. 添加完整工作流：
   ```
   PersonaLoader → PromptBuilder → PromptEditor → TweetGeneratorFromPrompt
   ```
2. 运行后在 `PromptEditor` 的文本框中编辑
3. 重新运行查看效果

---

## 📝 重要提示

### 兼容性
- 所有现有工作流仍然正常工作
- `TweetGenerator` 增加了输出，但不影响原有功能
- 新节点都在 `TwitterChat/Debug` 分类下

### 性能
- `PromptBuilder` 不调用 LLM，速度很快
- `PromptEditor` 只做字符串处理，无性能影响
- `TweetGeneratorFromPrompt` 与 `TweetGenerator` 性能相同

### 使用建议
1. **开发调试阶段**：使用 PromptBuilder + PromptEditor 组合
2. **找到最佳提示词后**：保存到 custom_user_prompt_template 参数
3. **生产环境**：使用 TweetGenerator（现在可以查看提示词了）

---

## 🔧 更新方法

### 自动更新
```bash
cd custom_nodes/comfyui-twitterchat
git pull
```

### 手动更新
如果你手动修改过文件，需要：
1. 备份你的修改
2. 更新文件
3. 重启 ComfyUI

### 重启 ComfyUI
更新后必须重启 ComfyUI 才能看到新节点：
```bash
# 停止 ComfyUI
Ctrl+C

# 重新启动
python main.py
```

---

## 🐛 已知问题

### 文本框显示
- ComfyUI 的多行文本框会根据内容自动调整大小
- 如果内容很长，可能需要手动调整节点大小
- 建议使用外部编辑器编辑长提示词后粘贴

### 相对导入
- 新节点使用相对导入，在 ComfyUI 环境中正常工作
- 单独运行 Python 文件会报错（这是正常的）

---

## 💡 示例：修改提示词让推文更简短

**步骤**：

1. 创建工作流：
   ```
   Load Persona → Build Prompts → Edit Prompts → Generate Tweet From Prompts
   ```

2. 第一次运行，查看默认输出

3. 在 `Edit Prompts` 的 `user_prompt_override` 中修改：
   ```
   找到：字数 60-150 字
   改为：字数 30-60 字
   ```

4. 重新运行，对比效果

---

## 📚 相关文档

- **完整调试指南**: `docs/PROMPT_DEBUGGING_GUIDE.md`
- **快速开始**: `docs/QUICK_EDIT_GUIDE.md`
- **原始 README**: `README.md`
- **快速开始**: `QUICKSTART.md`

---

## 🙏 反馈

如果遇到问题或有建议，请：
1. 检查文档：`docs/PROMPT_DEBUGGING_GUIDE.md`
2. 查看示例：`docs/QUICK_EDIT_GUIDE.md`
3. 提交 Issue（如果是 GitHub 仓库）

---

**祝使用愉快！现在你可以完全掌控提示词了！🎉**
