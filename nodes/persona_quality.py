"""
Persona Quality Enhancement Nodes - Phase 2
人设质量提升节点 - 策略生成、视觉提取、scene_hint增强等
"""

import json
import requests
import copy
from collections import Counter
import re


class PersonaTweetStrategyGenerator:
    """
    推文策略生成节点
    先生成详细的内容策略，然后用于指导推文生成
    这样可以确保推文更符合人设定位和内容分布要求
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "core_persona_json": ("STRING", {
                    "forceInput": True
                }),
                "api_key": ("STRING", {
                    "default": "sk-7U0E6zRslf3aUM2Z9DcEIbaWxDY3aRZbR5Wq4g0TKw0IPe1L",
                    "multiline": False
                }),
                "api_base": ("STRING", {
                    "default": "https://www.dmxapi.cn/v1",
                    "multiline": False
                }),
                "model": ("STRING", {
                    "default": "gpt-4.1",
                    "multiline": False
                }),
                "temperature": ("FLOAT", {
                    "default": 0.8,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.05
                })
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("strategy_json",)
    FUNCTION = "generate_strategy"
    CATEGORY = "twitterchat/persona"

    def generate_strategy(self, core_persona_json, api_key, api_base, model, temperature):
        """
        生成推文内容策略
        """

        print(f"\n{'='*70}")
        print(f"📊 PersonaTweetStrategyGenerator: Generating content strategy")
        print(f"{'='*70}")

        # 解析core_persona
        try:
            core_persona = json.loads(core_persona_json)
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid core_persona JSON: {str(e)}")

        data = core_persona.get('data', {})
        name = data.get('name', 'Character')
        tags = data.get('tags', [])
        personality = data.get('personality', '')
        description = data.get('description', '')

        # 确定persona类型
        persona_type = self._determine_persona_type(tags, description)

        # 构建prompt
        system_prompt = self._get_system_prompt()
        user_prompt = self._get_user_prompt(data, persona_type)

        print(f"📝 Generating strategy for: {name}")
        print(f"   Type: {persona_type}")
        print(f"\n🤖 Calling LLM...")

        # 调用LLM
        try:
            strategy_text = self._call_llm(
                system_prompt,
                user_prompt,
                api_key,
                api_base,
                model,
                temperature
            )

            # 解析JSON
            strategy = self._parse_and_validate(strategy_text)

            print(f"✅ Strategy generated successfully")
            self._print_strategy_summary(strategy)

            strategy_json = json.dumps(strategy, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"❌ Generation failed: {str(e)}")
            raise

        print(f"{'='*70}\n")

        return (strategy_json,)

    def _determine_persona_type(self, tags, description):
        """确定persona类型"""
        text = ' '.join(tags).lower() + ' ' + description.lower()

        if 'bdsm' in text or 'submissive' in text or 'dom' in text:
            return 'bdsm_sub' if 'sub' in text else 'bdsm_dom'
        elif 'fitness' in text or 'gym' in text or 'workout' in text:
            return 'fitness_girl'
        elif 'artist' in text or 'creative' in text or 'art' in text:
            return 'artist'
        elif 'neighbor' in text or 'girl-next-door' in text:
            return 'neighbor'
        else:
            return 'attractive-woman'

    def _get_system_prompt(self):
        """系统提示词"""
        return """You are an expert at designing social media content strategies.

Create a detailed content strategy for this persona's Twitter presence that will:
1. Maximize engagement and follower attraction
2. Maintain authentic, believable posting patterns
3. Balance different content types strategically
4. Incorporate time-based mood variations
5. Include strategic imperfections for authenticity

