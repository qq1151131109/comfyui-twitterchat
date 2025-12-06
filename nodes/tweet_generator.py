"""Tweet generation node"""
# Use relative imports
from ..utils.llm_client import LLMClient
from ..utils.persona_utils import extract_few_shot_examples, search_character_book


class TweetGenerator:
    """Tweet Generator (combines persona + context)"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "persona": ("PERSONA",),
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "OpenAI/Claude API key"
                }),
                "api_base": ("STRING", {
                    "default": "https://api.openai.com/v1",
                    "multiline": False
                }),
                "model": ("STRING", {
                    "default": "gpt-4",
                    "multiline": False
                }),
            },
            "optional": {
                "calendar_plan": ("CALENDAR_PLAN",),  # Connect from CalendarManager
                "context": ("CONTEXT",),  # Optional!
                "is_batch_mode": ("BOOLEAN",),  # Batch mode flag (connect from CalendarManager)
                "custom_topic": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Custom topic (overrides calendar plan theme)"
                }),
                "temperature": ("FLOAT", {
                    "default": 0.85,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.05
                }),
                "custom_user_prompt_template": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "Custom user prompt template (leave empty to use default). Supports variables: {name}, {topic}, {plan_guidance}, {template_example}, {kb_info}"
                }),
                "system_prompt_override": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "⭐ Directly edit complete system prompt (leave empty for auto-generation)"
                }),
                "user_prompt_override": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "⭐ Directly edit complete user prompt (leave empty for auto-generation)"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("tweet", "scene_hint", "system_prompt", "user_prompt")
    FUNCTION = "generate"
    CATEGORY = "TwitterChat"
    DESCRIPTION = "Generate tweets and scene hints based on persona, calendar plan and context"

    def generate(self, persona, api_key, api_base, model,
                 calendar_plan=None, context=None, is_batch_mode=False, custom_topic="",
                 temperature=0.85, custom_user_prompt_template="",
                 system_prompt_override="", user_prompt_override=""):
        """
        Generate tweet and scene hint

        Args:
            persona: Character Card data
            api_key: LLM API key
            api_base: API base URL
            model: Model name
            calendar_plan: Calendar plan (optional)
            context: Context info (optional)
            is_batch_mode: Batch mode (clears real-time info like weather when True)
            custom_topic: Custom topic (overrides calendar_plan theme)
            temperature: Temperature parameter
            custom_user_prompt_template: Custom user prompt template
            system_prompt_override: Directly override system prompt (highest priority)
            user_prompt_override: Directly override user prompt (highest priority)

        Returns:
            (tweet, scene_hint, system_prompt, user_prompt) Tweet, scene, system prompt, user prompt
        """
        # If no context, use empty dict
        context = context or {}

        # If batch mode, clear real-time context info (weather, etc.)
        if is_batch_mode:
            context = self._clean_realtime_context(context)

        # If calendar_plan exists, use plan info first
        if calendar_plan:
            # custom_topic priority: user input > calendar_plan.theme
            if not custom_topic:
                custom_topic = calendar_plan.get("theme", "")
            # Add calendar_plan info to context
            context["calendar_plan"] = calendar_plan

        # Build system prompt
        system_prompt = self._build_system_prompt(persona, context)

        # Build user prompt (unified method)
        user_prompt = self._build_user_prompt(persona, context, custom_topic, calendar_plan, custom_user_prompt_template)

        # ⭐ If override provided, use override (highest priority)
        if system_prompt_override.strip():
            system_prompt = system_prompt_override
        if user_prompt_override.strip():
            user_prompt = user_prompt_override

        # Extract few-shot examples
        examples = extract_few_shot_examples(persona, max_examples=2)

        # Assemble messages
        messages = [{"role": "system", "content": system_prompt}]

        # Add few-shot
        for example in examples:
            messages.append({"role": "assistant", "content": example})

        messages.append({"role": "user", "content": user_prompt})

        # Call LLM
        try:
            llm = LLMClient(api_key, api_base, model)
            response = llm.generate(messages, temperature=temperature, max_tokens=400)

            # Parse LLM output, extract tweet and scene hint
            tweet, scene_hint = self._parse_response(response, calendar_plan)

            return (tweet, scene_hint, system_prompt, user_prompt)
        except Exception as e:
            raise RuntimeError(f"Tweet generation failed: {str(e)}")

    def _parse_response(self, response: str, calendar_plan=None) -> tuple:
        """
        Parse LLM response, extract tweet and scene hint

        Format:
        TWEET: Tweet content...
        SCENE: gym, sporty outfit
        """
        tweet = ""
        scene_hint = ""

        lines = response.strip().split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if line.startswith('TWEET:'):
                current_section = 'tweet'
                tweet = line.replace('TWEET:', '').strip()
            elif line.startswith('SCENE:'):
                current_section = 'scene'
                scene_hint = line.replace('SCENE:', '').strip()
            elif current_section == 'tweet' and line:
                tweet += '\n' + line
            elif current_section == 'scene' and line:
                scene_hint += ' ' + line

        # If not formatted, try simple split
        if not tweet and not scene_hint:
            # Assume first line is tweet, last line is scene
            parts = response.strip().split('\n')
            if len(parts) >= 2:
                tweet = '\n'.join(parts[:-1]).strip()
                scene_hint = parts[-1].strip()
            else:
                tweet = response.strip()
                scene_hint = "casual, daily life"  # Default scene

        # If scene hint is empty and calendar plan exists, use suggested scene from plan
        if not scene_hint and calendar_plan:
            scene_hint = calendar_plan.get("suggested_scene", "casual, daily life")

        return tweet.strip(), scene_hint.strip()

    def _build_system_prompt(self, persona: dict, context: dict) -> str:
        """Build system prompt"""
        data = persona["data"]
        name = data.get("name", "")

        # ===== 1. Today's context info (at the top) =====
        background_info = ""
        if context:
            date_info = context.get("date", {})
            weather_info = context.get("weather", {})

            bg_parts = []

            # Date and day of week
            if date_info.get('formatted'):
                bg_parts.append(f"Today is {date_info['formatted']}")

            # Special date (holiday/weekend)
            special_info = date_info.get('special') or date_info.get('formatted_special')
            if special_info:
                bg_parts.append(f"Special date: {special_info}")

            # Weather
            if weather_info.get('formatted'):
                bg_parts.append(f"Weather: {weather_info['formatted']}")

            if bg_parts:
                background_info = "【Today's Context】\n" + ", ".join(bg_parts) + ".\n\n"

        # ===== 2. Base persona =====
        base_system = data.get("system_prompt", "")

        # ===== 2.5 Visual profile (new: for scene generation) =====
        visual_profile = self._build_visual_profile(data)

        # ===== 3. Tweet style guidance =====
        # Tweet-specific guidance (supports new flat structure and old extensions structure)
        twitter_ext = data.get("twitter_persona") or data.get("extensions", {}).get("twitter_persona", {})
        tweet_prefs = twitter_ext.get("tweet_preferences", {})

        # ⭐ Check if persona has custom tweet style guidance
        custom_guidance = data.get("tweet_style_guide") or data.get("extensions", {}).get("tweet_style_guide", "")

        # If custom guidance exists, use it; otherwise use default
        if custom_guidance:
            style_guidance = custom_guidance
        else:
            # Default guidance (can be auto-adjusted based on persona tags)
            tags = data.get("tags", [])

            # Determine style based on tags
            if any(tag in ["cute", "innocent", "girl-next-door", "traditional"] for tag in tags):
                # Innocent/cute style
                style_guidance = """
