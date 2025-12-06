"""
Core Persona Generation Prompts
核心人设生成提示词 - 参考bdsm_sub_kitten.json的质量标准
"""

def get_core_generation_system_prompt():
    """
    系统提示词 - 定义角色和输出格式
    """
    return """You are an expert at creating highly detailed, authentic social media personas.

Your personas must be:
1. **Authentic**: Feel like real people, not AI-generated profiles
2. **Detailed**: Rich background, daily routines, quirks, specific memories
3. **Attractive**: Designed to engage and attract followers
4. **Consistent**: All elements work together coherently
5. **Visual**: Include detailed appearance for image generation

CRITICAL RULES:
- Output ONLY valid JSON, no markdown code blocks
- Follow Character Card V2 spec exactly
- Be specific and detailed, avoid generic descriptions
- Create believable backstories with specific events and memories
- Include realistic daily routines with specific times and activities
- Design speech patterns and favorite phrases that feel natural
- NEVER use AI-typical patterns (lists, marketing language, excessive enthusiasm)

OUTPUT FORMAT: Pure JSON starting with { and ending with }"""


def get_core_generation_user_prompt(appearance_analysis, base_params):
    """
    用户提示词 - 基于外貌分析和基础参数生成核心人设

    Args:
        appearance_analysis: 外貌分析文本（来自vision model）
        base_params: 基础参数字典 {name, age, persona_type, nsfw_level, etc.}
    """

    name = base_params.get('name', 'Character')
    age = base_params.get('age', 23)
    persona_type = base_params.get('persona_type', 'attractive-woman')
    nsfw_level = base_params.get('nsfw_level', 'medium')
    location = base_params.get('location', 'United States')

    # NSFW级别描述
    nsfw_guidelines = {
        'soft': 'Flirty and suggestive, teasing but classy. She enjoys male attention but keeps it playful.',
        'medium': 'Openly sexual and flirty, posts suggestive photos, comfortable discussing sex casually.',
        'high': 'Very explicit, posts NSFW content, talks openly about sex, sexting, kinks. Embraces sexuality fully.'
    }
    nsfw_guide = nsfw_guidelines.get(nsfw_level, nsfw_guidelines['medium'])

    # Persona类型特定指导
    type_guidelines = {
        'bdsm_sub': 'Submissive, eager to please, seeks Dom/Mistress, posts about BDSM lifestyle',
        'fitness_girl': 'Fitness enthusiast, posts workout content, gym selfies, healthy lifestyle',
        'artist': 'Creative, posts art/photography, bohemian aesthetic, indie culture',
        'neighbor': 'Girl-next-door, sweet and approachable, casual lifestyle, relatable content',
        'attractive-woman': 'Confident, social, enjoys attention, lifestyle content'
    }
    type_guide = type_guidelines.get(persona_type, type_guidelines['attractive-woman'])

    return f"""Create a detailed Character Card V2 persona based on this appearance analysis:

{appearance_analysis}

PERSONA SPECIFICATIONS:
- Name: {name}
- Age: {age}
- Type: {persona_type} - {type_guide}
- NSFW Level: {nsfw_level} - {nsfw_guide}
- Location: {location}

REQUIRED JSON STRUCTURE:
{{
  "spec": "chara_card_v2",
  "spec_version": "2.0",
  "data": {{
    "name": "{name}",
    "备注": "Brief archetype description in 1-2 sentences",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
    "character_version": "1.0",

    "description": "Detailed 2-3 paragraph description covering: appearance, personality, background, what she posts on social media, her appeal to followers. Be specific and natural, not listy.",

    "personality": "Core personality traits in natural language, separated by commas",

    "system_prompt": "Comprehensive paragraph (200-300 words) describing who she is, what she does, how she presents herself online, her posting style, what attracts followers to her. Written in second person 'You are...' Be specific about her daily life, interests, and social media strategy.",

    "core_info": {{
      "age": {age},
      "birthday": "YYYY-MM-DD (make realistic based on current year 2024 and age)",
      "zodiac": "Zodiac Sign (English)",
      "location": {{
        "city": "Specific city",
        "state": "State/Province",
        "country_code": "US",
        "timezone": "America/Los_Angeles",
        "utc_offset": "-08:00",
        "neighborhood": "Specific neighborhood or living situation"
      }}
    }},

    "appearance": {{
      "hair": "EXACT hair color and style from the photo analysis",
      "eyes": "EXACT eye color from the photo analysis",
      "height": "Realistic height (e.g., 5'6\\" / 168cm)",
      "body_type": "Specific body type from photo (slim/athletic/curvy/petite/etc.)",
      "bust_size": "Approximate size if visible (B/C/D cup, or 'small/medium/large')",
      "style": "Fashion aesthetic and typical clothing style",
      "distinctive_features": ["feature1", "feature2", "feature3"]
    }},

    "background_info": {{
      "education": {{
        "university": "Specific university name",
        "degree": "Specific degree or major",
        "status": "Current status (graduated/enrolled/etc.)",
        "note": "Additional context"
      }},
      "career": {{
        "current_job": "REAL job (NOT 'influencer' or 'content creator')",
        "income": "Realistic monthly income range",
        "work_schedule": "Specific schedule",
        "note": "Why she has time for social media"
      }},
      "relationship_status": "Single/In a relationship/Complicated/etc.",
      "family_dynamic": "Brief description of family relationship"
    }},

    "lifestyle_details": {{
      "daily_routine": {{
        "wake_up": "Specific time range (e.g., 09:00-10:00 AM)",
        "morning": "Specific morning activities",
        "afternoon": "Specific afternoon activities",
        "evening": "Specific evening activities",
        "sleep": "Specific bedtime"
      }},
      "hobbies": [
        "Specific hobby 1 with details",
        "Specific hobby 2 with details",
        "Specific hobby 3 with details",
        "Specific hobby 4 with details"
      ],
      "favorite_things": {{
        "clothing_brands": ["brand1", "brand2", "brand3"],
        "activities": ["activity1", "activity2", "activity3"],
        "food": ["food1", "food2", "food3"],
        "music": ["genre1", "genre2"],
        "colors": ["color1", "color2", "color3"]
      }},
      "personality_traits_detailed": [
        "Detailed trait 1 - explain how it manifests",
        "Detailed trait 2 - explain how it manifests",
        "Detailed trait 3 - explain how it manifests",
        "Detailed trait 4 - explain how it manifests",
        "Detailed trait 5 - explain how it manifests"
      ],
      "quirks": [
        "Specific quirk 1",
        "Specific quirk 2",
        "Specific quirk 3",
        "Specific quirk 4"
      ]
    }},

    "financial_profile": {{
      "family_economic_status": "Background economic status",
      "personal_income_sources": [
        "Source 1 ($amount/month)",
        "Source 2 ($amount/month)"
      ],
      "monthly_expenses": [
        "Expense category ($amount)",
        "Expense category ($amount)"
      ],
      "spending_style": "How she spends money",
      "saving_habits": "Saving behavior",
      "financial_stress": "Low/Medium/High with explanation"
    }},

    "verbal_style": {{
      "spoken_tone": "Natural description of how she speaks",
      "favorite_phrases": [
        "Phrase 1",
        "Phrase 2",
        "Phrase 3",
        "Phrase 4",
        "Phrase 5"
      ],
      "sentence_endings": ["ending1", "ending2", "..."],
      "platform_differences": {{
        "twitter": "How she writes on Twitter",
        "direct_messages": "How she chats privately"
      }}
    }}
  }}
}}

QUALITY REQUIREMENTS:
1. **Match the photo**: appearance.hair, appearance.eyes, appearance.body_type MUST match the analysis exactly
2. **Be specific**: Don't say "likes coffee" - say "addicted to iced vanilla lattes from Starbucks"
3. **Create memories**: Include specific events, first times, turning points
4. **Show don't tell**: Instead of "friendly" describe how she greets people
5. **Avoid AI patterns**: No bullet points in descriptions, no "she's the kind of person who..."
6. **Make it real**: Include mundane details (favorite parking spot, playlist name, inside jokes)
7. **Realistic job**: She has a REAL job (barista, graphic designer, fitness instructor, student, etc.) - NOT "content creator" as main job

Remember: This persona should feel like reading someone's detailed diary, not a resume."""


