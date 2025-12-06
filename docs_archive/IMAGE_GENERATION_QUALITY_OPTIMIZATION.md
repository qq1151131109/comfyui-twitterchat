# 图像生成质量优化方案

## 📋 问题梳理

### 当前工作流

```
CalendarManager (生成 suggested_scene)
    ↓
TweetGenerator (生成 tweet + scene_hint)
    ↓
ImagePromptBuilder (组装完整 prompt)
    ↓
LoRA Loader + 文生图模型
    ↓
生成的图像
```

### 🚨 主要问题分类

#### 1. **人物一致性问题**（核心问题）

**问题表现**:
- ❌ 出现多个人物（2人、3人、群体场景）
- ❌ 人物角度/姿态难以控制（侧脸、背影、远景）
- ❌ 人物特征不稳定（发型、服装、五官变化）
- ❌ LoRA 触发失效或强度不足

**根本原因**:
- LLM 生成的 scene_hint 中包含多人场景描述
- 缺乏对"单人"、"solo"、"1girl"等关键词的强制约束
- LoRA 权重不足以压制基础模型的多样性
- 负面提示词（negative prompt）缺失或不够强
- 场景描述过于复杂，模型注意力分散

**示例问题场景**:
```
❌ 问题场景: "with grandfather in tea garden"
   → 会生成 2 个人

❌ 问题场景: "friends gathering at cafe"
   → 会生成多人

❌ 问题场景: "group photo, family reunion"
   → 会生成群体
```

---

#### 2. **场景描述质量问题**

**问题表现**:
- ❌ 场景过于抽象或模糊
- ❌ 场景描述词汇不够具体
- ❌ 缺少关键视觉元素（光线、角度、构图）
- ❌ 与人设特征不匹配

**示例**:
```
❌ 不好: "happy moment"
✅ 好: "solo, 1girl, sitting on chair, traditional tea room, afternoon sunlight through window, smiling, looking at camera"

❌ 不好: "daily life"
✅ 好: "solo, 1girl, wearing hanfu, outdoor tea garden, morning mist, holding tea cup, front view"
```

---

#### 3. **提示词组织问题**

**问题表现**:
- ❌ 关键词位置不合理（重要词在后面）
- ❌ 质量词和 LoRA 触发词被场景词覆盖
- ❌ 缺少负面提示词（negative prompt）
- ❌ 权重标记使用不当

**当前 Prompt 结构**:
```
[LoRA触发词], [质量词], [scene_hint], [后置提示词]
```

**问题**:
- scene_hint 如果太长，会稀释前面的权重
- 没有使用 `(keyword:1.2)` 等权重标记强化关键词

---

#### 4. **日历计划场景规划问题**

**问题表现**:
- ❌ CalendarManager 生成的 `suggested_scene` 包含多人场景
- ❌ 场景描述过于开放，LLM 自由发挥过多
- ❌ 没有场景类型白名单/黑名单机制

**示例问题**:
```json
// ❌ 问题运营日历
{
  "suggested_scene": "having dinner with friends"  // 会生成多人
}

// ❌ 问题运营日历
{
  "suggested_scene": "group activity"  // 不明确
}
```

---

#### 5. **LoRA 配置问题**

**问题表现**:
- ❌ LoRA 权重过低（<0.6），人物特征不稳定
- ❌ LoRA 触发词缺失或错误
- ❌ 基础模型与 LoRA 不匹配

---

#### 6. **生成参数问题**

**问题表现**:
- ❌ CFG Scale 过低或过高
- ❌ 采样步数不足
- ❌ 分辨率不合适（过大导致细节失控）
- ❌ 种子固定导致多样性不足

---

## 🎯 优化方案

### 方案 A: 多层次约束（推荐 ⭐）

在多个环节同时约束，确保生成质量。

#### A1. 运营日历生成优化

**修改位置**: `utils/calendar_manager.py` 的 `generate_calendar_prompt()`

**优化内容**:
1. 添加场景类型约束
2. 强制单人场景要求
3. 提供场景模板

