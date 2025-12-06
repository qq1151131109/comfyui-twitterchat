# Image-to-Persona Generator Guide

## 🎯 Overview

Generate complete social media persona JSON from portrait photos. The system uses Vision LLM to analyze the photo and create a Character Card V2 persona that:

- ✅ **Matches the person's actual appearance**
- ✅ **Attracts male followers naturally**
- ✅ **Includes NSFW/flirty content** (adjustable level)
- ✅ **Seems like a real person** (not OnlyFans model)
- ✅ **Provides Twitter & WhatsApp strategies**
- ✅ **English output**

## 🚀 Quick Start

### Basic Usage

```bash
cd custom_nodes/comfyui-twitterchat
python persona_from_image.py --image path/to/photo.jpg
```

That's it! The script will:
1. Analyze the portrait photo
2. Generate a matching persona
3. Save to `personas/` directory

### Specify Name

```bash
python persona_from_image.py --image photo.jpg --name "Sophia"
```

### Set NSFW Level

```bash
python persona_from_image.py --image photo.jpg --nsfw medium
```

Levels:
- `soft` - Subtle sensuality, girl-next-door
- `medium` - Moderately flirty, teasing (default)
- `high` - Openly sexual, bold content

## 📋 Requirements

### Image Requirements

**Format**: JPG, PNG, WebP, GIF

**Content**: Portrait photo showing:
- Clear face view
- Full head and shoulders (ideally)
- Good lighting
- Solo portrait (one person only)

**Recommended**:
- High resolution (1000px+)
- Natural setting or styled photoshoot
- Shows personality through pose/expression

### API Requirements

The script uses Vision-capable LLM (GPT-4 Vision or compatible).

**Default**: Pre-configured API (works out of the box)

**Custom API**: Set environment variables:
```bash
export OPENAI_API_KEY="your-key"
export OPENAI_API_BASE="https://api.example.com/v1"
```

## 🎨 What Gets Generated

### Complete Persona Package

The generated JSON includes:

#### 1. **Physical Description** (matched to photo)
```json
{
  "appearance": {
    "hair": "Long platinum blonde, wavy",
    "eyes": "Blue-gray, almond shaped",
    "body_type": "Slim athletic, toned",
    "height": "5'6\" (168cm)",
    "style": "California casual, feminine",
    "distinctive_features": ["Bright smile", "Defined cheekbones"]
  }
}
```

#### 2. **Background & Personality**
- Realistic occupation (NOT "influencer")
- Education background
- Daily routine
- Hobbies and interests
- Speech patterns and phrases

#### 3. **Twitter Strategy**
- Content distribution (innocent/flirty/lifestyle/thirst-traps)
- 10-12 tweet examples
- Posting times and frequency
- Engagement tactics

Example tweet:
```json
{
  "type": "flirty",
  "text": "why do guys always stare at me in the gym? literally just trying to do my squats 🙄💕",
  "context": "post-workout selfie in tight leggings"
}
```

#### 4. **WhatsApp Chat Persona**
- Texting style and patterns
- How she responds to compliments
- Flirting techniques
- Photo request handling
- Conversation examples

Example exchange:
```json
{
  "scenario": "Late night chat",
  "messages": [
    {"from": "him", "text": "can't stop thinking about you"},
    {"from": "her", "text": "hehe you're trouble... but i kinda like it 😈"}
  ]
}
```

#### 5. **Attraction Profile**
- What attracts men to her
- Her teasing style
- Escalation comfort level
- Subtle monetization (gifts, not selling content)

## 📸 Example Workflows

### Workflow 1: Fitness Influencer

**Photo**: Gym selfie, athletic girl in sportswear

```bash
python persona_from_image.py \
  --image gym_girl.jpg \
  --name "Kayla" \
  --nsfw medium
```

**Output**: Fitness-focused persona with workout content, healthy lifestyle, athletic aesthetic

### Workflow 2: College Student

**Photo**: Young woman in casual clothes, campus background

```bash
python persona_from_image.py \
  --image college_girl.jpg \
  --nsfw soft
```

