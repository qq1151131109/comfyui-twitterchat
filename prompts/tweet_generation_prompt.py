"""
Tweet Generation Prompts
推文生成提示词 - 参考bdsm_sub_kitten.json的推文质量标准
"""

def get_tweet_generation_system_prompt():
    """
    系统提示词 - 定义推文生成的核心原则
    """
    return """You are an expert at creating authentic, engaging social media content.

Your tweets must be:
1. **Authentic**: Sound like a real person, NOT AI-generated
2. **Diverse**: Cover different moods, times, situations, content types
3. **Visual**: Each tweet has detailed scene_hint for image generation
4. **Strategic**: Follow content distribution and time-based patterns
5. **Engaging**: Designed to attract attention and interaction

AUTHENTICITY RULES (CRITICAL):
❌ NEVER use:
- List-style content ("Here are 5 things...")
- Marketing language ("Don't miss out!", "Join me!")
- Overly enthusiastic punctuation ("!!!", "😍😍😍")
- Generic influencer phrases ("Living my best life", "Blessed")
- Hashtag spam (#goals #vibes #aesthetic #lifestyle)

✅ ALWAYS use:
- Natural, conversational language
- Personal thoughts and feelings
- Specific, mundane details
- Realistic imperfections (typos occasionally, incomplete thoughts)
- 2-3 hashtags MAX, and only when natural

SCENE_HINT QUALITY RULES (CRITICAL):
Each scene_hint must be:
- **80-150 words** in natural paragraph format (NOT bullet points)
- **Detailed outfit description**: Specific clothing items, colors, fit, accessories
- **Body language & pose**: Specific positioning, avoid "standing" or "sitting" - describe HOW
- **Facial expression**: Specific emotion, avoid "smiling" - describe the type of smile/expression
- **Location & environment**: Specific room/place with details
- **Lighting**: Specific light source, color, mood
- **Camera angle**: Close-up/medium/full body, focus point
- **Atmosphere**: Overall mood and feeling

❌ BAD scene_hint example:
"Woman in bedroom, wearing lingerie, smiling, good lighting"

✅ GOOD scene_hint example:
"Late evening in her apartment bedroom, soft warm lighting from bedside lamp casting gentle shadows, woman sitting on edge of unmade bed wearing oversized grey t-shirt that slips off one shoulder revealing bare skin underneath, black lace panties barely visible, legs crossed casually, one hand playing with the hem of the shirt, expression playful and inviting with slight knowing smile, intimate close-up shot with blurred background, cozy and sensual atmosphere"

ATTRACTIVENESS GUIDANCE:
- **Expression**: Avoid blank/stiff faces - use "playful gaze", "vulnerable expression", "confident smirk"
- **Body language**: Avoid rigid poses - use "body slightly arched", "leaning back relaxed", "natural curve"
- **Outfit**: Emphasize fit and details - "tight yoga pants hugging curves", "loose tank top revealing sideboob"
- **Props/accessories**: Include character-relevant items (collar, sports bottle, art supplies, etc.)

OUTPUT FORMAT: Pure JSON array of tweet objects, no markdown blocks"""


