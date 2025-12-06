"""
Scene Hint Enhancement and Tweet Regeneration Nodes
Scene hint增强和推文重新生成节点
"""

import json
import requests
import copy


class SceneHintEnhancer:
    """
    Scene Hint增强节点
    将简单的scene_hint扩展为80-150字的详细描述
    使用visual_profile确保一致性
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "simple_scene_hint": ("STRING", {
                    "default": "bedroom selfie",
                    "multiline": True,
                    "placeholder": "简单描述，如：bedroom selfie, gym mirror pic等"
                }),
                "persona_json": ("STRING", {
                    "forceInput": True
                }),
                "enhancement_level": (["light", "medium", "detailed"], {
                    "default": "detailed"
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

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("enhanced_scene_hint", "word_count")
    FUNCTION = "enhance_scene_hint"
    CATEGORY = "twitterchat/persona"

    def enhance_scene_hint(self, simple_scene_hint, persona_json, enhancement_level,
                          api_key, api_base, model):
        """
        增强scene hint
        """

        print(f"\n{'='*70}")
        print(f"✨ SceneHintEnhancer: Enhancing scene hint")
        print(f"{'='*70}")
        print(f"Input: {simple_scene_hint[:100]}...")
        print(f"Enhancement level: {enhancement_level}")

        # 解析persona
        try:
            persona = json.loads(persona_json)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON parsing failed: {str(e)}")

        data = persona.get('data', {})

        # 提取visual_profile和appearance
        visual_profile = data.get('visual_profile', {})
        appearance = data.get('appearance', {})
        tags = data.get('tags', [])

        # 目标字数
        target_words = {
            'light': (60, 90),
            'medium': (80, 120),
            'detailed': (100, 150)
        }.get(enhancement_level, (100, 150))

        # 构建prompt
        system_prompt = self._get_system_prompt()
        user_prompt = self._get_user_prompt(
            simple_scene_hint,
            visual_profile,
            appearance,
            tags,
            target_words
        )

        print(f"\n🤖 Calling LLM...")

        # 调用LLM
        try:
            enhanced = self._call_llm(
                system_prompt,
                user_prompt,
                api_key,
                api_base,
                model
            )

            word_count = len(enhanced.split())

            print(f"✅ Enhanced scene hint generated")
            print(f"   Words: {word_count} (target: {target_words[0]}-{target_words[1]})")
            print(f"\n📝 Result:")
            print(f"   {enhanced[:200]}...")

        except Exception as e:
            print(f"❌ Enhancement failed: {str(e)}")
            raise

        print(f"{'='*70}\n")

        return (enhanced, word_count)

    def _get_system_prompt(self):
        """系统提示词"""
        return """You are an expert at writing detailed, attractive scene descriptions for image generation.

Your descriptions must:
1. Be 80-150 words in NATURAL PARAGRAPH format (NOT bullet points)
2. Include specific details: outfit, pose, expression, lighting, atmosphere
3. Avoid describing appearance (hair/face/body type - LoRA handles that)
4. Focus on: what she's wearing, where she is, how she's positioned, lighting mood
5. Use attractive, engaging language that emphasizes appeal
6. Follow the character's visual style and persona

Output ONLY the enhanced scene description, nothing else."""

    def _get_user_prompt(self, simple_hint, visual_profile, appearance, tags, target_words):
        """用户提示词"""

        # 从visual_profile提取关键信息
        common_outfits = visual_profile.get('common_outfits', [])
        common_props = visual_profile.get('common_props', [])
        colors = visual_profile.get('color_preferences', [])
        lighting = visual_profile.get('lighting_preferences', [])
        poses = visual_profile.get('typical_poses', [])

        # 从tags确定风格
        style_indicators = []
        if 'bdsm' in ' '.join(tags).lower():
            style_indicators.append("May include BDSM elements like collars, restraints")
        if 'fitness' in ' '.join(tags).lower():
            style_indicators.append("Athletic, sporty aesthetic")
        if 'artist' in ' '.join(tags).lower():
            style_indicators.append("Artistic, aesthetic focus")

        return f"""Enhance this simple scene description into a detailed 80-150 word paragraph:

SIMPLE DESCRIPTION:
"{simple_hint}"

CHARACTER'S VISUAL STYLE:
Common Outfits: {', '.join(common_outfits[:3]) if common_outfits else 'casual, comfortable'}
Common Props: {', '.join(common_props[:5]) if common_props else 'phone, everyday items'}
Favorite Colors: {', '.join(colors[:5]) if colors else 'varied'}
Typical Lighting: {', '.join(lighting[:2]) if lighting else 'natural, warm lighting'}
Typical Poses: {', '.join(poses[:3]) if poses else 'natural, relaxed poses'}
Style Notes: {'; '.join(style_indicators) if style_indicators else 'attractive, confident'}

