"""
Character Book and Template Nodes - Phase 3
知识库生成和模板加载节点
"""

import json
import requests
import os
import copy


class PersonaCharacterBookGenerator:
    """
    角色知识库生成节点
    基于人设生成character_book条目
    包含关键概念、关系、特殊话题的详细说明
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "persona_json": ("STRING", {
                    "forceInput": True
                }),
                "num_entries": ("INT", {
                    "default": 6,
                    "min": 3,
                    "max": 15,
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
                    "default": 0.8,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.05
                })
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("character_book_json",)
    FUNCTION = "generate_character_book"
    CATEGORY = "twitterchat/persona"

    def generate_character_book(self, persona_json, num_entries, api_key, api_base, model, temperature):
        """
        生成角色知识库
        """

        print(f"\n{'='*70}")
        print(f"📚 PersonaCharacterBookGenerator: Generating character book")
        print(f"{'='*70}")

        # 解析persona
        try:
            persona = json.loads(persona_json)
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid persona JSON: {str(e)}")

        data = persona.get('data', {})
        name = data.get('name', 'Character')
        tags = data.get('tags', [])

        print(f"📝 Generating {num_entries} knowledge entries for: {name}")

        # 识别关键概念
        key_concepts = self._identify_key_concepts(data)

        print(f"   Key concepts identified: {', '.join(key_concepts[:5])}")

        # 构建prompt
        system_prompt = self._get_system_prompt()
        user_prompt = self._get_user_prompt(data, key_concepts, num_entries)

        print(f"\n🤖 Calling LLM...")

        # 调用LLM
        try:
            book_text = self._call_llm(
                system_prompt,
                user_prompt,
                api_key,
                api_base,
                model,
                temperature
            )

            # 解析JSON
            character_book = self._parse_and_validate(book_text, name)

            print(f"✅ Character book generated")
            self._print_summary(character_book)

            book_json = json.dumps(character_book, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"❌ Generation failed: {str(e)}")
            raise

        print(f"{'='*70}\n")

        return (book_json,)

    def _identify_key_concepts(self, persona_data):
        """识别关键概念"""
        concepts = []

        tags = persona_data.get('tags', [])
        description = persona_data.get('description', '').lower()

        # 从tags提取
        for tag in tags:
            if tag.lower() in ['bdsm', 'submissive', 'dominant', 'petplay']:
                concepts.append(tag.upper())

        # 从description和其他字段提取
        keywords = {
            'bdsm': 'BDSM',
            'fitness': 'Fitness & Gym',
            'art': 'Art & Creativity',
            'college': 'College Life',
            'relationship': 'Relationships'
        }

        for keyword, concept in keywords.items():
            if keyword in description and concept not in concepts:
                concepts.append(concept)

        # 从social_circle提取重要关系
        social = persona_data.get('social_circle', {})
        close_friends = social.get('close_friends', [])
        for friend in close_friends[:2]:  # 前2个最亲密的朋友
            concepts.append(f"Friend: {friend.get('name', 'Unknown')}")

        return concepts[:10]  # 最多10个

    def _get_system_prompt(self):
        """系统提示词"""
        return """You are an expert at creating character knowledge bases.

Create detailed knowledge entries that:
1. Explain key concepts important to this character
2. Provide context for relationships and experiences
3. Define how she thinks about and uses these concepts
4. Include specific examples and memories

Each entry should be rich with detail and personality.

Output ONLY valid JSON, no markdown blocks."""

    def _get_user_prompt(self, persona_data, key_concepts, num_entries):
        """用户提示词"""

        name = persona_data.get('name', 'Character')
        personality = persona_data.get('personality', '')
        description = persona_data.get('description', '')[:500]

        # 收集相关信息
        social = persona_data.get('social_circle', {})
        relationships = persona_data.get('relationship_history', {})
        lifestyle = persona_data.get('lifestyle_details', {})

        return f"""Create a character knowledge base for this persona:

CHARACTER SUMMARY:
Name: {name}
Personality: {personality}
Description: {description}

KEY CONCEPTS TO COVER:
{chr(10).join([f"- {concept}" for concept in key_concepts])}

Additional Context:
- Friends: {', '.join([f.get('name', 'Unknown') for f in social.get('close_friends', [])[:3]])}
- Past relationships: {len(relationships.get('past_relationships', []))}
- Hobbies: {', '.join(lifestyle.get('hobbies', [])[:3])}