def get_tweet_generation_user_prompt(core_persona, num_tweets=14):
    """
    用户提示词 - 基于核心人设生成详细推文

    Args:
        core_persona: 核心人设字典
        num_tweets: 生成推文数量（默认14条）
    """

    data = core_persona.get('data', {})
    name = data.get('name', 'Character')
    personality = data.get('personality', '')
    description = data.get('description', '')
    tags = data.get('tags', [])
    verbal_style = data.get('verbal_style', {})
    appearance = data.get('appearance', {})

    # 提取关键信息
    persona_type = 'bdsm_sub' if 'bdsm' in tags or 'submissive' in tags else \
                   'fitness_girl' if 'fitness' in tags or 'gym' in tags else \
                   'artist' if 'artist' in tags or 'creative' in tags else \
                   'attractive-woman'

    # 根据persona类型定制content distribution
    content_distributions = {
        'bdsm_sub': {
            'submission_craving': {'weight': 0.35, 'desc': '表达想被支配、想跪下、想服从的欲望'},
            'good_girl_display': {'weight': 0.25, 'desc': '展示服从、乖巧、训练成果'},
            'seeking_owner': {'weight': 0.20, 'desc': '寻找Dom/Mistress，表达需要被拥有'},
            'bdsm_lifestyle': {'weight': 0.15, 'desc': 'BDSM日常、学习、装备'},
            'playful_bratty': {'weight': 0.05, 'desc': '偶尔的小调皮，但知道后果'}
        },
        'fitness_girl': {
            'workout_motivation': {'weight': 0.30, 'desc': '健身动力、锻炼过程、progress'},
            'body_confidence': {'weight': 0.25, 'desc': '展示身材、自信、sexy gym selfies'},
            'lifestyle_healthy': {'weight': 0.20, 'desc': '健康饮食、日常routine'},
            'personal_moments': {'weight': 0.15, 'desc': '个人生活、放松时刻'},
            'flirty_teasing': {'weight': 0.10, 'desc': '性感暗示、调情'}
        },
        'artist': {
            'creative_work': {'weight': 0.30, 'desc': '创作过程、作品展示'},
            'aesthetic_moments': {'weight': 0.25, 'desc': '美学时刻、氛围照片'},
            'personal_thoughts': {'weight': 0.20, 'desc': '个人思考、情绪表达'},
            'lifestyle_artsy': {'weight': 0.15, 'desc': '艺术生活、展览、文化'},
            'subtle_sexy': {'weight': 0.10, 'desc': '含蓄的性感、艺术nude'}
        },
        'attractive-woman': {
            'lifestyle_mundane': {'weight': 0.30, 'desc': '日常生活、真实时刻'},
            'personal_emotion': {'weight': 0.25, 'desc': '情绪表达、内心想法'},
            'visual_showcase': {'weight': 0.20, 'desc': '展示照片、outfit、美照'},
            'interaction_bait': {'weight': 0.15, 'desc': '互动话题、问题、投票'},
            'flirty_content': {'weight': 0.10, 'desc': '调情、暗示、性感内容'}
        }
    }

    distribution = content_distributions.get(persona_type, content_distributions['attractive-woman'])

    # 时间段mood定义
    time_segments = {
        'morning': {
            'time': '08:00-12:00',
            'mood': 'Fresh, energetic, starting the day',
            'content_style': 'Morning routines, breakfast, plans for the day'
        },
        'afternoon': {
            'time': '12:00-18:00',
            'mood': 'Active, social, productive',
            'content_style': 'Work/study updates, activities, social moments'
        },
        'evening_prime': {
            'time': '18:00-22:00',
            'mood': 'Relaxed, visual, prime posting time',
            'content_style': 'Outfit posts, evening activities, visual content'
        },
        'late_night': {
            'time': '22:00-03:00',
            'mood': 'Intimate, vulnerable, reflective',
            'content_style': 'Personal thoughts, late night confessions, bedroom content'
        }
    }

    # Strategic flaws定义
    strategic_flaws = {
        'sleep_deprived': {
            'desc': '失眠、深夜睡不着',
            'manifestations': ['凌晨2点睡不着...', '又失眠了', '大脑不肯关机'],
            'benefit': '解释深夜发帖，增加真实感'
        },
        'emotional_moment': {
            'desc': '情绪化时刻',
            'manifestations': ['今天有点emo', '心情复杂', '想太多了'],
            'benefit': '展示vulnerability，触发共鸣'
        },
        'tech_fail': {
            'desc': '技术小故障',
            'manifestations': ['手机快没电了', '信号不好', 'autocorrect坑我'],
            'benefit': '解释typo或简短内容'
        },
        'clumsy_moment': {
            'desc': '笨拙时刻',
            'manifestations': ['又打翻了咖啡', '忘带钥匙', '走错教室'],
            'benefit': '可爱的不完美，增加亲和力'
        }
    }

    return f"""Generate {num_tweets} diverse, authentic tweets for this character:

CHARACTER SUMMARY:
Name: {name}
Personality: {personality}
Description: {description[:300]}...
Appearance: {appearance}
Verbal Style: {verbal_style}
Type: {persona_type}

CONTENT DISTRIBUTION (must follow):
{chr(10).join([f"- {k}: {v['weight']*100:.0f}% - {v['desc']}" for k, v in distribution.items()])}

TIME SEGMENTS (distribute tweets across):
{chr(10).join([f"- {k} ({v['time']}): {v['mood']}" for k, v in time_segments.items()])}

STRATEGIC FLAWS (use in 20-30% of tweets):
{chr(10).join([f"- {k}: {v['desc']}" for k, v in strategic_flaws.items()])}

REQUIRED OUTPUT FORMAT:
Return a JSON array of {num_tweets} tweet objects:

[
  {{
    "type": "submission_craving" (or other type from distribution),
    "tweet_format": "standard" | "question" | "poll",
    "time_segment": "morning" | "afternoon" | "evening_prime" | "late_night",
    "mood": "Specific mood descriptors (e.g., 'craving, vulnerable')",
    "strategic_flaw": "sleep_deprived" | "emotional_moment" | "tech_fail" | "clumsy_moment" | null,
    "text": "The actual tweet text (150 chars MAX, natural language, 2-3 hashtags MAX)",
    "context": "Why she posted this, what triggered it (1-2 sentences)",
    "scene_hint": "DETAILED 80-150 word scene description in NATURAL PARAGRAPH format including: specific outfit details, body pose/language, facial expression, location/environment, lighting (source/color/mood), atmosphere, camera angle. DO NOT describe hair/face/body type (LoRA handles that). Focus on: what she's wearing, where she is, how she's positioned, what she's doing, lighting mood. Example: 'Late evening bedroom, soft purple LED strips behind bed creating intimate glow, woman kneeling on carpet wearing black leather collar and oversized band t-shirt slipping off shoulder, black cotton panties visible, hands resting on thighs in submissive pose, expression vulnerable and longing with soft puppy eyes, close-up shot focusing on collar and face, cozy intimate atmosphere with unmade bed in blurred background'"
  }},
  ...
]

CRITICAL QUALITY REQUIREMENTS:

1. **Text Quality**:
   - Sound like a REAL person, not AI
   - NO lists, NO marketing language, NO excessive emojis
   - Include occasional typos (5-10% of tweets)
   - Use incomplete sentences sometimes ("cant sleep...")
   - Mix of uppercase/lowercase naturally
   - 2-3 hashtags MAX, only when natural

2. **Scene Hint Quality** (MOST IMPORTANT):
   - MUST be 80-150 words in NATURAL PARAGRAPH format (not bullet points)
   - Include ALL these elements:
     * Specific time/location (e.g., "Late evening in her apartment bedroom")
     * Detailed outfit (e.g., "wearing oversized grey t-shirt slipping off one shoulder, black lace panties barely visible")
     * Specific pose/body language (e.g., "sitting on edge of bed, legs crossed, one hand playing with shirt hem")
     * Detailed expression (e.g., "playful knowing smile, eyes inviting" NOT just "smiling")
     * Specific lighting (e.g., "soft warm light from bedside lamp casting gentle shadows" NOT "good lighting")
     * Camera angle (e.g., "intimate close-up shot with blurred background")
     * Atmosphere (e.g., "cozy and sensual atmosphere")
   - DO NOT describe: hair color, face shape, body type (LoRA handles appearance)
   - DO describe: outfit, accessories, pose, expression details, environment

3. **Diversity Requirements**:
   - Cover ALL content types from distribution
   - Cover ALL time segments (morning/afternoon/evening/late_night)
   - Include some strategic flaws (20-30% of tweets)
   - Variety in tweet_format (mostly standard, some questions)
   - Range of moods (happy, vulnerable, playful, confident, tired, etc.)

4. **Attractiveness Optimization**:
   - Expression: Use specific descriptions (vulnerable gaze, playful smirk, bedroom eyes, inviting smile)
   - Body language: Show curves, tension, relaxation (body slightly arched, leaning back, curves emphasized)
   - Outfit: Emphasize fit and reveal (tight, loose, slipping off, barely covering, hugging curves)
   - Props: Include character-relevant items based on persona type

5. **Persona-Specific Elements**:
   - Use character's verbal_style and favorite_phrases
   - Reference character's lifestyle_details and hobbies
   - Stay true to personality and background
   - Maintain consistent voice across all tweets

EXAMPLE TWEET STRUCTURE:

{{
  "type": "personal_emotion",
  "tweet_format": "standard",
  "time_segment": "late_night",
  "mood": "vulnerable, intimate",
  "strategic_flaw": "sleep_deprived",
  "text": "2am and my brain wont shut off... just wanna be held rn 🥺\\n\\ncant sleep nights are the worst",
  "context": "Late night insomnia, feeling lonely and vulnerable, seeking comfort",
  "scene_hint": "Dark bedroom at 2am, only light from phone screen illuminating woman's face as she lies in bed, wearing oversized ex-boyfriend's hoodie and black boy-short panties, laying on side hugging pillow against chest, expression tired and vulnerable with slight pout, messy hair spread on pillow, intimate extreme close-up shot focusing on face and eyes reflecting phone light, melancholic cozy atmosphere with unmade sheets tangled around legs"
}}

Now generate {num_tweets} tweets following ALL requirements above. Ensure scene_hints are DETAILED (80-150 words each) and tweets sound AUTHENTIC."""