**实现代码**:
```python
# 添加到 prompt 中
prompt += """

【场景描述规范】（非常重要）
1. **必须是单人场景**：
   - ✅ 允许：独自在茶园、一个人看书、自己泡茶、独自散步
   - ❌ 禁止：和爷爷、和朋友、家人聚会、合影、多人场景

2. **场景描述格式**（英文）：
   - 必须包含：solo, 1girl
   - 构图：front view / side view / upper body / full body
   - 地点：具体场所（tea garden / traditional room / courtyard）
   - 姿态：sitting / standing / walking / holding [object]
   - 氛围：morning sunlight / afternoon light / evening glow
   - 服装：wearing [outfit]

3. **场景模板参考**：
   - 日常生活：solo, 1girl, upper body, traditional courtyard, wearing casual dress, morning sunlight, smiling, looking at camera
   - 传统服装：solo, 1girl, full body, wearing hanfu, outdoor tea garden, afternoon light, standing, front view
   - 工作场景：solo, 1girl, sitting at tea table, indoor traditional room, making tea, focused expression, side view
   - 休闲时刻：solo, 1girl, reading book, under tree, tea garden background, peaceful atmosphere, soft lighting

4. **严格禁止的场景**：
   - 任何包含"爷爷"、"朋友"、"家人"、"客人"的场景
   - 任何"合影"、"聚会"、"活动"等多人场景
   - 任何"背影"、"远景"、"看不清脸"的场景
"""
```

---

#### A2. 推文生成场景约束

**修改位置**: `nodes/tweet_generator.py` 的 `_build_user_prompt()`

**优化内容**:
1. 强化场景描述要求
2. 添加场景检查清单

**实现代码**:
```python
# 修改场景描述要求部分
场景描述要求:
- **强制要求**：必须以 "solo, 1girl" 开头
- 用英文描述，简洁明了（5-15个词组）
- 必须包含：构图角度（front view/side view/upper body）
- 必须包含：地点描述（具体地点，不要用 "somewhere"）
- 可选包含：服装、姿态、光线、氛围
- **严格禁止**：不要出现任何其他人物（grandfather/friend/people/crowd/group）
- **严格禁止**：不要出现背影、远景、看不清脸的描述

正确示例：
✅ solo, 1girl, upper body, front view, traditional tea room, wearing qipao, afternoon sunlight, smiling, looking at camera
✅ solo, 1girl, full body, standing in tea garden, wearing hanfu, morning mist, holding tea cup
✅ solo, 1girl, sitting on chair, traditional courtyard, side view, reading book, peaceful atmosphere

错误示例（禁止）：
❌ with grandfather in tea garden  （有其他人）
❌ back view, walking away  （背影，看不清脸）
❌ distant shot, in the crowd  （远景，不清晰）
❌ group photo  （多人）
```

---

#### A3. 图像提示词优化

**修改位置**: `nodes/image_prompt_builder.py`

**优化内容**:
1. 自动添加单人约束词
2. 使用权重标记强化关键词
3. 自动生成负面提示词

**实现思路**:
```python
class ImagePromptBuilder:
    def build(self, scene_hint, persona, prepend_prompt="", append_prompt="", auto_lora=True):
        """构建图像提示词（优化版）"""

        # 1. 强制单人约束（最高权重）
        solo_constraint = "(solo:1.4), (1girl:1.3), (single person:1.2)"

        # 2. LoRA 触发词（高权重）
        lora_triggers = self._extract_lora_triggers(persona)
        if lora_triggers:
            lora_triggers = f"({lora_triggers}:1.2)"

        # 3. 质量词
        quality = prepend_prompt or "masterpiece, best quality, 8k uhd, professional photography"

        # 4. 场景描述（自动检查和修复）
        scene_hint = self._sanitize_scene_hint(scene_hint)

        # 5. 构图约束
        composition = "front view, upper body, looking at camera, clear face, detailed face"

        # 6. 人物特征（从人设提取）
        character_features = self._extract_character_features(persona)

        # 组装
        positive_parts = [
            solo_constraint,
            lora_triggers,
            quality,
            scene_hint,
            composition,
            character_features,
            append_prompt
        ]

        positive_prompt = ", ".join(filter(None, positive_parts))

        # 7. 生成负面提示词
        negative_prompt = self._build_negative_prompt()

        return (positive_prompt, negative_prompt)

    def _sanitize_scene_hint(self, scene_hint: str) -> str:
        """清理和修复场景描述"""
        # 检查是否包含多人关键词
        multi_person_keywords = [
            "grandfather", "grandpa", "爷爷",
            "friend", "friends", "朋友",
            "people", "crowd", "group", "群体",
            "family", "家人",
            "together", "with", "和",
            "2girls", "3girls", "multiple",
            "couple", "伴侣"
        ]

        scene_lower = scene_hint.lower()
        for keyword in multi_person_keywords:
            if keyword in scene_lower:
                print(f"[警告] 场景描述包含多人关键词: {keyword}")
                # 移除这些词
                scene_hint = scene_hint.replace(keyword, "")

        # 确保以 solo, 1girl 开头
        if not scene_hint.lower().startswith("solo"):
            scene_hint = "solo, 1girl, " + scene_hint

        # 移除背影相关描述
        back_view_keywords = ["back view", "背影", "from behind", "rear view"]
        for keyword in back_view_keywords:
            if keyword in scene_lower:
                scene_hint = scene_hint.replace(keyword, "front view")

        return scene_hint.strip()

    def _build_negative_prompt(self) -> str:
        """生成负面提示词"""
        negative = """
        multiple people, 2girls, 3girls, group, crowd,
        other person, grandfather, friend, family,
        back view, rear view, from behind, distant shot,
        blurry face, unclear face, face out of frame,
        multiple faces, extra limbs, deformed,
        nsfw, nude, sexy, revealing,
        low quality, worst quality, lowres, bad anatomy,
        watermark, signature, text, logo
        """
        return ", ".join([x.strip() for x in negative.split(",") if x.strip()])

    def _extract_character_features(self, persona: dict) -> str:
        """从人设提取人物特征"""
        # 可以从人设的 appearance 字段提取
        # 例如：long black hair, brown eyes, gentle smile
        # 这里返回空字符串，可根据需要扩展
        return ""
```

