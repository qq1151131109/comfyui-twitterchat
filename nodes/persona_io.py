"""
Persona I/O Nodes
人设输入输出节点 - 保存、预览、加载
"""

import os
import json
from datetime import datetime


class PersonaSaver:
    """
    人设保存节点
    保存完整人设到JSON文件
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "persona_json": ("STRING", {
                    "forceInput": True
                }),
                "filename": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "留空自动生成（角色名_timestamp.json）"
                })
            },
            "optional": {
                "add_lora_info": (["no", "yes"], {
                    "default": "no"
                }),
                "lora_model_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "LoRA模型路径（如需添加）"
                }),
                "lora_strength": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("filepath", "success_message")
    FUNCTION = "save_persona"
    CATEGORY = "twitterchat/persona"
    OUTPUT_NODE = True

    def save_persona(self, persona_json, filename, add_lora_info="no",
                    lora_model_path="", lora_strength=1.0):
        """
        保存人设到文件
        """

        print(f"\n{'='*70}")
        print(f"💾 PersonaSaver: Saving persona")
        print(f"{'='*70}")

        # 解析persona
        try:
            persona = json.loads(persona_json)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON parsing failed: {str(e)}")

        # 添加LoRA信息（如果需要）
        if add_lora_info == "yes" and lora_model_path:
            persona['data']['lora'] = {
                "model_path": lora_model_path,
                "strength": lora_strength,
                "note": "LoRA for consistent character appearance"
            }
            print(f"   ✓ LoRA info added: {lora_model_path}")

        # 确定文件名
        if not filename or not filename.strip():
            name = persona.get('data', {}).get('name', 'persona')
            name_slug = name.lower().replace(' ', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{name_slug}_{timestamp}.json"

        if not filename.endswith('.json'):
            filename += '.json'

        # 确定保存路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        personas_dir = os.path.join(os.path.dirname(current_dir), 'personas')
        os.makedirs(personas_dir, exist_ok=True)

        filepath = os.path.join(personas_dir, filename)

        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(persona, f, ensure_ascii=False, indent=2)

        success_message = f"✅ Persona saved successfully!\n\nFile: {filename}\nPath: {filepath}\n\nUse in PersonaLoader or TweetGenerator"

        print(f"\n{success_message}")
        print(f"{'='*70}\n")

        return (filepath, success_message)


class PersonaPreview:
    """
    人设预览节点
    格式化显示人设的不同部分
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "persona_json": ("STRING", {
                    "forceInput": True
                }),
                "preview_mode": ([
                    "summary",
                    "core_info",
                    "tweets",
                    "visual",
                    "full"
                ], {
                    "default": "summary"
                })
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("preview_text",)
    FUNCTION = "preview"
    CATEGORY = "twitterchat/persona"
    OUTPUT_NODE = True

    def preview(self, persona_json, preview_mode):
        """
        预览人设
        """

        # 解析persona
        try:
            persona = json.loads(persona_json)
        except json.JSONDecodeError as e:
            return (f"❌ JSON parsing failed: {str(e)}",)

        data = persona.get('data', {})

        if preview_mode == "summary":
            preview_text = self._preview_summary(data)
        elif preview_mode == "core_info":
            preview_text = self._preview_core(data)
        elif preview_mode == "tweets":
            preview_text = self._preview_tweets(data)
        elif preview_mode == "visual":
            preview_text = self._preview_visual(data)
        elif preview_mode == "full":
            preview_text = json.dumps(persona, ensure_ascii=False, indent=2)
        else:
            preview_text = self._preview_summary(data)

        print(f"\n{'='*70}")
        print(f"👁️  PersonaPreview: {preview_mode.upper()}")
        print(f"{'='*70}")
        print(preview_text)
        print(f"{'='*70}\n")

        return (preview_text,)

    def _preview_summary(self, data):
        """摘要预览"""

        name = data.get('name', 'N/A')
        age = data.get('core_info', {}).get('age', 'N/A')
        description = data.get('description', 'N/A')
        personality = data.get('personality', 'N/A')

        appearance = data.get('appearance', {})
        hair = appearance.get('hair', 'N/A')
        eyes = appearance.get('eyes', 'N/A')
        body_type = appearance.get('body_type', 'N/A')

        occupation = data.get('background_info', {}).get('career', {}).get('current_job', 'N/A')

        tweets = data.get('twitter_persona', {}).get('tweet_examples', [])
        tweet_count = len(tweets)

        twitter = data.get('twitter_persona', {}).get('social_accounts', {})
        handle = twitter.get('twitter_handle', 'N/A')
        followers = twitter.get('follower_count', 'N/A')

        text = f"""📋 PERSONA SUMMARY

👤 Basic Info:
   Name: {name}
   Age: {age}
   Occupation: {occupation}

💇 Appearance:
   Hair: {hair}
   Eyes: {eyes}
   Body Type: {body_type}

🎭 Personality:
   {personality}

📝 Description:
   {description[:300]}{"..." if len(description) > 300 else ""}

🐦 Twitter:
   Handle: {handle}
   Followers: {followers}
   Tweets: {tweet_count} examples generated
"""

        return text

    def _preview_core(self, data):
        """核心信息预览"""

        core_info = data.get('core_info', {})
        location = core_info.get('location', {})
        background = data.get('background_info', {})
        lifestyle = data.get('lifestyle_details', {})
        verbal = data.get('verbal_style', {})

        text = f"""📊 CORE INFORMATION

🎂 Personal:
   Age: {core_info.get('age', 'N/A')}
   Birthday: {core_info.get('birthday', 'N/A')}
   Zodiac: {core_info.get('zodiac', 'N/A')}

📍 Location:
   City: {location.get('city', 'N/A')}
   State: {location.get('state', 'N/A')}
   Timezone: {location.get('timezone', 'N/A')}
   Living: {location.get('neighborhood', 'N/A')}

🎓 Background:
   Education: {background.get('education', {}).get('degree', 'N/A')}
   University: {background.get('education', {}).get('university', 'N/A')}
   Occupation: {background.get('career', {}).get('current_job', 'N/A')}
   Income: {background.get('career', {}).get('income', 'N/A')}
   Relationship: {background.get('relationship_status', 'N/A')}

🏃 Lifestyle:
   Daily Routine:
{self._format_dict(lifestyle.get('daily_routine', {}), indent=6)}

   Hobbies:
{self._format_list(lifestyle.get('hobbies', []), indent=6)}

💬 Verbal Style:
   Tone: {verbal.get('spoken_tone', 'N/A')}
   Favorite Phrases:
{self._format_list(verbal.get('favorite_phrases', []), indent=6)}
"""

        return text

    def _preview_tweets(self, data):
        """推文预览"""

        twitter = data.get('twitter_persona', {})
        tweets = twitter.get('tweet_examples', [])

        if not tweets:
            return "❌ No tweets found in persona"

        content_strategy = twitter.get('content_strategy', {})

        text = f"""🐦 TWITTER PERSONA

📈 Content Strategy:
"""

        for content_type, stats in content_strategy.items():
            if isinstance(stats, dict):
                percentage = stats.get('percentage', 'N/A')
                description = stats.get('description', '')
                text += f"   {content_type}: {percentage} - {description}\n"

        text += f"\n📝 Tweet Examples ({len(tweets)} total):\n\n"

        for i, tweet in enumerate(tweets[:5], 1):  # 只显示前5条
            text += f"   [{i}] {tweet.get('type', 'unknown')} | {tweet.get('time_segment', 'anytime')}\n"
            text += f"       {tweet.get('text', '')[:100]}...\n"
            text += f"       Scene: {len(tweet.get('scene_hint', '').split())} words\n\n"

        if len(tweets) > 5:
            text += f"   ... and {len(tweets) - 5} more tweets\n"

        return text

    def _preview_visual(self, data):
        """视觉档案预览"""

        appearance = data.get('appearance', {})
        visual_profile = data.get('visual_profile', {})

        text = f"""👗 VISUAL PROFILE

💇 Appearance:
   Hair: {appearance.get('hair', 'N/A')}
   Eyes: {appearance.get('eyes', 'N/A')}
   Height: {appearance.get('height', 'N/A')}
   Body Type: {appearance.get('body_type', 'N/A')}
   Style: {appearance.get('style', 'N/A')}
   Features: {', '.join(appearance.get('distinctive_features', []))}
"""

        if visual_profile:
            text += f"\n🎨 Visual Style Guide:\n"
            text += f"   Common Outfits:\n{self._format_list(visual_profile.get('common_outfits', []), indent=6)}\n"
            text += f"   Common Props:\n{self._format_list(visual_profile.get('common_props', []), indent=6)}\n"
            text += f"   Color Preferences: {', '.join(visual_profile.get('color_preferences', []))}\n"
            text += f"   Lighting: {', '.join(visual_profile.get('lighting_preferences', []))}\n"

        # 显示几个scene_hint示例
        tweets = data.get('twitter_persona', {}).get('tweet_examples', [])
        if tweets:
            text += f"\n📸 Scene Hint Examples:\n\n"
            for i, tweet in enumerate(tweets[:3], 1):
                scene_hint = tweet.get('scene_hint', '')
                text += f"   [{i}] {tweet.get('type', 'unknown')}:\n"
                text += f"       {scene_hint[:150]}...\n\n"

        return text

    def _format_dict(self, d, indent=0):
        """格式化字典"""
        lines = []
        for key, value in d.items():
            lines.append(f"{' '*indent}- {key}: {value}")
        return '\n'.join(lines) if lines else f"{' '*indent}(empty)"

    def _format_list(self, lst, indent=0):
        """格式化列表"""
        lines = []
        for item in lst:
            lines.append(f"{' '*indent}- {item}")
        return '\n'.join(lines) if lines else f"{' '*indent}(empty)"