TARGET: {target_words[0]}-{target_words[1]} words

REQUIREMENTS:
1. Write as a NATURAL PARAGRAPH (not bullet points)
2. Include:
   - Specific time/location (e.g., "Late evening in her apartment bedroom")
   - Detailed outfit from her common styles (specific items, colors, how they fit)
   - Specific pose/body language (how she's positioned, what she's doing)
   - Detailed facial expression (specific emotion, avoid just "smiling")
   - Specific lighting (source, color, mood it creates)
   - Camera angle (close-up/medium/full, focus point)
   - Overall atmosphere

3. DO NOT describe: hair color, eye color, facial features, body type (LoRA handles these)
4. DO describe: outfit details, accessories, pose, expression nuances, environment
5. Use attractive language emphasizing appeal

EXAMPLE QUALITY:
"Late evening in her apartment bedroom, soft warm lighting from bedside lamp casting gentle shadows, woman sitting on edge of unmade bed wearing oversized grey t-shirt that slips off one shoulder revealing bare skin underneath, black lace panties barely visible, legs crossed casually, one hand playing with the hem of the shirt, expression playful and inviting with slight knowing smile, intimate close-up shot with blurred background, cozy and sensual atmosphere"

Now enhance the simple description above:"""

    def _call_llm(self, system_prompt, user_prompt, api_key, api_base, model):
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
            "temperature": 0.8,
            "max_tokens": 500
        }

        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()

        result = response.json()
        content = result['choices'][0]['message']['content'].strip()

        # 移除可能的引号
        if content.startswith('"') and content.endswith('"'):
            content = content[1:-1]

        return content


class PersonaTweetRegenerate:
    """
    推文重新生成节点
    选择性地重新生成特定索引的推文，保持其他推文不变
    可以使用新的策略或保持原有策略
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "persona_json": ("STRING", {
                    "forceInput": True
                }),
                "tweet_indices": ("STRING", {
                    "default": "0,5,12",
                    "multiline": False,
                    "placeholder": "要重新生成的推文索引（逗号分隔，如：0,5,12）"
                }),
                "regenerate_mode": (["replace", "enhance_scene_hint_only"], {
                    "default": "replace"
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
                    "default": 0.9,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.05
                })
            },
            "optional": {
                "strategy_json": ("STRING", {
                    "default": "",
                    "multiline": False
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("updated_persona_json", "regeneration_report")
    FUNCTION = "regenerate_tweets"
    CATEGORY = "twitterchat/persona"

    def regenerate_tweets(self, persona_json, tweet_indices, regenerate_mode,
                         api_key, api_base, model, temperature, strategy_json=""):
        """
        重新生成指定的推文
        """

        print(f"\n{'='*70}")
        print(f"🔄 PersonaTweetRegenerate: Regenerating tweets")
        print(f"{'='*70}")

        # 解析persona
        try:
            persona = json.loads(persona_json)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON parsing failed: {str(e)}")

        # 解析索引
        try:
            indices = [int(i.strip()) for i in tweet_indices.split(',') if i.strip()]
        except ValueError as e:
            raise Exception(f"Invalid indices format: {str(e)}")

        data = persona.get('data', {})
        tweets = data.get('twitter_persona', {}).get('tweet_examples', [])

        if not tweets:
            raise Exception("No tweets found in persona")

        # 验证索引
        invalid_indices = [i for i in indices if i < 0 or i >= len(tweets)]
        if invalid_indices:
            raise Exception(f"Invalid indices (out of range): {invalid_indices}")

        print(f"📝 Regenerating {len(indices)} tweets: {indices}")
        print(f"   Mode: {regenerate_mode}")
        print(f"   Total tweets: {len(tweets)}")

        # 根据模式处理
        if regenerate_mode == "replace":
            updated_tweets, report = self._regenerate_full_tweets(
                indices, tweets, data, strategy_json,
                api_key, api_base, model, temperature
            )
        else:  # enhance_scene_hint_only
            updated_tweets, report = self._enhance_scene_hints_only(
                indices, tweets, data,
                api_key, api_base, model
            )

        # 更新persona
        updated_persona = copy.deepcopy(persona)
        updated_persona['data']['twitter_persona']['tweet_examples'] = updated_tweets

        updated_json = json.dumps(updated_persona, ensure_ascii=False, indent=2)

        print(f"\n{report}")
        print(f"{'='*70}\n")

        return (updated_json, report)

    def _regenerate_full_tweets(self, indices, original_tweets, persona_data, strategy_json,
                               api_key, api_base, model, temperature):
        """完全重新生成推文"""

        # 导入prompt
        import sys
        import os
        prompts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'prompts')
        sys.path.insert(0, prompts_dir)

        from tweet_generation_prompt import get_tweet_generation_system_prompt, get_tweet_generation_user_prompt

        # 构建core_persona格式
        core_persona = {
            'data': persona_data
        }

        # 对于每个索引，生成新推文
        updated_tweets = original_tweets.copy()
        regenerated_count = 0

        for idx in indices:
            old_tweet = original_tweets[idx]
            old_type = old_tweet.get('type', 'lifestyle_mundane')
            old_time = old_tweet.get('time_segment', 'afternoon')

            print(f"\n   Regenerating tweet {idx} ({old_type}, {old_time})...")

            # 生成1条同类型、同时段的新推文
            system_prompt = get_tweet_generation_system_prompt()

            # 简化的user prompt，只生成1条
            user_prompt = f"""Generate 1 tweet for this character matching these specifications:

CHARACTER: {persona_data.get('name', 'Character')}
REQUIRED TYPE: {old_type}
REQUIRED TIME SEGMENT: {old_time}

Use the full persona details to generate an authentic tweet with detailed scene_hint (80-150 words).

Return JSON array with 1 tweet object."""

            # 调用LLM
            try:
                url = f"{api_base.rstrip('/')}/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                data_req = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": temperature,
                    "max_tokens": 1500
                }

                response = requests.post(url, headers=headers, json=data_req, timeout=120)
                response.raise_for_status()
                result = response.json()
                content = result['choices'][0]['message']['content']

                # 解析
                content = content.strip()
                if content.startswith('```'):
                    lines = content.split('\n')
                    if lines[0].startswith('```'):
                        lines = lines[1:]
                    if lines and lines[-1].strip() == '```':
                        lines = lines[:-1]
                    content = '\n'.join(lines)

                new_tweets = json.loads(content.strip())
                if isinstance(new_tweets, list) and len(new_tweets) > 0:
                    updated_tweets[idx] = new_tweets[0]
                    regenerated_count += 1
                    print(f"      ✓ Regenerated successfully")
                else:
                    print(f"      ✗ Failed to parse new tweet")

            except Exception as e:
                print(f"      ✗ Error: {str(e)}")

        report = f"""✅ Tweet Regeneration Complete

Regenerated: {regenerated_count}/{len(indices)} tweets
Indices: {indices}
Mode: Full replacement
"""

        return updated_tweets, report

    def _enhance_scene_hints_only(self, indices, original_tweets, persona_data,
                                  api_key, api_base, model):
        """只增强scene_hint，保持推文文本不变"""

        updated_tweets = original_tweets.copy()
        enhanced_count = 0

        for idx in indices:
            old_tweet = original_tweets[idx].copy()
            old_scene_hint = old_tweet.get('scene_hint', '')

            print(f"\n   Enhancing scene_hint for tweet {idx}...")

            # 使用SceneHintEnhancer的逻辑
            visual_profile = persona_data.get('visual_profile', {})
            appearance = persona_data.get('appearance', {})
            tags = persona_data.get('tags', [])

            # 构建简化的增强prompt
            system_prompt = """Enhance this scene description to 80-150 words. Keep it as a natural paragraph.
Output ONLY the enhanced description."""

            user_prompt = f"""Original: {old_scene_hint}

Enhance to 80-150 words with specific details:
- Outfit specifics
- Pose details
- Expression nuances
- Lighting specifics
- Atmosphere

Enhanced description:"""

            try:
                url = f"{api_base.rstrip('/')}/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                data_req = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.8,
                    "max_tokens": 500
                }

                response = requests.post(url, headers=headers, json=data_req, timeout=60)
                response.raise_for_status()
                result = response.json()
                enhanced = result['choices'][0]['message']['content'].strip()

                # 移除引号
                if enhanced.startswith('"') and enhanced.endswith('"'):
                    enhanced = enhanced[1:-1]

                old_tweet['scene_hint'] = enhanced
                updated_tweets[idx] = old_tweet
                enhanced_count += 1

                word_count = len(enhanced.split())
                print(f"      ✓ Enhanced ({word_count} words)")

            except Exception as e:
                print(f"      ✗ Error: {str(e)}")

        report = f"""✅ Scene Hint Enhancement Complete

Enhanced: {enhanced_count}/{len(indices)} tweets
Indices: {indices}
Mode: Scene hint only (text unchanged)
"""

        return updated_tweets, report


# 节点映射
NODE_CLASS_MAPPINGS = {
    "SceneHintEnhancer": SceneHintEnhancer,
    "PersonaTweetRegenerate": PersonaTweetRegenerate
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SceneHintEnhancer": "Scene Hint Enhancer ✨",
    "PersonaTweetRegenerate": "Persona Tweet Regenerate 🔄"
}
