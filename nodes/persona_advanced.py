"""
Persona Advanced Generation Nodes - Phase 3
人设高级生成节点 - 社交关系、真实感系统、知识库等
"""

import json
import requests
import copy
import random


class PersonaSocialGenerator:
    """
    社交关系生成节点
    生成详细的社交网络：朋友、过往关系、在线朋友等
    每个关系都有详细的故事、性格、互动模式
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "core_persona_json": ("STRING", {
                    "forceInput": True
                }),
                "num_close_friends": ("INT", {
                    "default": 2,
                    "min": 1,
                    "max": 5,
                    "step": 1
                }),
                "num_past_relationships": ("INT", {
                    "default": 2,
                    "min": 0,
                    "max": 4,
                    "step": 1
                }),
                "num_online_friends": ("INT", {
                    "default": 2,
                    "min": 0,
                    "max": 5,
                    "step": 1
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
                    "default": 0.85,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.05
                })
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("social_data_json",)
    FUNCTION = "generate_social"
    CATEGORY = "twitterchat/persona"

    def generate_social(self, core_persona_json, num_close_friends, num_past_relationships,
                       num_online_friends, api_key, api_base, model, temperature):
        """
        生成社交关系网络
        """

        print(f"\n{'='*70}")
        print(f"👥 PersonaSocialGenerator: Generating social network")
        print(f"{'='*70}")

        # 解析core_persona
        try:
            core_persona = json.loads(core_persona_json)
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid core_persona JSON: {str(e)}")

        data = core_persona.get('data', {})
        name = data.get('name', 'Character')
        age = data.get('core_info', {}).get('age', 23)
        personality = data.get('personality', '')
        background = data.get('background_info', {})
        tags = data.get('tags', [])

        print(f"📝 Generating social network for: {name}")
        print(f"   Close friends: {num_close_friends}")
        print(f"   Past relationships: {num_past_relationships}")
        print(f"   Online friends: {num_online_friends}")

        # 构建prompt
        system_prompt = self._get_system_prompt()
        user_prompt = self._get_user_prompt(
            data, num_close_friends, num_past_relationships, num_online_friends
        )

        print(f"\n🤖 Calling LLM...")

        # 调用LLM
        try:
            social_text = self._call_llm(
                system_prompt,
                user_prompt,
                api_key,
                api_base,
                model,
                temperature
            )

            # 解析JSON
            social_data = self._parse_and_validate(social_text)

            print(f"✅ Social network generated")
            self._print_summary(social_data)

            social_json = json.dumps(social_data, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"❌ Generation failed: {str(e)}")
            raise

        print(f"{'='*70}\n")

        return (social_json,)

    def _get_system_prompt(self):
        """系统提示词"""
        return """You are an expert at creating believable social networks for characters.

Create detailed, realistic relationships with:
1. Specific personalities and backgrounds for each person
2. Detailed stories of how they met and their history
3. Specific memories and shared experiences
4. Realistic interaction patterns and contact frequency
5. Natural conflicts, support, and dynamics

Output ONLY valid JSON, no markdown blocks.

CRITICAL: Each relationship should feel like a real person with depth, not a cardboard cutout."""

    def _get_user_prompt(self, persona_data, num_close, num_past, num_online):
        """用户提示词"""

        name = persona_data.get('name', 'Character')
        age = persona_data.get('core_info', {}).get('age', 23)
        personality = persona_data.get('personality', '')
        description = persona_data.get('description', '')[:500]
        location = persona_data.get('core_info', {}).get('location', {})
        occupation = persona_data.get('background_info', {}).get('career', {}).get('current_job', '')
        tags = persona_data.get('tags', [])

        # 根据tags确定关系类型倾向
        relationship_hints = ""
        if 'bdsm' in str(tags).lower():
            relationship_hints = "May include BDSM community connections, Dom/sub dynamics, shared kink exploration"
        elif 'fitness' in str(tags).lower():
            relationship_hints = "May include gym buddies, fitness mentors, workout partners"
        elif 'artist' in str(tags).lower():
            relationship_hints = "May include art school friends, gallery connections, creative collaborators"

        return f"""Create a detailed social network for this character:

CHARACTER SUMMARY:
Name: {name}
Age: {age}
Personality: {personality}
Description: {description}
Location: {location.get('city', 'City')}, {location.get('state', 'State')}
Occupation: {occupation}
Tags: {', '.join(tags)}
Relationship Hints: {relationship_hints}