REQUIRED OUTPUT:
{{
  "character_book": {{
    "name": "{name}'s Knowledge Base",
    "description": "Key knowledge about {name}'s world, relationships, and important concepts",
    "entries": [
      {{
        "keys": ["keyword1", "keyword2", "keyword3"],
        "content": "DETAILED explanation (150-300 words) covering: what this concept means to her, how she experiences it, specific examples and memories, how it shapes her behavior and thoughts, why it's important to her",
        "priority": 10,
        "enabled": true
      }},
      ... ({num_entries} total entries)
    ]
  }}
}}

ENTRY TYPES TO INCLUDE:

1. **Core Concepts** (2-3 entries):
   - Main themes from tags (BDSM, fitness, art, etc.)
   - How she understands and practices these
   - Key memories and turning points
   - Current state and goals

2. **Important Relationships** (2-3 entries):
   - Closest friends with details
   - Significant past relationships
   - What these relationships taught her
   - Current dynamics

3. **Key Objects/Places** (1-2 entries):
   - Meaningful possessions
   - Important locations
   - Why they matter

QUALITY REQUIREMENTS:

1. **Detail**: Each entry 150-300 words with specific examples
2. **Personality**: Written in a way that reflects her voice and perspective
3. **Keys**: 3-6 keywords that would trigger this knowledge
4. **Priority**: 10 for most important, 8-9 for secondary, 7 for tertiary
5. **Authenticity**: Include emotions, memories, growth, contradictions

EXAMPLE ENTRY (for reference):
{{
  "keys": ["BDSM", "Dom", "sub", "submissive", "服从", "支配"],
  "content": "小猫是探索BDSM的普通大学生，天生渴望被支配和拥有。她通过网上学习了解BDSM的核心是SSC（Safe, Sane, Consensual）和RACK（Risk Aware Consensual Kink）。她知道服从不是weakness，而是她选择的trust和love language。她享受权力交换带来的安全感和归属感。她在寻找的不是abuse，而是responsible的Dom/Mistress建立mutual respect的D/s关系。她的第一个Dom是Jake，虽然是在线关系，但Jake教会了她很多...（continues with specific details）",
  "priority": 10,
  "enabled": true
}}

Generate the character book JSON now:"""

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

    def _parse_and_validate(self, content, name):
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
            book_data = json.loads(content)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON parsing failed: {str(e)}")

        # 验证结构
        if 'character_book' not in book_data:
            raise Exception("Missing 'character_book' field")

        character_book = book_data['character_book']

        if 'entries' not in character_book:
            raise Exception("Missing 'entries' field in character_book")

        entries = character_book['entries']
        if not isinstance(entries, list) or len(entries) == 0:
            raise Exception("Entries must be a non-empty array")

        print(f"   ✓ JSON validation passed")
        print(f"   ✓ Generated {len(entries)} entries")

        return character_book

    def _print_summary(self, character_book):
        """打印摘要"""
        entries = character_book.get('entries', [])

        print(f"\n📚 Character Book Summary:")
        print(f"   Total entries: {len(entries)}")

        for i, entry in enumerate(entries, 1):
            keys = entry.get('keys', [])
            content_len = len(entry.get('content', ''))
            priority = entry.get('priority', 0)

            print(f"   [{i}] Keys: {', '.join(keys[:3])}")
            print(f"       Content: {content_len} chars, Priority: {priority}")


class PersonaTemplateLoader:
    """
    模板加载节点
    加载预设的人设模板（如BDSM sub, fitness girl等）
    可以作为生成的参考或基础进行修改
    """

    @classmethod
    def INPUT_TYPES(cls):
        # 查找templates目录中的模板
        current_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(os.path.dirname(current_dir), 'templates')

        # 如果templates目录不存在，创建它
        os.makedirs(templates_dir, exist_ok=True)

        # 查找所有.json文件
        template_files = []
        if os.path.exists(templates_dir):
            template_files = [f for f in os.listdir(templates_dir) if f.endswith('.json')]

        if not template_files:
            template_files = ["(no templates found)"]

        return {
            "required": {
                "template_name": (template_files, {
                    "default": template_files[0]
                }),
                "load_mode": (["reference", "editable_copy"], {
                    "default": "reference"
                })
            },
            "optional": {
                "customize_name": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "新名字（仅editable_copy模式）"
                }),
                "customize_age": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 35,
                    "step": 1
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("template_persona_json", "template_info", "usage_guide")
    FUNCTION = "load_template"
    CATEGORY = "twitterchat/persona"

    def load_template(self, template_name, load_mode, customize_name="", customize_age=0):
        """
        加载模板
        """

        print(f"\n{'='*70}")
        print(f"📄 PersonaTemplateLoader: Loading template")
        print(f"{'='*70}")

        if template_name == "(no templates found)":
            return ("", "No templates available", "Create templates in custom_nodes/comfyui-twitterchat/templates/")

        # 查找模板文件
        current_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(os.path.dirname(current_dir), 'templates')
        template_path = os.path.join(templates_dir, template_name)

        if not os.path.exists(template_path):
            # 尝试从examples目录加载
            examples_dir = os.path.join(os.path.dirname(current_dir), 'examples')
            template_path = os.path.join(examples_dir, template_name)

            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Template not found: {template_name}")

        # 加载模板
        with open(template_path, 'r', encoding='utf-8') as f:
            template_data = json.load(f)

        data = template_data.get('data', {})
        name = data.get('name', 'Template')
        age = data.get('core_info', {}).get('age', 'N/A')
        persona_type = data.get('备注', '') or ', '.join(data.get('tags', [])[:3])

        print(f"📝 Loaded template: {name}")
        print(f"   Type: {persona_type}")
        print(f"   Age: {age}")
        print(f"   Mode: {load_mode}")

        # 根据模式处理
        if load_mode == "editable_copy":
            # 创建可编辑副本
            template_data = copy.deepcopy(template_data)

            if customize_name:
                template_data['data']['name'] = customize_name
                print(f"   → Customized name: {customize_name}")

            if customize_age > 0:
                if 'core_info' not in template_data['data']:
                    template_data['data']['core_info'] = {}
                template_data['data']['core_info']['age'] = customize_age
                print(f"   → Customized age: {customize_age}")

        template_json = json.dumps(template_data, ensure_ascii=False, indent=2)

        # 生成模板信息
        tweets = data.get('twitter_persona', {}).get('tweet_examples', [])
        has_social = 'social_circle' in data
        has_auth = 'language_authenticity' in data or 'strategic_flaws' in data
        has_book = 'character_book' in data

        template_info = f"""📄 Template: {template_name}