Output ONLY valid JSON, no markdown blocks."""

    def _get_user_prompt(self, persona_data, persona_type):
        """用户提示词"""

        name = persona_data.get('name', 'Character')
        personality = persona_data.get('personality', '')
        description = persona_data.get('description', '')[:500]
        appearance = persona_data.get('appearance', {})
        lifestyle = persona_data.get('lifestyle_details', {})
        verbal_style = persona_data.get('verbal_style', {})

        # 根据类型提供策略模板
        type_strategies = {
            'bdsm_sub': {
                'distribution': {
                    'submission_craving': 0.35,
                    'good_girl_display': 0.25,
                    'seeking_owner': 0.20,
                    'bdsm_lifestyle': 0.15,
                    'playful_bratty': 0.05
                },
                'core_themes': ['submission', 'obedience', 'seeking Dom/Mistress', 'BDSM exploration', 'pet play']
            },
            'fitness_girl': {
                'distribution': {
                    'workout_motivation': 0.30,
                    'body_confidence': 0.25,
                    'lifestyle_healthy': 0.20,
                    'personal_moments': 0.15,
                    'flirty_teasing': 0.10
                },
                'core_themes': ['fitness journey', 'body positivity', 'gym culture', 'healthy lifestyle', 'strength']
            },
            'artist': {
                'distribution': {
                    'creative_work': 0.30,
                    'aesthetic_moments': 0.25,
                    'personal_thoughts': 0.20,
                    'lifestyle_artsy': 0.15,
                    'subtle_sexy': 0.10
                },
                'core_themes': ['creativity', 'artistic vision', 'aesthetics', 'indie culture', 'self-expression']
            },
            'neighbor': {
                'distribution': {
                    'lifestyle_mundane': 0.35,
                    'personal_emotion': 0.25,
                    'interaction_bait': 0.20,
                    'visual_showcase': 0.12,
                    'subtle_flirty': 0.08
                },
                'core_themes': ['everyday life', 'relatable moments', 'sweet & approachable', 'coffee culture', 'simple pleasures']
            },
            'attractive-woman': {
                'distribution': {
                    'lifestyle_mundane': 0.30,
                    'personal_emotion': 0.25,
                    'visual_showcase': 0.20,
                    'interaction_bait': 0.15,
                    'flirty_content': 0.10
                },
                'core_themes': ['lifestyle', 'confidence', 'self-care', 'social life', 'personal growth']
            }
        }

        strategy_template = type_strategies.get(persona_type, type_strategies['attractive-woman'])

        return f"""Create a comprehensive content strategy for this Twitter persona:

PERSONA SUMMARY:
Name: {name}
Type: {persona_type}
Personality: {personality}
Description: {description}
Appearance: {appearance}
Lifestyle: {lifestyle.get('hobbies', [])}
Verbal Style: {verbal_style.get('spoken_tone', '')}

TEMPLATE GUIDANCE (adapt to this specific persona):
Suggested Distribution: {strategy_template['distribution']}
Core Themes: {strategy_template['core_themes']}

REQUIRED OUTPUT FORMAT:
{{
  "content_type_distribution": {{
    "type_name": {{
      "weight": 0.35,
      "description": "What this type covers and why it's important",
      "examples": ["Example tweet idea 1", "Example tweet idea 2", "Example tweet idea 3"]
    }},
    ... (5-6 content types total, weights must sum to 1.0)
  }},

  "time_based_mood": {{
    "morning": {{
      "time": "08:00-12:00",
      "mood": "Descriptive mood for this time",
      "content_preference": ["type1", "type2"],
      "language_style": "How she speaks in the morning",
      "example": "Example tweet for this time"
    }},
    "afternoon": {{
      "time": "12:00-18:00",
      "mood": "...",
      "content_preference": ["..."],
      "language_style": "...",
      "example": "..."
    }},
    "evening_prime": {{
      "time": "18:00-22:00",
      "mood": "...",
      "content_preference": ["..."],
      "language_style": "...",
      "example": "...",
      "note": "Prime posting time for visual content"
    }},
    "late_night": {{
      "time": "22:00-03:00",
      "mood": "...",
      "content_preference": ["..."],
      "language_style": "...",
      "example": "...",
      "note": "Most intimate and vulnerable time"
    }}
  }},

  "strategic_flaws": {{
    "active_flaws": [
      {{
        "type": "sleep_deprived",
        "frequency": 0.20,
        "time_preference": ["late_night", "early_morning"],
        "manifestations": ["Specific example 1", "Specific example 2"],
        "benefit": "Why this makes her more authentic"
      }},
      {{
        "type": "emotional_moment",
        "frequency": 0.15,
        "manifestations": ["..."],
        "benefit": "..."
      }},
      {{
        "type": "clumsy_moment",
        "frequency": 0.10,
        "manifestations": ["..."],
        "benefit": "..."
      }}
    ],
    "integration_rule": "How to naturally incorporate these flaws"
  }},

  "engagement_tactics": {{
    "interaction_hooks": [
      "Question format that encourages responses",
      "Poll topic that fits her personality",
      "Relatable statement that prompts sharing"
    ],
    "reply_style": "How she responds to comments and DMs",
    "community_building": "How she builds follower relationships"
  }},

  "visual_content_guide": {{
    "outfit_categories": [
      "Category 1 (e.g., 'workout gear'): specific items",
      "Category 2 (e.g., 'cozy home'): specific items",
      "Category 3 (e.g., 'going out'): specific items"
    ],
    "scene_locations": [
      "Location 1: why and when",
      "Location 2: why and when",
      "Location 3: why and when"
    ],
    "lighting_moods": [
      "Mood 1: specific lighting setup",
      "Mood 2: specific lighting setup"
    ],
    "pose_guidelines": "General guidance on attractive posing for her body type and personality"
  }},

  "posting_rhythm": {{
    "frequency": "X-Y tweets/day",
    "best_times": [
      "Time slot 1: content type",
      "Time slot 2: content type",
      "Time slot 3: content type"
    ],
    "peak_days": ["Monday", "Wednesday", "Friday", ...],
    "consistency_note": "Pattern followers can expect"
  }}
}}