**Output**: Student persona with campus life, study sessions, innocent-yet-cute vibe

### Workflow 3: Glamorous Type

**Photo**: Dressed up, makeup, sophisticated look

```bash
python persona_from_image.py \
  --image glam_photo.jpg \
  --name "Isabella" \
  --nsfw high
```

**Output**: Sophisticated persona with fashion focus, luxury lifestyle, confident sexuality

## 🎯 NSFW Level Details

### Soft (Innocent-Flirty)
- **Content**: 70% innocent, 30% subtly flirty
- **Style**: Girl-next-door, sweet with hints
- **Examples**:
  - "just got out of the shower... feeling fresh ☀️"
  - "trying on clothes for hours... why is it so hard?"
- **Best for**: Natural, approachable vibe

### Medium (Balanced) - DEFAULT
- **Content**: 50% lifestyle, 30% flirty, 20% suggestive
- **Style**: Confident but classy, teasing
- **Examples**:
  - "new lingerie set came in... should I show you? 👀"
  - "feeling extra naughty today... oops hehe 😈"
- **Best for**: Attracting male followers while staying classy

### High (Bold)
- **Content**: 40% sexual, 40% lifestyle, 20% innocent
- **Style**: Openly sexual but not explicit
- **Examples**:
  - "need someone to keep me warm tonight... any volunteers? 🥵"
  - "taking nude requests in DMs... for the special ones 💕"
- **Best for**: Maximum male attention, bold personality

## 🔧 Advanced Usage

### Use Specific Photo from Image Directory

```bash
python persona_from_image.py \
  --image image/keti_one__.jpg \
  --name "Katerina" \
  --output katerina_model.json
```

### Batch Process Multiple Photos

Create `batch_images.sh`:

```bash
#!/bin/bash
for img in image/*.jpg; do
  name=$(basename "$img" .jpg)
  python persona_from_image.py \
    --image "$img" \
    --output "${name}_persona.json" \
    --nsfw medium
  sleep 5  # Rate limit
done
```

### Custom API and Model

```bash
python persona_from_image.py \
  --image photo.jpg \
  --api-key "sk-your-key" \
  --api-base "https://api.openai.com/v1" \
  --model "gpt-4-vision-preview"
```

## 📊 Output Structure

### File Naming
- Auto: `{persona_name}_{image_filename}.json`
- Custom: Use `--output` flag

### File Location
```
custom_nodes/comfyui-twitterchat/personas/{filename}.json
```

### JSON Structure
```json
{
  "spec": "chara_card_v2",
  "spec_version": "2.0",
  "data": {
    "name": "...",
    "description": "...",
    "appearance": {...},
    "personality_details": {
      "public_persona": "...",
      "private_side": "...",
      "attraction_strategy": "..."
    },
    "twitter_persona": {
      "content_strategy": {...},
      "tweet_examples": [...]
    },
    "whatsapp_persona": {
      "chat_style": "...",
      "conversation_examples": [...]
    },
    "attraction_profile": {
      "what_attracts_men": [...],
      "teasing_style": "...",
      "escalation_comfort": "..."
    }
  }
}
```

## 💡 Tips for Best Results

### Photo Selection
1. **Clear facial features**: Well-lit, in-focus
2. **Shows personality**: Smile, expression, pose
3. **Indicates style**: Clothing, setting, aesthetic
4. **Single subject**: No group photos

### Good Photos ✅
- Selfie with clear face
- Professional portrait
- Full body shot showing style
- Natural setting showing lifestyle

### Avoid ❌
- Blurry or dark photos
- Group shots
- Heavy filters/editing
- Obscured face

### Name Selection
- Match ethnicity/background
- Sounds natural and real
- Easy to remember
- Not overly unique (avoid celebrity names)

### NSFW Level Selection

**Use soft if**:
- Photo is very innocent-looking
- Want slow-burn attraction
- Targeting wholesome audience

**Use medium if**:
- Photo shows confidence
- Want balanced appeal
- Targeting typical male audience (recommended)