**注意**:
- 这个改动会改变节点的返回值（从1个变成2个输出）
- 需要同时更新节点注册信息

---

#### A4. 日历生成系统提示词约束

**修改位置**: `utils/calendar_manager.py`

**在 LLM system prompt 中添加**:
```python
messages = [
    {
        "role": "system",
        "content": """你是专业的社交媒体运营专家，擅长规划内容日历。

重要要求：
1. 必须输出有效的 JSON 格式
2. 所有字符串必须使用英文双引号 "
3. suggested_scene 必须是单人场景，绝对不允许出现其他人物
4. suggested_scene 必须以 "solo, 1girl" 开头
5. suggested_scene 必须包含具体的构图、地点、姿态描述
6. 严格禁止在 suggested_scene 中出现：grandfather/friend/people/group/crowd/together/with 等多人关键词
7. 严格禁止背影、远景等看不清脸的描述

场景描述示例：
✅ "solo, 1girl, upper body, front view, traditional tea room, wearing qipao, afternoon sunlight, smiling"
✅ "solo, 1girl, full body, standing in tea garden, wearing hanfu, morning light, holding tea cup"
❌ "with grandfather picking tea"  （多人场景，禁止）
❌ "back view in tea garden"  （背影，禁止）
"""
    },
    # ...
]
```

---

### 方案 B: 场景模板库（辅助方案）

创建预定义的安全场景模板，确保质量。

**实现位置**: 新建 `utils/scene_templates.py`

```python
"""场景模板库"""

# 场景分类
SCENE_CATEGORIES = {
    "tea_garden": {
        "name": "茶园场景",
        "templates": [
            "solo, 1girl, upper body, front view, tea garden, wearing casual dress, morning sunlight, picking tea leaves, smiling",
            "solo, 1girl, full body, standing in tea field, wearing hanfu, afternoon light, holding basket, looking at camera",
            "solo, 1girl, sitting on tea hill, traditional outfit, sunset glow, peaceful expression, side view"
        ]
    },
    "traditional_room": {
        "name": "传统室内",
        "templates": [
            "solo, 1girl, upper body, traditional tea room, wearing qipao, making tea, focused expression, front view",
            "solo, 1girl, sitting at tea table, traditional Chinese room, afternoon sunlight through window, elegant posture",
            "solo, 1girl, full body, standing in traditional study, wearing hanfu, reading, gentle smile"
        ]
    },
    "courtyard": {
        "name": "庭院场景",
        "templates": [
            "solo, 1girl, upper body, traditional courtyard, wearing casual dress, morning light, watering plants, front view",
            "solo, 1girl, sitting on wooden chair, courtyard, reading book, afternoon sunlight, peaceful atmosphere",
            "solo, 1girl, full body, walking in courtyard, wearing hanfu, surrounded by flowers, gentle smile"
        ]
    },
    "casual_indoor": {
        "name": "日常室内",
        "templates": [
            "solo, 1girl, upper body, bedroom, wearing casual clothes, morning light, looking at camera, gentle smile",
            "solo, 1girl, sitting on bed, cozy room, afternoon sunlight, reading, relaxed expression",
            "solo, 1girl, standing by window, home interior, soft lighting, thoughtful expression, side view"
        ]
    }
}

def get_safe_scene_template(topic_type: str, persona: dict) -> str:
    """
    根据话题类型返回安全的场景模板

    参数:
        topic_type: 话题类型（如：采茶日常、传统文化等）
        persona: 人设数据

    返回:
        场景描述模板
    """
    import random

    # 根据 topic_type 映射到场景分类
    category_mapping = {
        "采茶日常": "tea_garden",
        "茶园": "tea_garden",
        "传统文化": "traditional_room",
        "茶艺": "traditional_room",
        "日常分享": "casual_indoor",
        "休闲时光": "courtyard"
    }

    category = category_mapping.get(topic_type, "casual_indoor")
    templates = SCENE_CATEGORIES[category]["templates"]

    return random.choice(templates)

def validate_scene_safety(scene_hint: str) -> tuple[bool, str]:
    """
    验证场景描述是否安全（单人、无背影）

    返回:
        (is_safe, error_message)
    """
    scene_lower = scene_hint.lower()

    # 检查多人关键词
    multi_person_keywords = [
        "grandfather", "grandpa", "爷爷",
        "friend", "friends", "朋友",
        "people", "crowd", "group",
        "family", "together", "with",
        "2girls", "3girls", "couple"
    ]

    for keyword in multi_person_keywords:
        if keyword in scene_lower:
            return False, f"包含多人关键词: {keyword}"

    # 检查背影关键词
    back_view_keywords = ["back view", "背影", "from behind", "rear view"]
    for keyword in back_view_keywords:
        if keyword in scene_lower:
            return False, f"包含背影描述: {keyword}"

    # 检查是否以 solo 开头
    if not scene_lower.startswith("solo"):
        return False, "未以 'solo' 开头"

    return True, ""
```