CRITICAL REQUIREMENTS:
1. Adapt the template to THIS specific persona's unique traits
2. All content types must be authentic to her personality
3. Time-based moods should reflect realistic daily patterns
4. Strategic flaws must feel natural, not forced
5. Weights in content_type_distribution must sum to 1.0
6. Include 5-6 content types (not more, not less)
7. Make engagement tactics specific to her appeal

Generate the strategy JSON now:"""

    def _call_llm(self, system_prompt, user_prompt, api_key, api_base, model, temperature):
        """调用LLM"""
        url = f"{api_base.rstrip('/')}/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": 6000
        }

        response = requests.post(url, headers=headers, json=data, timeout=180)
        response.raise_for_status()

        result = response.json()
        content = result['choices'][0]['message']['content']

        return content

    def _parse_and_validate(self, content):
        """解析并验证JSON"""
        # 清理markdown
        content = content.strip()
        if content.startswith('```'):
            lines = content.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            content = '\n'.join(lines)

        content = content.strip()

        try:
            strategy = json.loads(content)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON parsing failed: {str(e)}")

        # 验证必需字段
        required_fields = ['content_type_distribution', 'time_based_mood', 'strategic_flaws']
        for field in required_fields:
            if field not in strategy:
                raise Exception(f"Missing required field: {field}")

        # 验证权重总和
        distribution = strategy.get('content_type_distribution', {})
        total_weight = sum(item.get('weight', 0) for item in distribution.values())
        if abs(total_weight - 1.0) > 0.01:
            print(f"   ⚠️  Warning: Content type weights sum to {total_weight:.2f}, not 1.0")

        print(f"   ✓ JSON validation passed")

        return strategy

    def _print_strategy_summary(self, strategy):
        """打印策略摘要"""
        distribution = strategy.get('content_type_distribution', {})
        flaws = strategy.get('strategic_flaws', {}).get('active_flaws', [])
        posting = strategy.get('posting_rhythm', {})

        print(f"\n📊 Strategy Summary:")
        print(f"   Content Types: {len(distribution)}")
        for type_name, info in distribution.items():
            weight = info.get('weight', 0)
            print(f"   - {type_name}: {weight*100:.0f}%")

        print(f"\n   Strategic Flaws: {len(flaws)}")
        for flaw in flaws:
            print(f"   - {flaw.get('type', 'unknown')}: {flaw.get('frequency', 0)*100:.0f}%")

        print(f"\n   Posting: {posting.get('frequency', 'N/A')}")


class PersonaVisualProfileExtractor:
    """
    视觉档案提取节点
    从推文的scene_hint中自动提取常见服装、道具、颜色、姿势等
    生成统一的visual_profile，确保视觉一致性
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "persona_json": ("STRING", {
                    "forceInput": True
                }),
                "api_key": ("STRING", {
                    "default": "sk-7U0E6zRslf3aUM2Z9DcEIbaWxDY3aRZbR5Wq4g0TKw0IPe1L",
                    "multiline": False
                }),
                "api_base": ("STRING", {
                    "default": "https://www.dmxapi.cn/v1",
                    "multiline": False
                }),
                "model": ("STRING", {
                    "default": "gpt-4.1",
                    "multiline": False
                })
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("visual_profile_json",)
    FUNCTION = "extract_visual_profile"
    CATEGORY = "twitterchat/persona"

    def extract_visual_profile(self, persona_json, api_key, api_base, model):
        """
        提取视觉档案
        """

        print(f"\n{'='*70}")
        print(f"🎨 PersonaVisualProfileExtractor: Extracting visual profile")
        print(f"{'='*70}")

        # 解析persona
        try:
            persona = json.loads(persona_json)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON parsing failed: {str(e)}")

        data = persona.get('data', {})
        tweets = data.get('twitter_persona', {}).get('tweet_examples', [])

        if not tweets:
            raise Exception("No tweets found in persona")

        # 收集所有scene_hints
        scene_hints = [t.get('scene_hint', '') for t in tweets if t.get('scene_hint')]

        print(f"📸 Analyzing {len(scene_hints)} scene hints...")

        # 使用LLM提取
        visual_profile = self._extract_with_llm(scene_hints, data, api_key, api_base, model)

        print(f"✅ Visual profile extracted")
        self._print_profile_summary(visual_profile)

        visual_profile_json = json.dumps(visual_profile, ensure_ascii=False, indent=2)

        print(f"{'='*70}\n")

        return (visual_profile_json,)

    def _extract_with_llm(self, scene_hints, persona_data, api_key, api_base, model):
        """使用LLM提取视觉档案"""

        # 构建prompt
        system_prompt = """You are an expert at analyzing visual content descriptions and extracting patterns.

Analyze the scene descriptions and identify:
1. Common outfits and clothing items
2. Frequently used props and accessories
3. Color preferences
4. Lighting preferences
5. Typical poses and body language
6. Any special elements (e.g., BDSM items, fitness equipment, art supplies)

Output ONLY valid JSON."""

        combined_hints = "\n\n---\n\n".join(scene_hints[:20])  # 最多20条

        persona_type_indicators = ' '.join(persona_data.get('tags', []))

        user_prompt = f"""Analyze these scene descriptions and extract visual patterns:

PERSONA CONTEXT:
Tags: {persona_type_indicators}
Appearance: {persona_data.get('appearance', {})}

SCENE DESCRIPTIONS:
{combined_hints}

Extract and return JSON:
{{
  "common_outfits": [
    "Outfit 1: detailed description with specific items",
    "Outfit 2: ...",
    "Outfit 3: ...",
    ... (3-5 most common outfits)
  ],
  "common_props": [
    "Prop 1",
    "Prop 2",
    "Prop 3",
    ... (props that appear repeatedly)
  ],
  "color_preferences": ["color1", "color2", "color3", ...],
  "lighting_preferences": [
    "Lighting setup 1: description",
    "Lighting setup 2: ...",
    ...
  ],
  "typical_poses": [
    "Pose 1: description",
    "Pose 2: ...",
    ...
  ],
  "special_elements": [
    "Element 1 (if any BDSM/fitness/art-specific items)",
    ...
  ],
  "atmosphere_keywords": ["keyword1", "keyword2", ...],
  "camera_angles": ["angle1", "angle2", ...]
}}

Focus on items that appear in MULTIPLE scenes. Ignore one-off items."""

        url = f"{api_base.rstrip('/')}/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,  # 低温保证精确提取
            "max_tokens": 3000
        }

        print(f"🤖 Calling LLM for extraction...")

        response = requests.post(url, headers=headers, json=data, timeout=120)
        response.raise_for_status()

        result = response.json()
        content = result['choices'][0]['message']['content']

        # 解析JSON
        content = content.strip()
        if content.startswith('```'):
            lines = content.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            content = '\n'.join(lines)

        visual_profile = json.loads(content.strip())

        return visual_profile

    def _print_profile_summary(self, profile):
        """打印视觉档案摘要"""
        print(f"\n🎨 Visual Profile Summary:")
        print(f"   Outfits: {len(profile.get('common_outfits', []))}")
        print(f"   Props: {len(profile.get('common_props', []))}")
        print(f"   Colors: {', '.join(profile.get('color_preferences', [])[:5])}")
        print(f"   Lighting styles: {len(profile.get('lighting_preferences', []))}")
        print(f"   Typical poses: {len(profile.get('typical_poses', []))}")


# 节点映射
NODE_CLASS_MAPPINGS = {
    "PersonaTweetStrategyGenerator": PersonaTweetStrategyGenerator,
    "PersonaVisualProfileExtractor": PersonaVisualProfileExtractor
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PersonaTweetStrategyGenerator": "Persona Tweet Strategy Generator 📊",
    "PersonaVisualProfileExtractor": "Persona Visual Profile Extractor 🎨"
}