**Use high if**:
- Photo is already suggestive
- Want maximum male attention
- Targeting adult audience

## 🚫 What NOT to Include

The generator explicitly AVOIDS:

- ❌ Mentioning OnlyFans, Patreon, paid content
- ❌ "Content creator" or "influencer" as occupation
- ❌ Explicit sexual descriptions
- ❌ References to selling nudes/videos
- ❌ Fake/unrealistic personas

Instead, it creates:

- ✅ Real occupation (student, teacher, nurse, etc.)
- ✅ Natural monetization (gifts, dinners, shopping)
- ✅ Authentic personality
- ✅ Believable lifestyle

## 🔄 Using in ComfyUI

After generating:

1. Load workflow in ComfyUI
2. **PersonaLoader** node:
   - Mode: `json_file`
   - Path: `custom_nodes/comfyui-twitterchat/personas/your_file.json`
3. Run workflow to generate tweets and images

## 🐛 Troubleshooting

### Error: "Image not found"
**Solution**: Use absolute path or verify file exists
```bash
# Check if file exists
ls -lh path/to/photo.jpg

# Use absolute path
python persona_from_image.py --image /full/path/to/photo.jpg
```

### Error: "API call failed"
**Solution**: Check API key and network
```bash
# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://www.dmxapi.cn/v1/models
```

### Output persona doesn't match photo
**Solution**:
- Use higher resolution photo
- Ensure good lighting
- Try different NSFW level
- Manually edit JSON after generation

### JSON parsing error
**Solution**:
- Retry (LLM output varies)
- Check API response in error message
- Try different model (--model flag)

## 📈 Quality Control

After generation, verify:

1. **Appearance matches photo**
   - Hair color/style correct?
   - Eye color correct?
   - Body type reasonable?

2. **Personality seems natural**
   - Speech patterns realistic?
   - Hobbies make sense?
   - Background believable?

3. **Content is attractive**
   - Tweet examples engaging?
   - Right NSFW balance?
   - WhatsApp examples natural?

4. **No red flags**
   - No OnlyFans mentions?
   - Seems like real person?
   - Not too explicit?

If anything is off, you can:
- Regenerate with different parameters
- Manually edit the JSON file
- Adjust NSFW level

## 🎓 Examples by Photo Type

### Example 1: Athletic/Fitness
**Photo**: Gym selfie, athletic build, sportswear
**Command**: `--nsfw medium`
**Result**: Fitness enthusiast, health-focused, gym lifestyle

### Example 2: Student/Young
**Photo**: Campus setting, casual clothes, book bag
**Command**: `--nsfw soft`
**Result**: College student, innocent with subtle flirt

### Example 3: Glamorous/Styled
**Photo**: Makeup, styled hair, dressy outfit
**Command**: `--nsfw high`
**Result**: Sophisticated, confident, openly flirty

### Example 4: Girl-Next-Door
**Photo**: Natural setting, simple clothes, friendly smile
**Command**: `--nsfw soft`
**Result**: Sweet, approachable, wholesome with hints

### Example 5: Beach/Summer
**Photo**: Beach setting, bikini or summer dress
**Command**: `--nsfw medium`
**Result**: Free-spirited, beach lifestyle, naturally sexy

## 🔐 Privacy & Safety

**Note**: This tool is for creating fictional personas for marketing/entertainment purposes.

**Recommendations**:
- Don't use photos of real people without permission
- Created personas are fictional characters
- Use responsibly and ethically
- Follow platform terms of service

## 🆘 Getting Help

If you encounter issues:

1. Check this guide first
2. Verify image and API configuration
3. Try with a different photo
4. Check error messages carefully
5. Manually edit generated JSON if needed

## 📚 Related Tools

- `persona_generator.py` - Generate persona from text description
- `test_generator.sh` - Test persona generation
- `PERSONA_GENERATOR_GUIDE.md` - Text-based persona guide

---

**Ready to start?**

```bash
cd custom_nodes/comfyui-twitterchat
python persona_from_image.py --image your_photo.jpg
```

Let the AI create a matching, attractive persona from any portrait! 🎭✨