【Tweet Style Requirements】
- Innocent girl-next-door image, warm and approachable
- Moderately suggestive but not explicit, maintain authenticity
- Share real-life details to increase relatability
- Avoid being overly commercial, keep it natural
- Express naturally like chatting, don't force interaction prompts
"""
            else:
                # Default style - open and flexible, based on persona's personality traits
                personality = data.get("personality", "")
                system_prompt_text = data.get("system_prompt", "")

                # Build dynamic style guidance based on personality traits
                style_guidance = f"""
【Tweet Style Requirements】
- Stay true to {name}'s personality: {personality}
- Follow the behavioral guidelines: {system_prompt_text[:200]}...
- Express content naturally according to character traits - no artificial limits on openness or explicitness
- Use language and topics that match the persona's comfort level and communication style
- If the persona is sexually open, embrace that fully; if shy, show that authenticity
- Share what this character would naturally share on their timeline
- Express naturally like chatting, don't force interaction prompts
- Let the persona's true voice shine through
"""

        # ===== 4. Tweet technical requirements =====
        technical_info = ""
        if tweet_prefs:
            tech_parts = []
            if tweet_prefs.get('emoji_usage'):
                tech_parts.append(f"Emoji: {tweet_prefs.get('emoji_usage')}")
            if tweet_prefs.get('avg_tweet_length'):
                tech_parts.append(f"Length: {tweet_prefs.get('avg_tweet_length')}")
            if tweet_prefs.get('hashtag_style'):
                tech_parts.append(f"Tags: {tweet_prefs.get('hashtag_style')}")

            if tech_parts:
                technical_info = "\n【Technical Requirements】\n" + " | ".join(tech_parts) + "\n"

        # ===== 5. Output format specification =====
        output_format = """
