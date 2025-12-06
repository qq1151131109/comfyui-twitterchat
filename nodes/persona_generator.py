"""
Persona Generator Nodes
人设生成节点 - 核心人设生成和推文生成
"""

import json
import requests
import sys
import os

# 添加prompts目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
prompts_dir = os.path.join(os.path.dirname(current_dir), 'prompts')
sys.path.insert(0, prompts_dir)

from core_generation_prompt import get_core_generation_system_prompt, get_core_generation_user_prompt
from tweet_generation_prompt import get_tweet_generation_system_prompt, get_tweet_generation_user_prompt


class PersonaCoreGenerator:
    """
    核心人设生成节点
    生成人设的基础部分：基本信息、背景、外貌、性格、生活方式等
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "appearance_analysis": ("STRING", {
                    "forceInput": True  # 必须来自上游节点
                }),
                "base_params_json": ("STRING", {
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
                    "multiline": False,
                    "placeholder": "gpt-4.1, gpt-4o, claude-3-opus等"
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
    RETURN_NAMES = ("core_persona_json",)
    FUNCTION = "generate_core"
    CATEGORY = "twitterchat/persona"

    def generate_core(self, appearance_analysis, base_params_json, api_key, api_base, model, temperature):
        """
        生成核心人设
        """

        print(f"\n{'='*70}")
        print(f"🏗️  PersonaCoreGenerator: Generating core persona")
        print(f"{'='*70}")

        # 解析base_params
        try:
            base_params = json.loads(base_params_json)
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid base_params JSON: {str(e)}")

        # 构建prompts
        system_prompt = get_core_generation_system_prompt()
        user_prompt = get_core_generation_user_prompt(appearance_analysis, base_params)

        print(f"📝 Generation parameters:")
        print(f"   Model: {model}")
        print(f"   Temperature: {temperature}")
        print(f"   Name: {base_params.get('name')}")
        print(f"   Type: {base_params.get('persona_type')}")
        print(f"\n🤖 Calling LLM...")

        # 调用LLM
        try:
            core_persona_text = self._call_llm(
                system_prompt,
                user_prompt,
                api_key,
                api_base,
                model,
                temperature
            )

            # 解析并验证JSON
            core_persona = self._parse_and_validate(core_persona_text)

            print(f"✅ Core persona generated successfully")
            print(f"   Fields: {', '.join(core_persona.get('data', {}).keys())}")

            core_persona_json = json.dumps(core_persona, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"❌ Generation failed: {str(e)}")
            raise

        print(f"{'='*70}\n")

        return (core_persona_json,)

    def _call_llm(self, system_prompt, user_prompt, api_key, api_base, model, temperature):
        """调用LLM API"""

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

        response = requests.post(url, headers=headers, json=data, timeout=180)
        response.raise_for_status()

        result = response.json()
        content = result['choices'][0]['message']['content']

        return content

    def _parse_and_validate(self, content):
        """解析并验证JSON"""

        # 清理可能的markdown代码块
        content = content.strip()
        if content.startswith('```'):
            lines = content.split('\n')
            # 移除第一行和最后一行
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            content = '\n'.join(lines)

        content = content.strip()

        try:
            persona_data = json.loads(content)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON parsing failed: {str(e)}\nContent preview:\n{content[:500]}...")

        # 验证必需字段
        if 'spec' not in persona_data or persona_data['spec'] != 'chara_card_v2':
            raise Exception("Invalid Character Card V2 format: missing or incorrect 'spec' field")

        if 'data' not in persona_data:
            raise Exception("Invalid Character Card V2 format: missing 'data' field")

        data = persona_data['data']
        required_fields = ['name', 'description', 'personality', 'system_prompt']
        missing_fields = [f for f in required_fields if f not in data]

        if missing_fields:
            raise Exception(f"Missing required fields in data: {', '.join(missing_fields)}")

        print(f"   ✓ JSON validation passed")

        return persona_data


class PersonaTweetGenerator:
    """
    推文生成节点
    基于核心人设生成详细的推文示例，每个推文包含scene_hint用于图像生成
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "core_persona_json": ("STRING", {
                    "forceInput": True
                }),
                "num_tweets": ("INT", {
                    "default": 14,
                    "min": 8,
                    "max": 30,
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
                    "default": 0.9,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.05
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("tweets_json", "quality_report")
    FUNCTION = "generate_tweets"
    CATEGORY = "twitterchat/persona"

    def generate_tweets(self, core_persona_json, num_tweets, api_key, api_base, model, temperature):
        """
        生成推文示例
        """

        print(f"\n{'='*70}")
        print(f"🐦 PersonaTweetGenerator: Generating tweets")
        print(f"{'='*70}")

        # 解析core_persona
        try:
            core_persona = json.loads(core_persona_json)
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid core_persona JSON: {str(e)}")

        # 构建prompts
        system_prompt = get_tweet_generation_system_prompt()
        user_prompt = get_tweet_generation_user_prompt(core_persona, num_tweets)

        print(f"📝 Generation parameters:")
        print(f"   Model: {model}")
        print(f"   Temperature: {temperature}")
        print(f"   Number of tweets: {num_tweets}")
        print(f"\n🤖 Calling LLM...")

        # 调用LLM
        try:
            tweets_text = self._call_llm(
                system_prompt,
                user_prompt,
                api_key,
                api_base,
                model,
                temperature
            )

            # 解析并验证
            tweets = self._parse_and_validate(tweets_text, num_tweets)

            # 生成质量报告
            quality_report = self._generate_quality_report(tweets)

            print(f"✅ Tweets generated successfully")
            print(f"\n{quality_report}")

            tweets_json = json.dumps(tweets, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"❌ Generation failed: {str(e)}")
            raise

        print(f"{'='*70}\n")

        return (tweets_json, quality_report)

    def _call_llm(self, system_prompt, user_prompt, api_key, api_base, model, temperature):
        """调用LLM API"""

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
            "max_tokens": 12000
        }

        response = requests.post(url, headers=headers, json=data, timeout=240)
        response.raise_for_status()

        result = response.json()
        content = result['choices'][0]['message']['content']

        return content

    def _parse_and_validate(self, content, expected_count):
        """解析并验证tweets JSON"""

        # 清理markdown代码块
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
            tweets = json.loads(content)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON parsing failed: {str(e)}\nContent preview:\n{content[:500]}...")

        # 验证是否为数组
        if not isinstance(tweets, list):
            raise Exception("Tweets must be an array")

        if len(tweets) == 0:
            raise Exception("No tweets generated")

        # 验证每个tweet的必需字段
        required_fields = ['type', 'tweet_format', 'time_segment', 'mood', 'text', 'context', 'scene_hint']

        for i, tweet in enumerate(tweets):
            missing = [f for f in required_fields if f not in tweet]
            if missing:
                raise Exception(f"Tweet {i} missing fields: {', '.join(missing)}")

            # 验证scene_hint长度
            scene_hint = tweet.get('scene_hint', '')
            word_count = len(scene_hint.split())
            if word_count < 70:
                print(f"   ⚠️  Tweet {i} scene_hint too short ({word_count} words, need 80+)")

        print(f"   ✓ Generated {len(tweets)} tweets")
        print(f"   ✓ JSON validation passed")

        return tweets

    def _generate_quality_report(self, tweets):
        """生成质量报告"""

        total = len(tweets)

        # 统计scene_hint长度
        scene_hints = [t.get('scene_hint', '') for t in tweets]
        word_counts = [len(sh.split()) for sh in scene_hints]
        avg_words = sum(word_counts) / len(word_counts) if word_counts else 0
        min_words = min(word_counts) if word_counts else 0
        max_words = max(word_counts) if word_counts else 0

        # 统计类型分布
        types = {}
        for t in tweets:
            tweet_type = t.get('type', 'unknown')
            types[tweet_type] = types.get(tweet_type, 0) + 1

        # 统计时间段分布
        time_segments = {}
        for t in tweets:
            segment = t.get('time_segment', 'unknown')
            time_segments[segment] = time_segments.get(segment, 0) + 1

        # 统计strategic_flaws使用
        flaws = sum(1 for t in tweets if t.get('strategic_flaw'))

        report = f"""📊 Quality Report:
   Total tweets: {total}

   Scene Hint Statistics:
   - Average length: {avg_words:.1f} words
   - Min length: {min_words} words
   - Max length: {max_words} words
   - Target: 80-150 words

   Content Type Distribution:
{chr(10).join([f"   - {k}: {v} ({v/total*100:.0f}%)" for k, v in types.items()])}

   Time Segment Distribution:
{chr(10).join([f"   - {k}: {v} ({v/total*100:.0f}%)" for k, v in time_segments.items()])}

   Strategic Flaws: {flaws}/{total} ({flaws/total*100:.0f}%)"""

        return report


# 节点映射
NODE_CLASS_MAPPINGS = {
    "PersonaCoreGenerator": PersonaCoreGenerator,
    "PersonaTweetGenerator": PersonaTweetGenerator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PersonaCoreGenerator": "Persona Core Generator 🏗️",
    "PersonaTweetGenerator": "Persona Tweet Generator 🐦"
}
