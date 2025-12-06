# 人设生成器使用指南

## 📖 简介

`persona_generator.py` 是一个自动化工具，使用大语言模型(LLM)生成符合Character Card V2规范的完整人设文件。

## 🚀 快速开始

### 1. 交互式模式（推荐新手）

```bash
cd custom_nodes/comfyui-twitterchat
python persona_generator.py --interactive
```

按照提示输入角色信息即可。

### 2. 命令行模式

```bash
python persona_generator.py --name "Emily" --type "fitness-girl" --age 24
```

### 3. 完整参数示例

```bash
python persona_generator.py \
  --name "Sarah" \
  --age 22 \
  --type "college-student" \
  --location "New York" \
  --personality "outgoing, artistic, funny" \
  --occupation "art student" \
  --interests "painting, coffee, indie music" \
  --style "bohemian, artsy" \
  --nsfw soft \
  --output sarah_artist.json
```

## 🎯 参数说明

### 必需参数（命令行模式）

| 参数 | 说明 | 示例 |
|------|------|------|
| `--name` | 角色名字 | `--name "Emily"` |

### 可选参数

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--age` | 年龄 | 23 | `--age 24` |
| `--type` | 人设类型 | college-student | `--type "fitness-girl"` |
| `--location` | 地点 | United States | `--location "Los Angeles"` |
| `--personality` | 性格特征 | friendly, creative | `--personality "bubbly, confident"` |
| `--occupation` | 职业 | - | `--occupation "yoga instructor"` |
| `--interests` | 兴趣爱好 | - | `--interests "fitness, fashion"` |
| `--style` | 风格美学 | - | `--style "athletic, feminine"` |
| `--nsfw` | 内容尺度 | soft | `none/soft/medium/explicit` |
| `--language` | 语言 | en | `en/zh` |
| `--output` | 输出文件名 | 自动生成 | `--output my_persona.json` |

### API配置参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--api-key` | API密钥 | 从环境变量读取 |
| `--api-base` | API基础URL | https://www.dmxapi.cn/v1 |
| `--model` | 模型名称 | grok-4-fast |

## 🔧 配置API密钥

### 方法1: 环境变量（推荐）

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_API_BASE="https://www.dmxapi.cn/v1"
```

或创建 `.env` 文件：

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥
```

### 方法2: 命令行参数

```bash
python persona_generator.py \
  --api-key "your-api-key" \
  --api-base "https://api.example.com/v1" \
  --name "Emily"
```

### 方法3: 使用脚本内置默认值

脚本内置了默认API配置，可以直接使用（但不推荐生产环境）。

## 📝 人设类型建议

以下是常见的人设类型供参考：

### 👩‍🎓 校园风格
- `college-student` - 大学生
- `sorority-girl` - 姐妹会女生
- `nerdy-student` - 学霸型
- `art-student` - 艺术生

### 💪 运动健身
- `fitness-girl` - 健身女孩
- `yoga-instructor` - 瑜伽教练
- `athlete` - 运动员
- `gym-enthusiast` - 健身爱好者

### 🎨 艺术创意
- `artist` - 艺术家
- `photographer` - 摄影师
- `influencer` - 网红
- `content-creator` - 内容创作者

### 💼 职业风格
- `young-professional` - 年轻职场人
- `entrepreneur` - 创业者
- `office-worker` - 上班族

### 🌟 特殊风格
- `goth-girl` - 哥特风
- `egirl` - 电子风
- `cottagecore` - 田园风
- `coquette` - 甜心风
- `brat` - 叛逆小恶魔

## 🎭 NSFW等级说明

| 等级 | 说明 | 适用场景 |
|------|------|----------|
| `none` | 无成人内容 | 纯净日常分享 |
| `soft` | 轻度暗示 | 略带性感的自拍 |
| `medium` | 中度 | 内衣展示、挑逗性内容 |
| `explicit` | 明确 | 露骨成人内容 |

## 📦 输出文件

生成的文件会保存在：
```
custom_nodes/comfyui-twitterchat/personas/
```

文件命名格式：
- 自动生成：`{name}_{timestamp}.json`
- 手动指定：使用 `--output` 参数

## 🔍 生成内容包含

完整的人设JSON包括：