Original Character:
   Name: {name}
   Age: {age}
   Type: {persona_type}

Completeness:
   ✓ Core persona: Yes
   ✓ Tweets: {len(tweets)} examples
   {'✓' if has_social else '✗'} Social network: {'Yes' if has_social else 'No'}
   {'✓' if has_auth else '✗'} Authenticity layers: {'Yes' if has_auth else 'No'}
   {'✓' if has_book else '✗'} Character book: {'Yes' if has_book else 'No'}

Load Mode: {load_mode}
{'Customizations applied:' if load_mode == 'editable_copy' and (customize_name or customize_age > 0) else ''}
{f'   Name: {customize_name}' if customize_name else ''}
{f'   Age: {customize_age}' if customize_age > 0 else ''}
"""

        # 生成使用指南
        usage_guide = f"""📖 Template Usage Guide

MODE: {load_mode}

{'REFERENCE MODE - This template is loaded as a reference example.' if load_mode == 'reference' else 'EDITABLE COPY MODE - This is a customized copy you can modify.'}

How to use:

1. **As Reference**:
   - Study the structure and quality
   - Use PersonaPreview to explore different sections
   - Compare with your generated personas using PersonaQualityChecker

2. **As Starting Point** (editable_copy):
   - Customize name and age
   - Connect to PersonaTweetRegenerate to refresh tweets
   - Connect to PersonaSocialGenerator to add new relationships
   - Connect to PersonaSaver to save your customized version

3. **For Learning**:
   - Preview tweets section to see quality scene_hints
   - Study social_circle for relationship depth examples
   - Examine language_authenticity for realistic patterns

Recommended Workflows:

WORKFLOW 1 - Learn from Template:
PersonaTemplateLoader (reference) → PersonaPreview → Study structure

WORKFLOW 2 - Customize Template:
PersonaTemplateLoader (editable_copy, customize name/age)
   → PersonaTweetRegenerate (refresh some tweets)
   → PersonaSaver (save as new persona)

WORKFLOW 3 - Compare Quality:
PersonaTemplateLoader → PersonaQualityChecker
YourPersona → PersonaQualityChecker
Compare scores
"""

        print(f"\n{template_info}")
        print(f"{'='*70}\n")

        return (template_json, template_info, usage_guide)


# 节点映射
NODE_CLASS_MAPPINGS = {
    "PersonaCharacterBookGenerator": PersonaCharacterBookGenerator,
    "PersonaTemplateLoader": PersonaTemplateLoader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PersonaCharacterBookGenerator": "Persona Character Book Generator 📚",
    "PersonaTemplateLoader": "Persona Template Loader 📄"
}