**集成到 TweetGenerator**:
```python
from ..utils.scene_templates import get_safe_scene_template, validate_scene_safety

def _parse_response(self, response: str, calendar_plan=None) -> tuple:
    """解析响应，并验证场景安全性"""
    tweet, scene_hint = self._original_parse_response(response)

    # 验证场景安全性
    is_safe, error_msg = validate_scene_safety(scene_hint)

    if not is_safe:
        print(f"[警告] 场景不安全: {error_msg}")
        print(f"[警告] 原始场景: {scene_hint}")

        # 使用安全模板替代
        if calendar_plan:
            topic_type = calendar_plan.get("topic_type", "")
            scene_hint = get_safe_scene_template(topic_type, self.persona)
            print(f"[修复] 使用安全模板: {scene_hint}")

    return tweet, scene_hint
```

---

### 方案 C: 生成后质量检查（可选）

创建图像质量检查节点，检测多人/背影问题。

**实现位置**: 新建 `nodes/image_quality_checker.py`

```python
"""图像质量检查节点（可选）"""
import torch
from transformers import pipeline

class ImageQualityChecker:
    """检查生成的图像是否符合要求"""

    def __init__(self):
        # 可选：加载人脸检测模型
        # self.face_detector = ...
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
            },
            "optional": {
                "enable_face_count": ("BOOLEAN", {"default": True}),
                "enable_face_clarity": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "BOOLEAN")
    RETURN_NAMES = ("images", "quality_report", "passed")
    FUNCTION = "check_quality"
    CATEGORY = "TwitterChat"

    def check_quality(self, images, enable_face_count=True, enable_face_clarity=True):
        """
        检查图像质量

        返回:
            - images: 原图像
            - quality_report: 质量报告
            - passed: 是否通过检查
        """
        issues = []

        if enable_face_count:
            face_count = self._count_faces(images)
            if face_count > 1:
                issues.append(f"检测到 {face_count} 张脸（期望1张）")
            elif face_count == 0:
                issues.append("未检测到人脸")

        if enable_face_clarity:
            clarity_score = self._check_face_clarity(images)
            if clarity_score < 0.5:
                issues.append(f"人脸清晰度不足 ({clarity_score:.2f})")

        passed = len(issues) == 0
        quality_report = "\n".join(issues) if issues else "✓ 质量检查通过"

        return (images, quality_report, passed)

    def _count_faces(self, images):
        """检测图像中的人脸数量"""
        # TODO: 实现人脸检测逻辑
        # 可使用 OpenCV、face_recognition 等库
        return 1  # 占位

    def _check_face_clarity(self, images):
        """检查人脸清晰度"""
        # TODO: 实现清晰度检测
        return 1.0  # 占位
```

---

## 🎨 生成参数优化建议

### LoRA 配置
```json
{
  "lora": {
    "model_name": "z-image/my_first_lora_v1.safetensors",
    "trigger_words": ["みかみゆあ", "三上悠亚", "Yua Mikami"],
    "recommended_weight": 0.85  // 提高到 0.8-0.9
  }
}
```

### 采样参数建议
- **CFG Scale**: 7-9（推荐 7.5）
- **Steps**: 28-35
- **Sampler**: DPM++ 2M Karras 或 Euler a
- **Resolution**: 512x768 或 768x512（避免过大）
- **Clip Skip**: 2