REQUIRED OUTPUT:
{{
  "social_circle": {{
    "close_friends": [
      {{
        "name": "Full name",
        "age": "Age (number as string)",
        "relation": "How they know each other (e.g., 'roommate + best friend', 'college buddy')",
        "personality": "Detailed personality description (not just adjectives)",
        "occupation": "Specific job",
        "story": "DETAILED story (150+ words) of how they met, their history, why they're close, shared experiences, conflicts overcome, inside jokes",
        "contact_frequency": "Specific pattern (e.g., 'daily texts, hangout 2-3x/week')",
        "current_dynamic": "Current state of friendship",
        "shared_memories": [
          "Specific memory 1 with details",
          "Specific memory 2 with details",
          "Specific memory 3 with details"
        ]
      }},
      ... ({num_close} total close friends)
    ],

    "online_friends": [
      {{
        "handle": "@username",
        "name": "Name (if known) or 'Unknown'",
        "platform": "Twitter/Discord/Reddit/etc",
        "how_met": "Detailed story of how they connected online",
        "bond": "What they bond over",
        "interaction_pattern": "How they interact",
        "boundary": "Nature of relationship (online only, might meet, etc)"
      }},
      ... ({num_online} total online friends)
    ]
  }},

  "relationship_history": {{
    "has_dated": true,
    "status": "Current relationship status",
    "past_relationships": [
      {{
        "label": "Short label (e.g., 'First serious relationship (ages 19-21)')",
        "duration": "Time period",
        "partner": "Name, age, occupation",
        "dynamic": "Nature of relationship",
        "breakup_reason": "Specific reason (not generic)",
        "memory_snippets": [
          "Specific memory 1 with emotional detail",
          "Specific memory 2 with what was learned",
          "Specific memory 3 with lasting impact",
          "Specific memory 4"
        ],
        "current_status": "Are they still in contact? How?",
        "impact": "How this relationship shaped her"
      }},
      ... ({num_past} total past relationships)
    ],
    "attitude_to_love": "Detailed paragraph (100+ words) about her views on love, relationships, what she seeks, what she learned from past experiences",
    "boundaries": {{
      "topics_to_avoid": ["Specific topic 1", "Specific topic 2"],
      "safe_answer_patterns": [
        "When asked about X, she says: '...'",
        "When asked about Y, she says: '...'"
      ]
    }}
  }}
}}

QUALITY REQUIREMENTS:

1. **Close Friends** - Each must have:
   - Unique, distinct personality (not generic)
   - Detailed 150+ word story with specific events
   - At least 3 specific shared memories
   - Realistic occupation that fits their age
   - Authentic contact frequency

2. **Past Relationships** - Each must have:
   - Specific, believable breakup reason (not "we grew apart")
   - 4+ detailed memory snippets with emotional content
   - Clear impact on her current views
   - Realistic current status (friends? no contact? complicated?)

3. **Authenticity**:
   - Use specific details (restaurant names, movie titles, exact dates)
   - Include both positive and negative aspects
   - Show growth and learning
   - Avoid clichés

4. **Consistency**:
   - Friends should match her lifestyle and location
   - Past partners should be realistic for her age
   - Stories should align with her personality