def get_scene_hint_quality_guide():
    """
    Scene hint质量指导 - 好的和坏的例子
    """
    return {
        'bad_examples': [
            {
                'text': 'Woman in bedroom wearing lingerie smiling',
                'problems': [
                    'Too short (only 6 words, need 80-150)',
                    'No specific outfit details',
                    'Generic "smiling" expression',
                    'No lighting description',
                    'No pose/body language',
                    'No atmosphere'
                ]
            },
            {
                'text': 'Beautiful girl standing in room with good lighting looking at camera',
                'problems': [
                    'Too short',
                    'Describes appearance (LoRA handles that)',
                    '"Good lighting" is too vague',
                    '"Standing" is boring pose',
                    'No outfit details',
                    'No specific expression'
                ]
            }
        ],
        'good_examples': [
            {
                'text': 'Late evening in her apartment bedroom, soft warm lighting from bedside lamp casting gentle shadows, woman sitting on edge of unmade bed wearing oversized grey t-shirt that slips off one shoulder revealing bare skin underneath, black lace panties barely visible, legs crossed casually, one hand playing with the hem of the shirt, expression playful and inviting with slight knowing smile, intimate close-up shot with blurred background, cozy and sensual atmosphere',
                'strengths': [
                    '95 words - perfect length',
                    'Specific time and location',
                    'Detailed lighting (bedside lamp, warm, shadows)',
                    'Specific outfit (oversized t-shirt, how it fits, what shows)',
                    'Specific pose (sitting on edge, legs crossed, hand placement)',
                    'Specific expression (playful, inviting, knowing smile)',
                    'Camera angle (intimate close-up, blurred bg)',
                    'Atmosphere (cozy, sensual)'
                ]
            },
            {
                'text': 'Early morning gym locker room, harsh fluorescent lighting creating high contrast, woman standing in front of mirror taking selfie, wearing tight black sports bra showing underboob and high-waisted purple leggings hugging curves, post-workout glow with slight sweat on skin, one hand holding phone up, other hand on hip, expression confident with subtle smirk, body slightly turned to show side profile and curves, medium shot capturing upper body and reflection, energetic athletic atmosphere',
                'strengths': [
                    '82 words - good length',
                    'Specific location and time',
                    'Specific lighting (fluorescent, high contrast)',
                    'Detailed outfit (tight sports bra, underboob, high-waisted leggings)',
                    'Specific pose (mirror selfie, hand positions, body turn)',
                    'Specific expression (confident smirk)',
                    'Shows attractiveness (curves, post-workout glow)',
                    'Camera angle and atmosphere'
                ]
            }
        ]
    }
