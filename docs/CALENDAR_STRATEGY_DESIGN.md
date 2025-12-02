# Calendar Manager 策略系统设计方案

## 📋 目录
- [问题分析](#问题分析)
- [设计目标](#设计目标)
- [架构设计](#架构设计)
- [数据来源](#数据来源)
- [实现方案](#实现方案)
- [使用示例](#使用示例)

---

## 问题分析

### 当前硬编码的内容

```python
# calendar_manager.py - 当前的硬编码
运营目标：
- 吸引男性粉丝                 ← 写死
- 保持适度性感暧昧风格          ← 写死！与清纯人设冲突
- 内容多样化但符合人设

要求：
- 周一：身材展示类 - 新周动力   ← 不适合茶园人设
- 周三：生活撒娇类 - 轻松日常
- 周五：福利互动类 - 周末福利
- 周日：暧昧互动类 - 休息日闲聊

内容分布：身材展示40%、暧昧互动25%、生活日常20%、福利互动15%  ← 与人设冲突

节假日：us_holidays = holidays.US()  ← 林美灵是中国人，应该用中国节假日
```

### 核心问题

1. **风格冲突**：性感暧昧策略 vs 清纯茶园人设
2. **内容分布冲突**：身材展示40% vs 个人生活60%
3. **国家冲突**：美国节假日 vs 中国节假日
4. **不可扩展**：新增人设类型需要修改代码

---

## 设计目标

### 核心原则

```
1. 数据驱动：策略应该来自人设文件，而非代码
2. 多层优先级：显式配置 > 自动推断 > 默认值
3. 向后兼容：旧人设文件不应该崩溃
4. 易于扩展：新增人设类型不需要修改代码
```

### 灵活性要求

- ✅ 不同人设有不同的运营策略
- ✅ 支持从人设文件显式配置
- ✅ 支持基于现有字段自动推断
- ✅ 支持基于 tags 自动匹配模板
- ✅ 支持手动覆盖（通过节点参数）

---

## 架构设计

### 1. 整体架构

```
┌─────────────────────────────────────────────────┐
│           CalendarManager 节点                   │
│  (用户界面: persona, api_key, force_regenerate)│
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│        CalendarStrategyBuilder                   │
│  (策略构建器: 多层级读取和推断)                  │
└────────────────┬────────────────────────────────┘
                 │
         ┌───────┼───────┐
         ▼       ▼       ▼
    ┌─────┐ ┌─────┐ ┌─────┐
    │显式 │ │推断 │ │模板 │
    │配置 │ │策略 │ │匹配 │
    └─────┘ └─────┘ └─────┘
         │       │       │
         └───────┼───────┘
                 ▼
         ┌──────────────┐
         │ 完整的策略对象│
         │ CalendarStrategy│
         └───────┬────────┘
                 │
                 ▼
         ┌──────────────┐
         │生成 LLM Prompt│
         └──────────────┘
```

### 2. CalendarStrategy 数据结构

```python
@dataclass
class CalendarStrategy:
    """日历策略完整定义"""

    # 基本信息
    persona_name: str
    persona_description: str
    persona_personality: str

    # 目标受众
    target_audience: dict  # {gender, age_range, interests}

    # 风格描述
    style_description: str

    # 周节奏（周一到周日的内容类型）
    weekly_rhythm: dict  # {weekday: {topic_type, description, keywords}}

    # 内容分布（百分比）
    content_distribution: dict  # {content_type: percentage}

    # 节假日配置
    holidays_config: dict  # {country_code, custom_holidays}
```

### 3. 多层优先级系统

```
优先级 1 (最高): 人设文件显式配置
    └─ data.calendar_strategy (新增字段，可选)

优先级 2: 从现有字段推断
    ├─ twitter_scenario.content_strategy_guide
    ├─ twitter_persona.content_themes
    └─ twitter_persona.tweet_preferences.content_strategy

优先级 3: 基于 tags 自动匹配模板
    ├─ cute/innocent/traditional → 清纯模板
    ├─ fitness/model/athletic → 健身模板
    └─ 其他 → 默认模板

优先级 4 (最低): 默认模板
    └─ 通用性感风格（当前的硬编码内容）
```

---

## 数据来源

### 1. 人设文件中已有的可用数据

#### 茶园女孩（林美灵）

```json
{
  "tags": ["tea", "girl-next-door", "traditional", "cute"],

  "twitter_scenario": {
    "content_strategy_guide": "内容平衡：个人生活/清纯照片 60%、茶园日常背景 25%、暧昧互动 15%"
  },

  "twitter_persona": {
    "content_themes": {
      "personal_life": {"frequency": "60%", ...},
      "tea_garden_background": {"frequency": "25%", ...},
      "flirty_interaction": {"frequency": "15%", ...}
    }
  },

  "core_info": {
    "location": {
      "country_code": "CN"  ← 用于节假日
    }
  }
}
```

#### 健身女孩（Emily）

```json
{
  "tags": ["fitness", "model", "athletic"],

  "extensions": {
    "twitter_persona": {
      "tweet_preferences": {
        "content_strategy": {
          "fitness_content": "40% - workouts, exercises",
          "lifestyle": "30% - meals, daily routines",
          "modeling_content": "20% - photoshoots",
          "fan_interaction": "10% - Q&A, polls"
        }
      }
    }
  }
}
```

### 2. 新增字段（可选）

用户可以在人设文件中添加 `calendar_strategy` 字段实现完全控制：

```json
{
  "data": {
    "calendar_strategy": {
      "target_audience": {
        "gender": "male 80%, female 20%",
        "age_range": "25-45岁",
        "interests": ["茶文化", "传统美女", "生活品质"]
      },

      "style_description": "清纯邻家女孩形象，温柔亲切，适度暧昧但不露骨",

      "weekly_rhythm": {
        "Monday": {
          "topic_type": "茶园日常",
          "description": "新周开始，采茶制茶",
          "keywords": ["采茶", "制茶", "新周", "茶山"]
        },
        "Wednesday": {
          "topic_type": "个人生活",
          "description": "分享日常，展示真实生活",
          "keywords": ["日常", "生活", "真实", "温柔"]
        },
        "Friday": {
          "topic_type": "传统文化",
          "description": "茶文化、传统才艺",
          "keywords": ["茶文化", "传统", "汉服", "书法"]
        },
        "Sunday": {
          "topic_type": "温柔撒娇",
          "description": "休息日，情感互动",
          "keywords": ["撒娇", "互动", "温柔", "情感"]
        }
      },

      "content_distribution": {
        "个人生活/清纯照片": 60,
        "茶园日常背景": 25,
        "暧昧互动": 15
      },

      "holidays_config": {
        "country_code": "CN",
        "custom_holidays": [
          {"date": "2025-05-21", "name": "国际茶日"}
        ]
      }
    }
  }
}
```

---

## 实现方案

### Phase 1: 策略构建器（核心）

```python
class CalendarStrategyBuilder:
    """
    日历策略构建器

    职责：从人设文件中读取、推断、匹配策略
    """

    def __init__(self, persona: dict):
        self.persona = persona
        self.data = persona["data"]

    def build(self) -> CalendarStrategy:
        """
        构建完整策略（多层优先级）

        返回: CalendarStrategy 对象
        """
        # 1. 尝试读取显式配置（优先级1）
        explicit = self._read_explicit_strategy()
        if explicit:
            return explicit

        # 2. 从现有字段推断（优先级2）
        inferred = self._infer_from_existing_fields()
        if inferred:
            return inferred

        # 3. 基于 tags 匹配模板（优先级3）
        template_matched = self._match_template_by_tags()
        if template_matched:
            return template_matched

        # 4. 使用默认模板（优先级4）
        return self._get_default_strategy()

    def _read_explicit_strategy(self) -> Optional[CalendarStrategy]:
        """读取 data.calendar_strategy 字段"""
        cal_strat = self.data.get("calendar_strategy")
        if not cal_strat:
            return None

        return CalendarStrategy(
            persona_name=self.data.get("name", "Unknown"),
            persona_description=self.data.get("description", ""),
            persona_personality=self.data.get("personality", ""),
            target_audience=cal_strat.get("target_audience", {}),
            style_description=cal_strat.get("style_description", ""),
            weekly_rhythm=cal_strat.get("weekly_rhythm", {}),
            content_distribution=cal_strat.get("content_distribution", {}),
            holidays_config=cal_strat.get("holidays_config", {})
        )

    def _infer_from_existing_fields(self) -> Optional[CalendarStrategy]:
        """从现有字段推断策略"""

        # 1. 提取内容分布
        content_dist = self._extract_content_distribution()
        if not content_dist:
            return None

        # 2. 推断周节奏
        weekly_rhythm = self._infer_weekly_rhythm(content_dist)

        # 3. 推断风格描述
        style_desc = self._infer_style_description()

        # 4. 推断目标受众
        target_aud = self._infer_target_audience()

        # 5. 获取节假日配置
        holidays_conf = self._get_holidays_config()

        return CalendarStrategy(
            persona_name=self.data.get("name", "Unknown"),
            persona_description=self.data.get("description", ""),
            persona_personality=self.data.get("personality", ""),
            target_audience=target_aud,
            style_description=style_desc,
            weekly_rhythm=weekly_rhythm,
            content_distribution=content_dist,
            holidays_config=holidays_conf
        )

    def _extract_content_distribution(self) -> dict:
        """
        提取内容分布

        尝试顺序：
        1. twitter_persona.content_themes (结构化)
        2. twitter_scenario.content_strategy_guide (文本，需解析)
        3. tweet_preferences.content_strategy (结构化)
        """
        # 方式1: 从 content_themes 提取
        twitter_persona = (
            self.data.get("twitter_persona") or
            self.data.get("extensions", {}).get("twitter_persona", {})
        )
        content_themes = twitter_persona.get("content_themes", {})

        if content_themes:
            distribution = {}
            for theme_name, theme_data in content_themes.items():
                freq = theme_data.get("frequency", "")
                # 解析百分比，如 "60%" → 60
                percent = self._parse_percentage(freq)
                if percent:
                    # 美化主题名称
                    display_name = theme_data.get("goal", theme_name)
                    distribution[display_name] = percent

            if distribution:
                return distribution

        # 方式2: 解析 content_strategy_guide
        twitter_scenario = self.data.get("twitter_scenario", {})
        strategy_guide = twitter_scenario.get("content_strategy_guide", "")

        if strategy_guide:
            distribution = self._parse_content_strategy_text(strategy_guide)
            if distribution:
                return distribution

        # 方式3: 从 content_strategy 提取
        tweet_prefs = twitter_persona.get("tweet_preferences", {})
        content_strategy = tweet_prefs.get("content_strategy", {})

        if content_strategy:
            distribution = {}
            for key, value in content_strategy.items():
                # 解析格式: "40% - workouts, exercises"
                percent = self._parse_percentage(value)
                if percent:
                    distribution[key] = percent

            if distribution:
                return distribution

        return {}

    def _parse_content_strategy_text(self, text: str) -> dict:
        """
        解析文本格式的内容策略

        输入: "内容平衡：个人生活/清纯照片 60%、茶园日常背景 25%、暧昧互动 15%"
        输出: {"个人生活/清纯照片": 60, "茶园日常背景": 25, "暧昧互动": 15}
        """
        import re

        # 匹配模式: "名称 百分比%"
        pattern = r'([^、：]+?)\s*(\d+)%'
        matches = re.findall(pattern, text)

        return {name.strip(): int(percent) for name, percent in matches}

    def _parse_percentage(self, text: str) -> int:
        """从文本中提取百分比数字"""
        import re
        match = re.search(r'(\d+)%', str(text))
        return int(match.group(1)) if match else 0

    def _infer_weekly_rhythm(self, content_dist: dict) -> dict:
        """
        根据内容分布推断周节奏

        策略：
        - 将内容类型分配到一周的不同日子
        - 按照比例分配，高比例内容出现次数多
        """
        # 按比例排序
        sorted_types = sorted(
            content_dist.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # 固定的周节奏框架
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday",
                    "Friday", "Saturday", "Sunday"]

        # 根据比例分配内容类型到不同日子
        weekly_rhythm = {}

        if len(sorted_types) >= 3:
            # 有3+种类型，分配到不同日子
            primary_type = sorted_types[0][0]    # 最高比例
            secondary_type = sorted_types[1][0]  # 次高比例
            tertiary_type = sorted_types[2][0]   # 第三

            weekly_rhythm = {
                "Monday": {
                    "topic_type": primary_type,
                    "description": f"新周开始 - {primary_type}",
                    "keywords": self._generate_keywords(primary_type)
                },
                "Tuesday": {
                    "topic_type": secondary_type,
                    "description": f"{secondary_type}",
                    "keywords": self._generate_keywords(secondary_type)
                },
                "Wednesday": {
                    "topic_type": primary_type,
                    "description": f"周中 - {primary_type}",
                    "keywords": self._generate_keywords(primary_type)
                },
                "Thursday": {
                    "topic_type": tertiary_type,
                    "description": f"{tertiary_type}",
                    "keywords": self._generate_keywords(tertiary_type)
                },
                "Friday": {
                    "topic_type": secondary_type,
                    "description": f"周末前 - {secondary_type}",
                    "keywords": self._generate_keywords(secondary_type)
                },
                "Saturday": {
                    "topic_type": primary_type,
                    "description": f"周末 - {primary_type}",
                    "keywords": self._generate_keywords(primary_type)
                },
                "Sunday": {
                    "topic_type": tertiary_type,
                    "description": f"休息日 - {tertiary_type}",
                    "keywords": self._generate_keywords(tertiary_type)
                }
            }
        else:
            # 内容类型少，使用默认分配
            for i, weekday in enumerate(weekdays):
                type_index = i % len(sorted_types)
                content_type = sorted_types[type_index][0]

                weekly_rhythm[weekday] = {
                    "topic_type": content_type,
                    "description": f"{content_type}",
                    "keywords": self._generate_keywords(content_type)
                }

        return weekly_rhythm

    def _generate_keywords(self, content_type: str) -> list:
        """根据内容类型生成关键词"""
        # 简单的关键词提取（可以进一步优化）
        keywords = [word.strip() for word in content_type.replace("/", " ").split()
                    if len(word.strip()) > 1]
        return keywords[:4]  # 最多4个关键词

    def _infer_style_description(self) -> str:
        """推断风格描述"""
        # 尝试从 tweet_guidance 获取
        tweet_guidance = (
            self.data.get("tweet_guidance") or
            self.data.get("extensions", {}).get("tweet_guidance", "")
        )

        if tweet_guidance:
            # 提取前几行作为风格描述
            lines = tweet_guidance.split('\n')
            desc_lines = [l.strip() for l in lines if l.strip()
                          and not l.strip().startswith('-')
                          and not l.strip().startswith('⭐')][:3]
            return ' '.join(desc_lines)

        # Fallback: 从 system_prompt 提取
        system_prompt = self.data.get("system_prompt", "")
        if system_prompt:
            # 提取描述性句子（简单启发式）
            sentences = system_prompt.split('。')
            return sentences[0] + '。' if sentences else ""

        return ""

    def _infer_target_audience(self) -> dict:
        """推断目标受众"""
        # 尝试从 target_audience 字段读取
        target_aud = (
            self.data.get("target_audience") or
            self.data.get("extensions", {}).get("target_audience", {})
        )

        if target_aud:
            primary_demo = target_aud.get("primary_demographics", {})
            return {
                "gender": primary_demo.get("gender", ""),
                "age_range": primary_demo.get("age_range", ""),
                "interests": primary_demo.get("interests", [])
            }

        # 默认假设（可以根据 tags 进一步推断）
        return {
            "gender": "male 80%, female 20%",
            "age_range": "25-45岁",
            "interests": []
        }

    def _get_holidays_config(self) -> dict:
        """获取节假日配置"""
        # 从 core_info.location 获取国家代码
        core_info = (
            self.data.get("core_info") or
            self.data.get("extensions", {}).get("core_info", {})
        )
        location = core_info.get("location", {})
        country_code = location.get("country_code", "US")

        return {
            "country_code": country_code,
            "custom_holidays": []  # 可以从人设中读取
        }

    def _match_template_by_tags(self) -> Optional[CalendarStrategy]:
        """基于 tags 匹配预定义模板"""
        tags = self.data.get("tags", [])

        # 检查是否匹配清纯风格
        if any(tag in ["cute", "innocent", "girl-next-door", "traditional"] for tag in tags):
            return self._get_cute_template()

        # 检查是否匹配健身风格
        if any(tag in ["fitness", "model", "athletic", "gym"] for tag in tags):
            return self._get_fitness_template()

        return None

    def _get_cute_template(self) -> CalendarStrategy:
        """清纯风格模板"""
        return CalendarStrategy(
            persona_name=self.data.get("name", "Unknown"),
            persona_description=self.data.get("description", ""),
            persona_personality=self.data.get("personality", ""),
            target_audience={
                "gender": "male 80%, female 20%",
                "age_range": "25-45岁",
                "interests": ["传统文化", "生活品质", "真诚互动"]
            },
            style_description="清纯邻家女孩形象，温柔亲切，适度暧昧但不露骨，保持真诚感",
            weekly_rhythm={
                "Monday": {
                    "topic_type": "日常生活",
                    "description": "新周开始，分享日常",
                    "keywords": ["日常", "生活", "新周"]
                },
                "Wednesday": {
                    "topic_type": "特色内容",
                    "description": "展示特色和才艺",
                    "keywords": ["特色", "才艺", "文化"]
                },
                "Friday": {
                    "topic_type": "互动福利",
                    "description": "周末前互动",
                    "keywords": ["互动", "福利", "周末"]
                },
                "Sunday": {
                    "topic_type": "温柔撒娇",
                    "description": "休息日情感互动",
                    "keywords": ["撒娇", "温柔", "情感"]
                }
            },
            content_distribution={
                "个人生活/日常分享": 60,
                "特色背景内容": 25,
                "暧昧互动": 15
            },
            holidays_config=self._get_holidays_config()
        )

    def _get_fitness_template(self) -> CalendarStrategy:
        """健身风格模板"""
        return CalendarStrategy(
            persona_name=self.data.get("name", "Unknown"),
            persona_description=self.data.get("description", ""),
            persona_personality=self.data.get("personality", ""),
            target_audience={
                "gender": "male 70%, female 30%",
                "age_range": "20-40岁",
                "interests": ["健身", "运动", "健康生活"]
            },
            style_description="健身网红形象，展示身材和训练，激励粉丝，适度性感",
            weekly_rhythm={
                "Monday": {
                    "topic_type": "身材展示类",
                    "description": "新周训练，展示效果",
                    "keywords": ["健身", "训练", "身材", "新周"]
                },
                "Wednesday": {
                    "topic_type": "生活日常类",
                    "description": "日常生活，健康饮食",
                    "keywords": ["日常", "饮食", "生活"]
                },
                "Friday": {
                    "topic_type": "福利互动类",
                    "description": "周末福利互动",
                    "keywords": ["福利", "互动", "周末"]
                },
                "Sunday": {
                    "topic_type": "休息恢复类",
                    "description": "休息日放松",
                    "keywords": ["休息", "恢复", "放松"]
                }
            },
            content_distribution={
                "身材展示/训练": 40,
                "生活日常": 30,
                "专业内容": 20,
                "粉丝互动": 10
            },
            holidays_config=self._get_holidays_config()
        )

    def _get_default_strategy(self) -> CalendarStrategy:
        """默认策略（当前的硬编码内容）"""
        return CalendarStrategy(
            persona_name=self.data.get("name", "Unknown"),
            persona_description=self.data.get("description", ""),
            persona_personality=self.data.get("personality", ""),
            target_audience={
                "gender": "male 80%, female 20%",
                "age_range": "25-45岁",
                "interests": []
            },
            style_description="保持适度性感暧昧风格，吸引男性粉丝",
            weekly_rhythm={
                "Monday": {
                    "topic_type": "身材展示类",
                    "description": "新周动力",
                    "keywords": ["身材", "展示", "新周"]
                },
                "Wednesday": {
                    "topic_type": "生活撒娇类",
                    "description": "轻松日常",
                    "keywords": ["生活", "撒娇", "日常"]
                },
                "Friday": {
                    "topic_type": "福利互动类",
                    "description": "周末福利",
                    "keywords": ["福利", "互动", "周末"]
                },
                "Sunday": {
                    "topic_type": "暧昧互动类",
                    "description": "休息日闲聊",
                    "keywords": ["暧昧", "互动", "闲聊"]
                }
            },
            content_distribution={
                "身材展示": 40,
                "暧昧互动": 25,
                "生活日常": 20,
                "福利互动": 15
            },
            holidays_config={"country_code": "US", "custom_holidays": []}
        )
```

### Phase 2: CalendarManager 集成

```python
class CalendarManager:
    def generate_calendar_prompt(self, persona: Dict, year_month: str) -> str:
        """生成日历 LLM prompt（使用策略构建器）"""

        # 1. 构建策略
        builder = CalendarStrategyBuilder(persona)
        strategy = builder.build()

        # 2. 获取节假日
        holidays_info = self._get_holidays_for_month(
            strategy.holidays_config["country_code"],
            year_month
        )

        # 3. 格式化周节奏
        weekly_rhythm_text = self._format_weekly_rhythm(strategy.weekly_rhythm)

        # 4. 格式化内容分布
        content_dist_text = self._format_content_distribution(
            strategy.content_distribution
        )

        # 5. 组装 prompt
        prompt = f"""你是一位专业的社交媒体运营专家，为 {strategy.persona_name} 规划 {year_month} 月的推文运营日历。

人设信息：
- 名称：{strategy.persona_name}
- 描述：{strategy.persona_description}
- 性格：{strategy.persona_personality}

运营目标：
- 目标受众：{strategy.target_audience.get('gender', '')} {strategy.target_audience.get('age_range', '')}
- 内容风格：{strategy.style_description}
- 内容多样化但符合人设

本月特殊日期：
{holidays_info}

要求：
1. 规划 {year_month}-01 到 {year_month}-XX 每天的内容
2. 考虑一周节奏：
{weekly_rhythm_text}
3. 特殊日期要有特殊主题（节日、纪念日）
4. 内容分布：{content_dist_text}
5. 避免连续3天相同类型
6. suggested_scene 用英文描述，简洁明了

输出格式（严格 JSON，不要有其他说明文字）：
{{
  "YYYY-MM-DD": {{
    "weekday": "Monday",
    "topic_type": "...",
    "theme": "...",
    "content_direction": "...",
    "keywords": [...],
    "suggested_scene": "...",
    "special_event": null or "..."
  }}
}}

请直接输出 JSON，不要包含任何 ```json 标记或其他说明。
"""

        return prompt

    def _get_holidays_for_month(self, country_code: str, year_month: str) -> str:
        """获取指定月份的节假日"""
        import holidays
        from datetime import datetime
        import calendar as cal

        year, month = map(int, year_month.split("-"))

        try:
            country_holidays = holidays.country_holidays(country_code, years=year)
        except:
            country_holidays = holidays.US(years=year)

        _, days_in_month = cal.monthrange(year, month)
        month_holidays = []

        for day in range(1, days_in_month + 1):
            date = datetime(year, month, day).date()
            if date in country_holidays:
                holiday_name = country_holidays.get(date)
                month_holidays.append(f"{year_month}-{day:02d}: {holiday_name}")

        return "\n".join(month_holidays) if month_holidays else "无特殊节日"

    def _format_weekly_rhythm(self, weekly_rhythm: dict) -> str:
        """格式化周节奏为文本"""
        lines = []
        for weekday, info in weekly_rhythm.items():
            lines.append(
                f"   - {weekday}: {info['topic_type']} - {info['description']}"
            )
        return "\n".join(lines)

    def _format_content_distribution(self, content_dist: dict) -> str:
        """格式化内容分布为文本"""
        items = [f"{name}{percent}%" for name, percent in content_dist.items()]
        return "、".join(items)
```

---

## 使用示例

### 示例 1：使用现有人设（自动推断）

```python
# 林美灵 - 从 twitter_persona.content_themes 自动推断
persona = load_persona("tea_girl_meilin.json")

# CalendarStrategyBuilder 自动：
# 1. 提取内容分布：个人生活60%、茶园背景25%、暧昧互动15%
# 2. 根据 tags ["cute", "traditional"] 匹配清纯模板
# 3. 根据 country_code="CN" 使用中国节假日
# 4. 自动推断周节奏

# 生成的提示词：
运营目标：
- 目标受众：male 80%, female 20% 25-45岁
- 内容风格：清纯邻家女孩形象，温柔亲切，适度暧昧但不露骨

要求：
2. 考虑一周节奏：
   - Monday: 个人生活/清纯照片 - 新周开始，分享日常
   - Wednesday: 茶园日常背景 - 展示特色和才艺
   - Friday: 个人生活/清纯照片 - 周末前互动
   - Sunday: 暧昧互动 - 休息日情感互动
4. 内容分布：个人生活/清纯照片60%、茶园日常背景25%、暧昧互动15%

本月特殊日期：
2025-12-25: Christmas Day
```

### 示例 2：使用显式配置（完全控制）

```json
// tea_girl_meilin_custom.json
{
  "data": {
    "name": "林美灵",
    "calendar_strategy": {
      "style_description": "清纯茶园女孩，分享真实乡村生活和传统文化",

      "weekly_rhythm": {
        "Monday": {
          "topic_type": "采茶日常",
          "description": "新周开始，采茶制茶",
          "keywords": ["采茶", "制茶", "茶山", "新周"]
        },
        "Wednesday": {
          "topic_type": "传统文化",
          "description": "展示茶艺、书法等传统才艺",
          "keywords": ["茶艺", "书法", "汉服", "传统"]
        },
        "Friday": {
          "topic_type": "温馨生活",
          "description": "和爷爷的日常，家族故事",
          "keywords": ["爷爷", "家族", "温馨", "传承"]
        },
        "Sunday": {
          "topic_type": "撒娇互动",
          "description": "休息日，温柔撒娇",
          "keywords": ["撒娇", "互动", "温柔", "陪伴"]
        }
      },

      "content_distribution": {
        "清纯日常/传统文化": 60,
        "茶园生活背景": 30,
        "温柔撒娇互动": 10
      },

      "holidays_config": {
        "country_code": "CN",
        "custom_holidays": [
          {"date": "2025-05-21", "name": "国际茶日"}
        ]
      }
    }
  }
}
```

---

## 总结

### 核心优势

1. **完全数据驱动**：策略来自人设文件，而非硬编码
2. **多层优先级**：显式配置 > 推断 > 模板 > 默认
3. **向后兼容**：旧人设文件仍然可用（使用默认策略）
4. **易于扩展**：新增人设类型无需修改代码
5. **灵活强大**：支持从简单（只设tags）到复杂（完整配置）

### 实施计划

```
Phase 1: 核心框架（2-3天）
  ├─ CalendarStrategy 数据类
  ├─ CalendarStrategyBuilder 构建器
  └─ 基本的推断逻辑

Phase 2: 智能推断（2天）
  ├─ 内容分布提取（多种格式）
  ├─ 周节奏自动推断
  └─ 风格描述提取

Phase 3: 模板匹配（1天）
  ├─ 清纯模板
  ├─ 健身模板
  └─ 默认模板

Phase 4: 集成和测试（1天）
  ├─ CalendarManager 集成
  ├─ 节假日优化（country_code）
  └─ 端到端测试

总计：6-7天
```

### 下一步行动

1. **确认设计方案**：与用户确认架构是否满足需求
2. **创建 CalendarStrategy 数据类**
3. **实现 CalendarStrategyBuilder**（核心）
4. **测试不同场景**（林美灵、Emily、新人设）
5. **更新文档和模板**