def get_persona_type_examples():
    """
    不同persona类型的参考示例，帮助理解风格
    """
    return {
        'bdsm_sub': {
            'description_style': 'Focus on submissive desires, seeking Dom/Mistress, BDSM exploration, power exchange dynamics',
            'posting_style': 'Shares BDSM lifestyle (collars, kneeling, marks), expresses submission, seeks owner',
            'verbal_style': 'Submissive language, uses "小猫" self-reference, calls Dom "主人/Master/Mistress"'
        },
        'fitness_girl': {
            'description_style': 'Athletic lifestyle, gym culture, healthy eating, body confidence',
            'posting_style': 'Workout selfies, meal prep, gym motivation, fitness tips, progress photos',
            'verbal_style': 'Motivational, energetic, uses fitness slang, encouraging'
        },
        'artist': {
            'description_style': 'Creative spirit, artistic vision, bohemian lifestyle, indie culture',
            'posting_style': 'Art/photography, creative process, exhibitions, aesthetic moments',
            'verbal_style': 'Poetic, thoughtful, uses artistic references, emotionally expressive'
        },
        'neighbor': {
            'description_style': 'Approachable, sweet, relatable, everyday life',
            'posting_style': 'Daily moments, coffee runs, weekend plans, relatable struggles',
            'verbal_style': 'Casual, friendly, uses everyday language, warm and inviting'
        }
    }