class PersonaLoaderEnhanced:
    """
    增强的人设加载节点
    支持加载现有人设并分解为多个输出
    """

    @classmethod
    def INPUT_TYPES(cls):
        personas_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'personas')
        os.makedirs(personas_dir, exist_ok=True)

        persona_files = [f for f in os.listdir(personas_dir) if f.endswith('.json')]
        if not persona_files:
            persona_files = ["(no personas found)"]

        return {
            "required": {
                "persona_file": (persona_files, {
                    "default": persona_files[0] if persona_files else ""
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("persona_json", "system_prompt", "tweet_examples_json", "summary")
    FUNCTION = "load_persona"
    CATEGORY = "twitterchat/persona"

    def load_persona(self, persona_file):
        """
        加载人设
        """

        if persona_file == "(no personas found)":
            return ("", "No persona loaded", "[]", "No personas available")

        print(f"\n{'='*70}")
        print(f"📂 PersonaLoaderEnhanced: Loading persona")
        print(f"{'='*70}")

        personas_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'personas')
        filepath = os.path.join(personas_dir, persona_file)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Persona file not found: {filepath}")

        # 加载JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            persona = json.load(f)

        data = persona.get('data', {})

        # 提取system_prompt
        system_prompt = data.get('system_prompt', '')

        # 提取tweet_examples
        tweet_examples = data.get('twitter_persona', {}).get('tweet_examples', [])
        tweet_examples_json = json.dumps(tweet_examples, ensure_ascii=False, indent=2)

        # 生成摘要
        name = data.get('name', 'Unknown')
        age = data.get('core_info', {}).get('age', 'N/A')
        description = data.get('description', '')[:200]

        summary = f"""Loaded: {name} ({age} years old)
Description: {description}...
Tweets: {len(tweet_examples)} examples
File: {persona_file}"""

        persona_json = json.dumps(persona, ensure_ascii=False, indent=2)

        print(f"   ✓ Loaded: {name}")
        print(f"   ✓ Tweets: {len(tweet_examples)}")
        print(f"{'='*70}\n")

        return (persona_json, system_prompt, tweet_examples_json, summary)


# 节点映射
NODE_CLASS_MAPPINGS = {
    "PersonaSaver": PersonaSaver,
    "PersonaPreview": PersonaPreview,
    "PersonaLoaderEnhanced": PersonaLoaderEnhanced
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PersonaSaver": "Persona Saver 💾",
    "PersonaPreview": "Persona Preview 👁️",
    "PersonaLoaderEnhanced": "Persona Loader Enhanced 📂"
}