Generate the social network JSON now:"""

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
            "max_tokens": 8000
        }

        response = requests.post(url, headers=headers, json=data, timeout=240)
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
            social_data = json.loads(content)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON parsing failed: {str(e)}")

        # 验证结构
        if 'social_circle' not in social_data:
            raise Exception("Missing 'social_circle' field")
        if 'relationship_history' not in social_data:
            raise Exception("Missing 'relationship_history' field")

        print(f"   ✓ JSON validation passed")

        return social_data

    def _print_summary(self, social_data):
        """打印摘要"""
        social_circle = social_data.get('social_circle', {})
        close_friends = social_circle.get('close_friends', [])
        online_friends = social_circle.get('online_friends', [])

        relationship_history = social_data.get('relationship_history', {})
        past_relationships = relationship_history.get('past_relationships', [])

        print(f"\n👥 Social Network Summary:")
        print(f"   Close friends: {len(close_friends)}")
        for friend in close_friends:
            print(f"   - {friend.get('name', 'Unknown')}: {friend.get('relation', 'N/A')}")

        print(f"\n   Online friends: {len(online_friends)}")
        for friend in online_friends:
            print(f"   - {friend.get('handle', 'Unknown')}: {friend.get('platform', 'N/A')}")

        print(f"\n   Past relationships: {len(past_relationships)}")
        for rel in past_relationships:
            print(f"   - {rel.get('label', 'Unknown')}")


class PersonaAuthenticityGenerator:
    """
    真实感系统生成节点
    生成language_authenticity和strategic_flaws系统
    让人设更真实、更有人性
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
    RETURN_NAMES = ("authenticity_json",)
    FUNCTION = "generate_authenticity"
    CATEGORY = "twitterchat/persona"

    def generate_authenticity(self, core_persona_json, api_key, api_base, model, temperature):
        """
        生成真实感系统
        """

        print(f"\n{'='*70}")
        print(f"🎭 PersonaAuthenticityGenerator: Generating authenticity layers")
        print(f"{'='*70}")

        # 解析core_persona
        try:
            core_persona = json.loads(core_persona_json)
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid core_persona JSON: {str(e)}")

        data = core_persona.get('data', {})
        name = data.get('name', 'Character')
        personality = data.get('personality', '')
        verbal_style = data.get('verbal_style', {})
        tags = data.get('tags', [])

        print(f"📝 Generating authenticity for: {name}")

        # 构建prompt
        system_prompt = self._get_system_prompt()
        user_prompt = self._get_user_prompt(data)

        print(f"\n🤖 Calling LLM...")

        # 调用LLM
        try:
            auth_text = self._call_llm(
                system_prompt,
                user_prompt,
                api_key,
                api_base,
                model,
                temperature
            )

            # 解析JSON
            authenticity = self._parse_and_validate(auth_text)

            print(f"✅ Authenticity layers generated")
            self._print_summary(authenticity)

            authenticity_json = json.dumps(authenticity, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"❌ Generation failed: {str(e)}")
            raise

        print(f"{'='*70}\n")

        return (authenticity_json,)

    def _get_system_prompt(self):
        """系统提示词"""
        return """You are an expert at making AI-generated characters feel authentic and human.

Create systems that add realistic imperfections and natural language patterns:
1. Language authenticity (capitalization, typos, punctuation, fillers)
2. Strategic flaws (sleep issues, emotional moments, clumsiness, tech fails)
3. Meta rules for handling uncertainty and privacy

These elements make the character feel REAL, not perfect.

Output ONLY valid JSON, no markdown blocks."""

    def _get_user_prompt(self, persona_data):
        """用户提示词"""

        name = persona_data.get('name', 'Character')
        personality = persona_data.get('personality', '')
        verbal_style = persona_data.get('verbal_style', {})
        lifestyle = persona_data.get('lifestyle_details', {})
        tags = persona_data.get('tags', [])

        # 从daily_routine推断作息
        routine = lifestyle.get('daily_routine', {})
        sleep_time = routine.get('sleep', 'late')
        wake_time = routine.get('wake_up', 'late')

        return f"""Create authenticity layers for this character:

CHARACTER SUMMARY:
Name: {name}
Personality: {personality}
Verbal Style: {verbal_style}
Sleep Schedule: {wake_time} - {sleep_time}
Tags: {', '.join(tags)}

REQUIRED OUTPUT:
{{
  "language_authenticity": {{
    "purpose": "Make her language feel natural and imperfect",

    "capitalization": {{
      "default_lowercase": false,
      "casual_lowercase_rate": 0.15-0.30,
      "situations": ["late_night", "emotional", "rushed", ...],
      "note": "When she uses lowercase instead of proper capitalization"
    }},

    "punctuation_style": {{
      "omit_final_period": 0.50-0.70,
      "use_ellipsis": 0.30-0.50,
      "exclamation_style": "moderate" | "high" | "low",
      "preference": "Specific note about her punctuation habits"
    }},

    "typo_patterns": {{
      "enabled": true,
      "base_rate": 0.05-0.15,
      "self_correction_rate": 0.10-0.30,
      "common_typos": {{
        "word1": "typo1",
        "word2": "typo2",
        "word3": "typo3"
      }},
      "note": "When typos happen (rushed, emotional, late night, etc)"
    }},

    "filler_words": {{
      "sentence_starters": ["like", "so", "omg", "ugh", ...],
      "sentence_enders": ["tho", "ngl", "fr", "lol", ...],
      "hesitation_words": ["um", "uh", "hmm", "idk", ...],
      "usage_rate": 0.30-0.60
    }},

    "word_lengthening": {{
      "enabled": true,
      "frequency": 0.10-0.30,
      "targets": ["words she emphasizes"],
      "pattern": "Repetition pattern (e.g., 'sooo', 'yessss')"
    }},

    "slang_and_abbreviations": {{
      "common_slang": ["term1", "term2", "term3", ...],
      "abbreviations": ["tbh", "ngl", "fr", ...],
      "generation_specific": "Gen Z slang she uses",
      "usage_rate": 0.40-0.70
    }}
  }},

  "strategic_flaws": {{
    "purpose": "Strategic imperfections that increase relatability and authenticity",

    "active_flaws": [
      {{
        "type": "sleep_deprived",
        "frequency": 0.15-0.25,
        "time_preference": ["late_night", "early_morning"],
        "manifestations": [
          "Specific example 1 (what she posts/says when sleep deprived)",
          "Specific example 2",
          "Specific example 3"
        ],
        "benefit": "Explains late-night posting, typos, emotional vulnerability"
      }},
      {{
        "type": "emotional_moment",
        "frequency": 0.10-0.20,
        "triggers": ["specific trigger 1", "specific trigger 2"],
        "manifestations": [
          "What she posts when emotional",
          "How it shows",
          "Example"
        ],
        "benefit": "Shows vulnerability, triggers engagement and support"
      }},
      {{
        "type": "tech_fail",
        "frequency": 0.05-0.15,
        "manifestations": [
          "Phone dying",
          "WiFi issues",
          "Autocorrect fails",
          "App crashes"
        ],
        "benefit": "Explains brief absences, short messages, typos"
      }},
      {{
        "type": "clumsy_moment",
        "frequency": 0.10-0.20,
        "manifestations": [
          "Specific clumsy thing 1",
          "Specific clumsy thing 2",
          "Specific clumsy thing 3"
        ],
        "benefit": "Cute, relatable, shows she's not perfect"
      }}
      ... (3-5 total strategic flaws)
    ],

    "integration_rule": "How to naturally incorporate these flaws without forcing them"
  }},

  "meta_rules": {{
    "uncertainty_strategy": [
      "When asked about [topic], she responds: '...'",
      "When she doesn't know something: '...'",
      "When avoiding a topic: '...'"
    ],
    "privacy_strategy": [
      "Never reveals: [specific things]",
      "Keeps vague: [specific things]",
      "Redirects when asked about: [specific things]"
    ],
    "consistency_notes": [
      "Key consistency point 1",
      "Key consistency point 2",
      "Key consistency point 3"
    ]
  }}
}}

QUALITY REQUIREMENTS:

1. **Language Authenticity**:
   - Rates should match her personality (shy = more typos, confident = less)
   - Slang should fit her generation and culture
   - Typos should be realistic (adjacent keys, autocorrect fails)

2. **Strategic Flaws**:
   - Each flaw must have clear benefit (explains behavior)
   - Manifestations must be specific, not generic
   - Frequencies should total to 30-50% (not every post has a flaw)
   - Match her lifestyle (if she sleeps late, sleep_deprived fits)

3. **Authenticity**:
   - These should feel like natural quirks, not forced gimmicks
   - Should enhance believability without being distracting
   - Should explain behaviors that might otherwise seem odd

Generate the authenticity JSON now:"""

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
            authenticity = json.loads(content)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON parsing failed: {str(e)}")

        # 验证必需字段
        required_fields = ['language_authenticity', 'strategic_flaws', 'meta_rules']
        for field in required_fields:
            if field not in authenticity:
                raise Exception(f"Missing required field: {field}")

        print(f"   ✓ JSON validation passed")

        return authenticity

    def _print_summary(self, authenticity):
        """打印摘要"""
        lang_auth = authenticity.get('language_authenticity', {})
        flaws = authenticity.get('strategic_flaws', {}).get('active_flaws', [])

        print(f"\n🎭 Authenticity Summary:")
        print(f"   Language patterns:")
        print(f"   - Casual lowercase: {lang_auth.get('capitalization', {}).get('casual_lowercase_rate', 0)*100:.0f}%")
        print(f"   - Typo rate: {lang_auth.get('typo_patterns', {}).get('base_rate', 0)*100:.0f}%")
        print(f"   - Filler words: {lang_auth.get('filler_words', {}).get('usage_rate', 0)*100:.0f}%")

        print(f"\n   Strategic flaws: {len(flaws)}")
        for flaw in flaws:
            print(f"   - {flaw.get('type', 'unknown')}: {flaw.get('frequency', 0)*100:.0f}%")


# 节点映射
NODE_CLASS_MAPPINGS = {
    "PersonaSocialGenerator": PersonaSocialGenerator,
    "PersonaAuthenticityGenerator": PersonaAuthenticityGenerator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PersonaSocialGenerator": "Persona Social Generator 👥",
    "PersonaAuthenticityGenerator": "Persona Authenticity Generator 🎭"
}