### Negative Prompt 模板
```
multiple people, 2girls, 3girls, group, crowd, other person,
grandfather, friend, family, people in background,
back view, rear view, from behind, distant shot, far away,
blurry face, unclear face, face out of frame, faceless,
multiple faces, extra limbs, deformed hands, bad anatomy,
nsfw, nude, underwear, revealing clothes,
low quality, worst quality, lowres, jpeg artifacts,
watermark, signature, text, logo, username
```

---

## 📊 优化优先级

### 🔥 高优先级（立即实施）

1. **修改日历生成 Prompt**（方案 A1）
   - 影响：最大
   - 难度：低
   - 位置：`utils/calendar_manager.py`

2. **修改推文生成场景要求**（方案 A2）
   - 影响：大
   - 难度：低
   - 位置：`nodes/tweet_generator.py`

3. **优化图像提示词构建**（方案 A3）
   - 影响：大
   - 难度：中
   - 位置：`nodes/image_prompt_builder.py`

### ⚡ 中优先级（短期实施）

4. **创建场景模板库**（方案 B）
   - 影响：中
   - 难度：低
   - 位置：新建 `utils/scene_templates.py`

5. **提高 LoRA 权重**
   - 影响：中
   - 难度：极低
   - 位置：人设 JSON 配置

### 🌟 低优先级（长期优化）

6. **图像质量检查**（方案 C）
   - 影响：中
   - 难度：高
   - 位置：新建 `nodes/image_quality_checker.py`

---

## 🚀 实施计划

### 阶段 1: 快速修复（1天）
- [x] 修改 CalendarManager 的 prompt，添加单人场景约束
- [x] 修改 TweetGenerator 的场景描述要求
- [x] 更新人设 JSON，提高 LoRA 权重到 0.85

### 阶段 2: 深度优化（2-3天）
- [ ] 重构 ImagePromptBuilder，添加场景清理和负面提示词
- [ ] 创建场景模板库
- [ ] 集成场景验证逻辑

### 阶段 3: 质量保障（1周）
- [ ] 创建图像质量检查节点（可选）
- [ ] 批量测试 50+ 场景
- [ ] 建立问题案例库

---

## 📝 测试验证

### 测试场景清单

**必须通过的场景**:
- ✅ 茶园采茶（独自）
- ✅ 室内泡茶
- ✅ 庭院看书
- ✅ 穿汉服户外
- ✅ 穿旗袍室内
- ✅ 日常自拍

**必须避免的场景**:
- ❌ 和爷爷在茶园
- ❌ 和朋友聚会
- ❌ 合影
- ❌ 背影
- ❌ 远景
- ❌ 群体活动

### 质量评估标准

**A 级（优秀）**:
- 单人清晰
- 人脸清楚
- 姿态自然
- 场景匹配人设
- LoRA 特征明显

**B 级（良好）**:
- 单人
- 人脸可见
- 姿态基本自然
- 场景合理

**C 级（不合格）**:
- 多人
- 背影/远景
- 人脸模糊
- 场景不符

---

## 🔧 快速排查清单

如果生成结果有问题，按顺序检查：

1. **检查 CalendarManager 输出的 suggested_scene**
   - 是否包含多人关键词？
   - 是否包含背影描述？

2. **检查 TweetGenerator 输出的 scene_hint**
   - 是否以 "solo, 1girl" 开头？
   - 是否包含多人关键词？

3. **检查 ImagePromptBuilder 输出的 positive_prompt**
   - LoRA 触发词是否在前面？
   - 是否有 "solo, 1girl" 约束？
   - scene_hint 是否被正确组装？

4. **检查 LoRA 配置**
   - LoRA 权重是否 >= 0.8？
   - LoRA 文件路径是否正确？
   - LoRA 触发词是否匹配？

5. **检查采样参数**
   - CFG Scale 是否在 7-9？
   - Negative Prompt 是否包含多人约束？

---

## 💡 最佳实践

1. **保持 Prompt 简洁**
   - 单个 prompt 不超过 75 tokens
   - 关键词放在前面
   - 使用权重标记 `(keyword:1.2)`

2. **使用一致的场景模板**
   - 建立场景库，避免 LLM 自由发挥
   - 预定义安全场景

3. **强化单人约束**
   - 在多个环节重复强调
   - 使用高权重 `(solo:1.4)`

4. **定期测试验证**
   - 每周抽样测试 20 张
   - 记录问题案例
   - 持续优化 prompt

---

**文档版本**: v1.0
**最后更新**: 2025-12-03
**作者**: Claude Code