- ✅ 基本信息（姓名、年龄、生日、星座）
- ✅ 地理位置（城市、时区）
- ✅ 背景故事（教育、职业、家庭）
- ✅ 性格特征（详细描述）
- ✅ 日常作息（时间表）
- ✅ 兴趣爱好
- ✅ 穿搭风格
- ✅ 语言风格（口头禅、emoji使用）
- ✅ Twitter人设（账号信息、推文示例8-12条）
- ✅ 视觉描述（用于图像生成）

## 💡 使用技巧

### 1. 生成多样化内容

```bash
# 生成不同风格的人设
python persona_generator.py --name "Luna" --type "goth-girl" --style "dark, edgy"
python persona_generator.py --name "Sophia" --type "coquette" --style "soft, feminine"
python persona_generator.py --name "Alex" --type "fitness-girl" --interests "crossfit, nutrition"
```

### 2. 批量生成

创建 `batch_generate.sh`：

```bash
#!/bin/bash
names=("Emily" "Sarah" "Luna" "Sophia" "Chloe")
types=("fitness-girl" "artist" "goth-girl" "coquette" "college-student")

for i in "${!names[@]}"; do
  python persona_generator.py \
    --name "${names[$i]}" \
    --type "${types[$i]}" \
    --output "${names[$i],,}.json"
done
```

### 3. 自定义高级人设

对于复杂需求，可以：
1. 先用脚本生成基础版本
2. 手动编辑JSON文件细化细节
3. 添加自定义字段（如LoRA配置）

## 🐛 故障排查

### 问题1: API调用失败

**症状**: `API调用失败: 401 Unauthorized`

**解决**:
```bash
# 检查API密钥是否正确
echo $OPENAI_API_KEY

# 或使用命令行参数指定
python persona_generator.py --api-key "正确的密钥" --name "Test"
```

### 问题2: JSON解析错误

**症状**: `JSON解析失败`

**原因**: LLM输出格式不标准

**解决**:
- 重新运行命令（LLM输出有随机性）
- 尝试降低 `temperature` 参数
- 换用更稳定的模型（如GPT-4）

### 问题3: 生成内容质量不佳

**解决**:
- 提供更详细的参数（occupation, interests, style）
- 使用更强大的模型（gpt-4-turbo, claude-3-opus）
- 多生成几次，选择最好的

## 🔗 在ComfyUI中使用

生成人设后，在PersonaLoader节点中：

1. 选择模式：`json_file`
2. 输入路径：`custom_nodes/comfyui-twitterchat/personas/your_persona.json`
3. 运行工作流

## 📚 示例集合

### 示例1: 健身博主

```bash
python persona_generator.py \
  --name "Kayla" \
  --age 25 \
  --type "fitness-girl" \
  --location "Miami, Florida" \
  --personality "energetic, motivational, confident" \
  --occupation "fitness coach and influencer" \
  --interests "weightlifting, meal prep, beach workouts" \
  --style "athletic-feminine, activewear aesthetic" \
  --nsfw medium \
  --output kayla_fitness.json
```

### 示例2: 艺术系学生

```bash
python persona_generator.py \
  --name "Luna" \
  --age 21 \
  --type "art-student" \
  --location "Brooklyn, New York" \
  --personality "creative, introverted, dreamy" \
  --occupation "art student at Pratt Institute" \
  --interests "oil painting, vintage fashion, indie films" \
  --style "bohemian, artistic, vintage" \
  --nsfw soft \
  --output luna_artist.json
```

### 示例3: 加州女孩

```bash
python persona_generator.py \
  --name "Mia" \
  --age 23 \
  --type "california-girl" \
  --location "Santa Monica, California" \
  --personality "bubbly, flirty, carefree" \
  --occupation "lifestyle influencer" \
  --interests "surfing, beach volleyball, iced coffee" \
  --style "california casual, beachy vibes" \
  --nsfw medium \
  --output mia_cali.json
```

## 🤝 贡献

如果你改进了提示词模板或添加了新功能，欢迎分享！

## 📄 许可

本脚本为开源工具，可自由使用和修改。

---

**提示**: 生成高质量人设的关键是提供详细、具体的参数。不要害怕多试几次！
