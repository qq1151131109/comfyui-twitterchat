"""
Persona Tools Nodes
人设工具节点 - 合并、质量检查等
"""

import json
import copy


class PersonaMerger:
    """
    人设合并节点
    将核心人设和推文合并成完整的Character Card V2格式
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "core_persona_json": ("STRING", {
                    "forceInput": True
                }),
                "tweets_json": ("STRING", {
                    "forceInput": True
                })
            },
            "optional": {
                "add_twitter_persona": (["yes", "no"], {
                    "default": "yes"
                })
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("complete_persona_json",)
    FUNCTION = "merge_persona"
    CATEGORY = "twitterchat/persona"

    def merge_persona(self, core_persona_json, tweets_json, add_twitter_persona="yes"):
        """
        合并核心人设和推文
        """

        print(f"\n{'='*70}")
        print(f"🔧 PersonaMerger: Merging persona components")
        print(f"{'='*70}")

        # 解析JSON
        try:
            core_persona = json.loads(core_persona_json)
            tweets = json.loads(tweets_json)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON parsing failed: {str(e)}")

        # 创建完整人设
        complete_persona = copy.deepcopy(core_persona)

        if add_twitter_persona == "yes":
            # 添加twitter_persona部分
            twitter_persona = self._create_twitter_persona(core_persona, tweets)
            complete_persona['data']['twitter_persona'] = twitter_persona

        print(f"✅ Persona merged successfully")
        print(f"   Core fields: {len(core_persona.get('data', {}).keys())}")
        print(f"   Tweets: {len(tweets)}")
        if add_twitter_persona == "yes":
            print(f"   Twitter persona added: Yes")

        complete_json = json.dumps(complete_persona, ensure_ascii=False, indent=2)

        print(f"{'='*70}\n")

        return (complete_json,)

    def _create_twitter_persona(self, core_persona, tweets):
        """创建twitter_persona结构"""

        data = core_persona.get('data', {})
        name = data.get('name', 'Character')
        tags = data.get('tags', [])

        # 生成Twitter handle
        handle_base = name.lower().replace(' ', '_')
        twitter_handle = f"@{handle_base}"

        # 生成bio（从description提取或生成）
        description = data.get('description', '')
        bio_parts = description.split('.')[:2]  # 取前两句
        bio = '. '.join(bio_parts) + '.'
        if len(bio) > 160:
            bio = bio[:157] + '...'

        # 估算follower count（根据persona类型）
        follower_ranges = {
            'bdsm_sub': (15000, 50000),
            'bdsm_dom': (20000, 60000),
            'fitness_girl': (30000, 80000),
            'artist': (10000, 40000),
            'neighbor': (5000, 20000),
            'office_worker': (3000, 15000),
            'student': (2000, 10000),
            'attractive-woman': (10000, 40000)
        }

        persona_type = data.get('备注', '').lower()
        for key in follower_ranges:
            if key in persona_type or key in str(tags).lower():
                import random
                min_f, max_f = follower_ranges[key]
                follower_count = f"{random.randint(min_f, max_f):,}"
                break
        else:
            follower_count = "15,000"

        # 分析推文内容策略
        content_strategy = self._analyze_content_strategy(tweets)

        # 构建tweet_examples
        tweet_examples = []
        for tweet in tweets:
            tweet_example = {
                "type": tweet.get('type', 'lifestyle_mundane'),
                "tweet_format": tweet.get('tweet_format', 'standard'),
                "time_segment": tweet.get('time_segment', 'afternoon'),
                "mood": tweet.get('mood', ''),
                "strategic_flaw": tweet.get('strategic_flaw'),
                "text": tweet.get('text', ''),
                "context": tweet.get('context', ''),
                "scene_hint": tweet.get('scene_hint', '')
            }
            tweet_examples.append(tweet_example)

        twitter_persona = {
            "social_accounts": {
                "twitter_handle": twitter_handle,
                "display_name": name,
                "bio": bio,
                "follower_count": follower_count,
                "verified": False
            },
            "content_strategy": content_strategy,
            "tweet_examples": tweet_examples,
            "posting_strategy": {
                "frequency": "4-7 tweets/day",
                "best_times": [
                    "Morning (08:00-12:00) - daily routine",
                    "Afternoon (14:00-18:00) - activities",
                    "Evening prime (18:00-22:00) - visual content",
                    "Late night (22:00-03:00) - intimate/personal"
                ]
            }
        }

        return twitter_persona

    def _analyze_content_strategy(self, tweets):
        """分析推文生成内容策略"""

        # 统计类型分布
        types = {}
        for tweet in tweets:
            tweet_type = tweet.get('type', 'unknown')
            types[tweet_type] = types.get(tweet_type, 0) + 1

        total = len(tweets)
        content_strategy = {}

        for tweet_type, count in types.items():
            percentage = (count / total * 100) if total > 0 else 0
            # 生成描述（可以更详细）
            content_strategy[tweet_type] = {
                "percentage": f"{percentage:.0f}%",
                "count": count,
                "description": f"{tweet_type.replace('_', ' ').title()} content"
            }

        return content_strategy


class PersonaQualityChecker:
    """
    人设质量检查节点
    检查人设的完整性、详细程度等
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "persona_json": ("STRING", {
                    "forceInput": True
                })
            },
            "optional": {
                "reference_persona_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "参考人设路径（可选）"
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("quality_report", "missing_fields", "overall_score")
    FUNCTION = "check_quality"
    CATEGORY = "twitterchat/persona"

    def check_quality(self, persona_json, reference_persona_path=""):
        """
        检查人设质量
        """

        print(f"\n{'='*70}")
        print(f"✅ PersonaQualityChecker: Checking quality")
        print(f"{'='*70}")

        # 解析persona
        try:
            persona = json.loads(persona_json)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON parsing failed: {str(e)}")

        # 检查完整性
        completeness_score, missing = self._check_completeness(persona)

        # 检查详细程度
        depth_score = self._check_depth(persona)

        # 检查scene_hint质量
        visual_score = self._check_visual_quality(persona)

        # 检查真实感
        authenticity_score = self._check_authenticity(persona)

        # 总分
        overall_score = int((completeness_score + depth_score + visual_score + authenticity_score) / 4)

        # 生成报告
        quality_report = f"""📊 Quality Assessment Report

Overall Score: {overall_score}/100

Detailed Scores:
- Completeness: {completeness_score}/100 (required fields coverage)
- Depth: {depth_score}/100 (detail richness)
- Visual Quality: {visual_score}/100 (scene_hint quality)
- Authenticity: {authenticity_score}/100 (realness indicators)

{self._get_grade(overall_score)}

Missing Fields: {len(missing)}
{chr(10).join([f'- {f}' for f in missing[:10]])}
{"..." if len(missing) > 10 else ""}
"""

        missing_fields_str = "\n".join(missing) if missing else "None"

        print(quality_report)
        print(f"{'='*70}\n")

        return (quality_report, missing_fields_str, overall_score)

    def _check_completeness(self, persona):
        """检查完整性"""

        required_fields = [
            'spec',
            'spec_version',
            'data.name',
            'data.description',
            'data.personality',
            'data.system_prompt',
            'data.core_info',
            'data.appearance',
            'data.background_info',
            'data.lifestyle_details',
            'data.verbal_style'
        ]

        recommended_fields = [
            'data.tags',
            'data.financial_profile',
            'data.twitter_persona',
            'data.twitter_persona.tweet_examples'
        ]

        missing = []

        for field_path in required_fields + recommended_fields:
            if not self._check_field_exists(persona, field_path):
                missing.append(field_path)

        # 计算分数
        total_fields = len(required_fields) + len(recommended_fields)
        present_fields = total_fields - len(missing)
        score = int((present_fields / total_fields) * 100)

        return score, missing

    def _check_field_exists(self, obj, field_path):
        """检查嵌套字段是否存在"""
        parts = field_path.split('.')
        current = obj

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return False

        return True

    def _check_depth(self, persona):
        """检查详细程度"""

        data = persona.get('data', {})
        score = 0

        # 检查description长度
        description = data.get('description', '')
        if len(description) > 500:
            score += 25
        elif len(description) > 300:
            score += 15
        elif len(description) > 100:
            score += 5

        # 检查lifestyle_details
        lifestyle = data.get('lifestyle_details', {})
        if 'daily_routine' in lifestyle and len(lifestyle.get('daily_routine', {})) >= 4:
            score += 20
        if 'hobbies' in lifestyle and len(lifestyle.get('hobbies', [])) >= 3:
            score += 15
        if 'quirks' in lifestyle and len(lifestyle.get('quirks', [])) >= 3:
            score += 15

        # 检查verbal_style
        verbal = data.get('verbal_style', {})
        if 'favorite_phrases' in verbal and len(verbal.get('favorite_phrases', [])) >= 3:
            score += 15

        # 检查推文数量
        tweets = data.get('twitter_persona', {}).get('tweet_examples', [])
        if len(tweets) >= 14:
            score += 10

        return min(score, 100)

    def _check_visual_quality(self, persona):
        """检查scene_hint质量"""

        tweets = persona.get('data', {}).get('twitter_persona', {}).get('tweet_examples', [])

        if not tweets:
            return 0

        total_score = 0

        for tweet in tweets:
            scene_hint = tweet.get('scene_hint', '')
            word_count = len(scene_hint.split())

            # 长度分数
            if 80 <= word_count <= 150:
                total_score += 10
            elif 60 <= word_count < 80:
                total_score += 5
            elif word_count > 150:
                total_score += 7

        # 平均分
        avg_score = (total_score / len(tweets)) if tweets else 0
        return min(int(avg_score * 10), 100)

    def _check_authenticity(self, persona):
        """检查真实感"""

        score = 0

        data = persona.get('data', {})

        # 检查是否有strategic_flaws
        if 'strategic_flaws' in data:
            score += 30

        # 检查是否有language_authenticity
        if 'language_authenticity' in data:
            score += 30

        # 检查推文中是否使用strategic_flaw
        tweets = data.get('twitter_persona', {}).get('tweet_examples', [])
        flaws_used = sum(1 for t in tweets if t.get('strategic_flaw'))
        if flaws_used > 0:
            score += 20

        # 检查occupation是否真实（不是influencer/content creator）
        occupation = str(data.get('background_info', {}).get('career', {}).get('current_job', '')).lower()
        if occupation and 'influencer' not in occupation and 'content creator' not in occupation:
            score += 20

        return min(score, 100)

    def _get_grade(self, score):
        """获取评级"""
        if score >= 90:
            return "Grade: A+ (Excellent! Ready to use)"
        elif score >= 80:
            return "Grade: A (Very good, minor improvements possible)"
        elif score >= 70:
            return "Grade: B (Good, some enhancements recommended)"
        elif score >= 60:
            return "Grade: C (Acceptable, needs improvement)"
        else:
            return "Grade: D (Needs significant work)"


# 节点映射
NODE_CLASS_MAPPINGS = {
    "PersonaMerger": PersonaMerger,
    "PersonaQualityChecker": PersonaQualityChecker
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PersonaMerger": "Persona Merger 🔧",
    "PersonaQualityChecker": "Persona Quality Checker ✅"
}