【Output Format Specification】
Your output must strictly follow this format:
TWEET: [Tweet content with emojis and hashtags]
SCENE: [Scene description in English natural paragraph]
"""

        # ===== 6. Scene description standards =====
        # Dynamically adjust scene guidance based on persona tags
        tags = data.get("tags", [])

        # Base scene description standards
        scene_guidelines = """
【Scene Description Standards】
Generate concise, specific descriptions focusing on visual impact:

⚠️ **CRITICAL - START WITH SUBJECT**:
- ✅ Always begin scene with a simple subject descriptor: "a woman", "a girl", "a young woman"
- ✅ This helps the image model understand the main subject

⚠️ **CRITICAL - DO NOT DESCRIBE CHARACTER APPEARANCE**:
- ❌ NO hair descriptions (color, style, length)
- ❌ NO facial features (eyes, lips, face shape, skin tone)
- ❌ NO body descriptions (age, height, body type)
- ✅ Character appearance is controlled by LoRA trigger words
- ✅ ONLY describe outfit, pose, lighting, atmosphere, and background

⚠️ **CRITICAL - BE CONCISE**:
- ✅ Use short, direct phrases instead of long sentences
- ✅ Focus on key visual details that matter for the image
- ❌ Avoid flowery/literary language ("like a secret indulgence", "hanging in the air")
- ❌ Avoid redundant descriptions (don't repeat the same effect multiple times)
- ✅ Target 150-250 words total

**Outfit**:
- Specific garments with materials and fit (e.g., "black lace bralette", "sheer mesh top")
- Key accessories only (collar, jewelry, footwear)
- Emphasize revealing, form-fitting, or minimal clothing

**Pose**:
- Exact body position in 1-2 short phrases
- What the pose reveals or emphasizes
- Facial expression - be specific (half-lidded gaze, playful smirk, biting lip)

**Lighting**:
- Main light source and color temperature
- One key lighting effect (highlights, shadows, glow)

**Atmosphere**:
- Overall mood in 1-2 words (seductive, playful, intimate)

**Background**:
- Location in 3-5 key details max
- Only include elements that enhance the scene

**Camera**:
- Shot type, angle, one technical detail (depth of field/focus)

【Key Principles】
✅ Specific expressions over vague terms (e.g., "half-lidded gaze" not "focused")
✅ Dynamic poses over stiff positions (e.g., "leaning forward" not "standing")
✅ Revealing clothing that shows skin and curves
✅ Lighting that enhances mood (soft/warm/dramatic)
"""

        # Add specific scene guidance based on persona tags
        if any(tag in ["bdsm", "submissive", "petplay", "masochist"] for tag in tags):
            scene_guidelines += """
【Special Guidance for BDSM/Submissive Personas】
- Collar must be prominently visible
- Submissive posture: kneeling, leaning forward, lowered gaze
- Revealing attire that shows collar and skin
- Intimate, sultry atmosphere

Example (concise):
"A woman kneeling on bedroom carpet. Black lace bralette with sheer panels, black leather collar with silver ring visible on neck, matching lace panties. Back arched, one hand tracing collar, other on thigh. Half-lidded yearning gaze, lips parted. Dim purple LED lighting with soft shadows. Intimate and sultry mood. Background: rumpled bed, plushies, gothic decor, candles. Close-up shot, low angle, shallow depth of field, 8k quality."
"""
        elif any(tag in ["cute", "innocent", "girl-next-door"] for tag in tags):
            scene_guidelines += """
【Special Guidance for Innocent/Cute Personas】
- Natural, casual poses with playful energy
- Comfortable clothing that's subtly revealing (crop tops, shorts, sundresses)
- Bright, warm lighting (natural sunlight preferred)
- Cheerful, inviting atmosphere

Example (concise):
"A girl sitting on window sill in morning sunlight. White crop top showing midriff, denim shorts. Legs tucked to side, one hand holding mug, other playing with hair. Bright playful expression, gentle smile. Natural golden sunlight through window. Cheerful atmosphere. Background: potted plants, sheer curtains. Medium shot, slight low angle, shallow depth of field, 8k quality."
"""
        else:
            # Default general guidance
            scene_guidelines += """
Example (concise):
"A woman sitting on bed edge. Black lace lingerie with sheer panels, thigh-high stockings, strappy heels, silver jewelry. Legs crossed, one hand on thigh, other in hair. Back arched, sultry half-lidded gaze, lips parted in subtle smile. Warm golden hour sunlight through curtains mixed with soft purple LED lights. Intimate and seductive mood. Background: silk sheets, vintage mirror, candles, fairy lights. Medium shot, slightly low angle, shallow depth of field, 8k quality."
"""

        scene_guidelines += """

Use concise, natural language. Short direct phrases, not long sentences. Focus on key visual details - character appearance is controlled by LoRA.

【Final Checklist】
✅ Start with subject: "A woman...", "A girl..."
✅ Target 150-250 words total
❌ NO character appearance (hair, face, skin, eyes)
❌ NO flowery language ("like a dream", "hanging in the air")
❌ NO redundant descriptions
✅ Specific expressions (half-lidded gaze, playful smirk)
✅ Dynamic poses that reveal body
✅ Revealing clothing showing skin
✅ One key lighting effect
✅ Background: 3-5 key details only
✅ Format: Subject → Outfit → Pose → Lighting → Atmosphere → Background → Camera
"""

        # Combine
        system_prompt = f"""{background_info}{base_system}
{visual_profile}
{style_guidance}{technical_info}{output_format}{scene_guidelines}

【Authenticity Core Principles - Most Important!】
This is a tweet casually posted by a real person, not carefully crafted AI content!

⚠️ **Strictly Forbidden AI Characteristics**:
1. **List-style formatting** - ❌ Don't use "1. 2. 3." or "• • •" to enumerate
   - Real people don't list things so neatly
   - If enumerating, use natural language: "xxx, then xxx, also xxx"

2. **Marketing-style interaction prompts** - ❌ Strictly forbidden expressions:
   - "What do you think?" / "Tell me in comments~" / "Anyone else like this?"
   - "Share with me~" / "Let's chat" / "Double tap to like"
   - Any deliberate prompts to drive interaction

3. **Neat structure** - ❌ Avoid:
   - Similar sentence lengths
   - Regular punctuation patterns
   - Emojis fixed at sentence ends
   - Symmetrical paragraph structure

4. **Literary descriptions** - ❌ Avoid:
   - "Each strike makes the heart more determined" (too literary)
   - "Deep soul yearning" (too exaggerated)
   - "Like... as if..." (too formal)

5. **Excessive self-analysis** - ❌ Real people don't:
   - Analyze their own psychological state in detail
   - Use psychological terminology to describe feelings
   - Fully summarize and conclude their views

✅ **Authentic Expression Techniques** (Use flexibly based on {name}'s persona):

**Sentences should be casual, not neat**:
- ✅ "Practiced again this morning...\n\nKept thinking while kneeling\n\nWish I had an owner"
- ✅ "Feeling a bit mischievous today\n\nBut no owner to punish me\n\nGuess I'll... just be good"
- ❌ "Practiced obedience postures today. Felt inner peace. Looking forward to owner's arrival." (too neat)

**Emotions should be specific, not abstract**:
- ✅ "Knees hurt from kneeling but heart feels warm"
- ✅ "See the collar and want to put it on... want to be owned so bad"
- ❌ "Heart filled with longing for submission and devotion to owner" (too abstract)

**Expression should be colloquial, not formal**:
- ✅ "Emmm don't know how to say it"
- ✅ "Kinda... like that feeling..."
- ❌ "In conclusion" / "Based on the above" (too formal)

**If expressing similar content, change it like this**:
Original AI flavor: "Mirror affirmations three times daily: 1. xxx 2. xxx 3. xxx"
Authentic version: "Recently been saying stuff to myself in the mirror... like 'I want to obey' and stuff... kinda embarrassing but feels safe somehow"

【Important Reminders】
- **Context awareness**: Understand current date, weather, holidays to ensure content fits, but don't deliberately mention in tweets (real people don't say "today XX" in every post)
- **Authentic and natural**: Like a real person casually posting on their phone, not carefully crafted marketing copy
- **Persona charm**: Show personality through genuine emotions and expression, not deliberately "attracting fans"
- **Genuine emotions**: Occasionally reveal real small emotions, annoyances, joys to increase relatability
- **Consistent tone**: Always use {name}'s voice and personality
- **No marketing**: Absolutely don't use any interaction-driving prompts, only express yourself
"""

        return system_prompt

    def _build_user_prompt(self, persona: dict, context: dict, custom_topic: str = "", calendar_plan=None, custom_template="") -> str:
        """Build user prompt (unified method, independent of topic_type)"""
        data = persona["data"]
        name = data.get("name", "")

        # If there's a calendar plan, add plan guidance
        plan_guidance = ""
        # ⭐ Extract new fields for later use in prompts
        recommended_time = ""
        mood = ""
        strategic_flaw = None

        if calendar_plan:
            keywords = calendar_plan.get("keywords", [])
            keywords_str = ", ".join(keywords) if keywords else ""

            # ⭐ Extract new fields
            recommended_time = calendar_plan.get('recommended_time', '')
            mood = calendar_plan.get('mood', '')
            strategic_flaw = calendar_plan.get('strategic_flaw')

            # Display complete calendar plan info (including topic_type for classification only)
            topic_type_display = calendar_plan.get('topic_type', '')
            plan_guidance = f"""
Today's Content Plan:"""
            if topic_type_display:
                plan_guidance += f"\n- Content Type: {topic_type_display}"

            plan_guidance += f"""
- Theme: {calendar_plan.get('theme', '')}
- Content Direction: {calendar_plan.get('content_direction', '')}
- Keywords: {keywords_str}
- Suggested Scene: {calendar_plan.get('suggested_scene', '')}
"""
            # ⭐ Add recommended time slot and mood (if available)
            if recommended_time:
                plan_guidance += f"- Recommended Time Slot: {recommended_time}\n"
            if mood:
                plan_guidance += f"- Suggested Mood: {mood}\n"
            if strategic_flaw:
                plan_guidance += f"- Today's Strategic Flaw: {strategic_flaw}\n"

            # If there's a special event, mention it
            special_event = calendar_plan.get("special_event")
            if special_event:
                plan_guidance += f"- Special Event: {special_event}\n"

        # ⭐ Extract few-shot examples from persona file
        few_shot_examples, scene_examples = self._extract_relevant_tweet_examples(persona, calendar_plan)

        examples_text = ""
        if few_shot_examples:
            examples_text = "\nReference the style and tone of these persona tweet examples (adapt flexibly, don't copy):\n"
            for i, example in enumerate(few_shot_examples, 1):
                examples_text += f"{i}. {example}\n"

        # Add scene examples (if available)
        scene_examples_text = ""
        if scene_examples:
            scene_examples_text = "\n【Reference Scene Examples】(Scene styles matching persona):\n"
            for i, scene in enumerate(scene_examples, 1):
                scene_examples_text += f"{i}. {scene}\n"

        # Search character_book (using calendar_plan keywords and custom_topic)
        search_terms = []
        if calendar_plan:
            search_terms.extend(calendar_plan.get("keywords", []))
            search_terms.append(calendar_plan.get("theme", ""))
        if custom_topic:
            search_terms.append(custom_topic)

        kb_entries = []
        for term in search_terms:
            if term:
                entries = search_character_book(persona, term)
                kb_entries.extend(entries)

        # Deduplicate
        kb_entries = list(dict.fromkeys(kb_entries))[:3]  # Max 3 entries

        kb_info = ""
        if kb_entries:
            kb_info = "\n\nRelevant Background Knowledge:\n" + "\n".join([f"- {entry}" for entry in kb_entries])

        # If custom template provided, use custom template
        if custom_template:
            user_prompt = custom_template.format(
                name=name,
                topic=custom_topic or calendar_plan.get('theme', ''),
                plan_guidance=plan_guidance,
                examples_text=examples_text,
                scene_examples_text=scene_examples_text,
                kb_info=kb_info
            )
        else:
            # Build topic description
            topic_desc = ""
            if custom_topic:
                topic_desc = f"a tweet about「{custom_topic}」"
            elif calendar_plan and calendar_plan.get('theme'):
                topic_desc = f"a tweet about「{calendar_plan.get('theme')}」"
            else:
                topic_desc = "a tweet"

            # Use simplified user prompt (general rules already in system prompt)
            user_prompt = f"""Write {topic_desc} as {name}.
{plan_guidance}
{examples_text}
{scene_examples_text}
{kb_info}

【Core Requirements】
1. Incorporate current context but don't deliberately mention it
2. Strictly follow today's content plan theme and direction
3. Maintain persona's language style and personality traits
4. Express naturally like a real person, absolutely don't force interaction
5. Use appropriate emojis and hashtags (1-3)
6. Keep length between 60-150 characters

【Special Emphasis - For This Task】
❌ Strictly forbidden: List-style formatting ("1. 2. 3." or "• • •")
❌ Strictly forbidden: Marketing-style interaction prompts ("What do you think?"/"Share with me~", etc.)
❌ Strictly forbidden: Neat symmetrical structure (real tweets are casual)
❌ Strictly forbidden: Literary expressions ("soul"/"spirit"/"like... as if", etc.)

✅ Use natural colloquial expression: Like chatting with a friend
✅ Emotions should be specific: Don't use abstract descriptions, express real feelings
✅ Sentences should be casual: Don't make every sentence neat
✅ If enumerating: Use "then"/"also" for natural transitions, don't use numbering
"""

        return user_prompt

    def _extract_relevant_tweet_examples(self, persona: dict, calendar_plan=None, max_examples: int = 3) -> tuple:
        """
        Extract relevant tweet examples and scene examples from persona file

        Args:
            persona: Persona data
            calendar_plan: Calendar plan (used for keyword matching)
            max_examples: Maximum number of examples to return

        Returns:
            (tweet_examples, scene_examples) Lists of tweet texts and scene descriptions
        """
        data = persona["data"]
        tweet_examples = []
        scene_examples = []

        # 1. Extract from twitter_scenario.tweet_examples
        twitter_scenario = data.get("twitter_scenario", {})
        tweet_examples_raw = twitter_scenario.get("tweet_examples", [])

        if not tweet_examples_raw:
            # If not found, try reading from extensions (backward compatibility)
            extensions = data.get("extensions", {})
            twitter_persona = extensions.get("twitter_persona", {})
            tweet_examples_raw = twitter_persona.get("tweet_examples", [])

        # 2. Filter examples by relevance
        relevant_examples = []

        # Extract keywords for matching
        search_keywords = set()
        if calendar_plan:
            search_keywords.update(calendar_plan.get("keywords", []))
            theme = calendar_plan.get("theme", "")
            if theme:
                search_keywords.update(theme.split())
            # Also use topic_type as search keyword
            topic_type = calendar_plan.get("topic_type", "")
            if topic_type:
                search_keywords.update(topic_type.split())

        for example in tweet_examples_raw:
            example_type = example.get("type", "")
            example_text = example.get("text", "")
            example_context = example.get("context", "")
            example_scene = example.get("scene_hint", "")

            # Calculate relevance score
            relevance_score = 0

            # If keyword matches
            example_content = f"{example_type} {example_text} {example_context}".lower()
            for keyword in search_keywords:
                if keyword and keyword.lower() in example_content:
                    relevance_score += 2

            if relevance_score > 0:
                relevant_examples.append((relevance_score, example_text, example_scene))

        # 3. Sort by relevance, take top N
        relevant_examples.sort(key=lambda x: x[0], reverse=True)
        tweet_examples = [text for _, text, _ in relevant_examples[:max_examples] if text]
        scene_examples = [scene for _, _, scene in relevant_examples[:max_examples] if scene]

        # 4. If no relevant examples found, randomly select a few
        if not tweet_examples and tweet_examples_raw:
            import random
            sample_size = min(max_examples, len(tweet_examples_raw))
            sampled = random.sample(tweet_examples_raw, sample_size)
            tweet_examples = [ex.get("text", "") for ex in sampled if ex.get("text")]
            scene_examples = [ex.get("scene_hint", "") for ex in sampled if ex.get("scene_hint")]

        return tweet_examples, scene_examples

    def _build_visual_profile(self, data: dict) -> str:
        """
        Build visual profile (for scene generation)

        Extract visual preference information from persona's lifestyle_details.favorite_things, etc.

        Args:
            data: Character Card data field

        Returns:
            Visual profile text
        """
        visual_parts = []

        # Extract from lifestyle_details.favorite_things
        lifestyle_details = data.get("lifestyle_details", {})
        favorite_things = lifestyle_details.get("favorite_things", {})

        if favorite_things:
            visual_parts.append("【Visual Profile】(Reference for scene generation)")

            # Clothing preferences
            clothing = favorite_things.get("clothing", "")
            if clothing:
                visual_parts.append(f"- Common outfits: {clothing}")

            # BDSM items
            bdsm_items = favorite_things.get("bdsm_items", "")
            if bdsm_items:
                visual_parts.append(f"- Common props: {bdsm_items}")

            # Petplay items
            petplay_items = favorite_things.get("petplay_items", "")
            if petplay_items:
                visual_parts.append(f"- Petplay elements: {petplay_items}")

            # Color preferences
            colors = favorite_things.get("colors", "")
            if colors:
                visual_parts.append(f"- Color preferences: {colors}")

            # Pain preferences (may affect marks shown in scene)
            pain_preference = favorite_things.get("pain_preference", "")
            if pain_preference:
                visual_parts.append(f"- Possible marks: marks from {pain_preference}")

        # Extract from extensions.visual_preferences (backward compatibility)
        extensions = data.get("extensions", {})
        visual_prefs = extensions.get("visual_preferences", {})
        if visual_prefs and not visual_parts:
            # If nothing extracted from new format, try old format
            visual_parts.append("【Visual Profile】")
            for key, value in visual_prefs.items():
                if value:
                    visual_parts.append(f"- {key}: {value}")

        if visual_parts:
            return "\n" + "\n".join(visual_parts) + "\n"
        else:
            return ""

    def _clean_realtime_context(self, context: dict) -> dict:
        """
        Clear real-time context information (for batch mode)

        Args:
            context: Original context

        Returns:
            Cleaned context (with weather and other real-time info removed)
        """
        cleaned_context = context.copy()

        # Clear weather information
        if "weather" in cleaned_context:
            cleaned_context["weather"] = {}

        # Keep formatted date info, but clear special and formatted_special
        if "date" in cleaned_context:
            date_info = cleaned_context["date"].copy()
            # Clear special date info (since it's pre-generated, may not be accurate)
            date_info["special"] = None
            date_info["formatted_special"] = None
            cleaned_context["date"] = date_info

        return cleaned_context


# Node registration
NODE_CLASS_MAPPINGS = {
    "TweetGenerator": TweetGenerator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TweetGenerator": "Generate Tweet"
}
