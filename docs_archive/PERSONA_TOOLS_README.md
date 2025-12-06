# Persona Generation Tools - Complete Guide

This directory contains two powerful tools for generating Character Card V2 personas:

## 🎭 Tools Overview

| Tool | Input | Best For | Output |
|------|-------|----------|--------|
| **persona_generator.py** | Text description | Custom personas, specific requirements | Text-based persona |
| **persona_from_image.py** | Portrait photo | Matching real appearance, visual consistency | Image-matched persona |

---

## 📸 persona_from_image.py - Generate from Photos

**Use this when**: You have a portrait photo and want a persona that matches the appearance.

### Quick Start

```bash
# Basic usage
python persona_from_image.py --image path/to/photo.jpg

# With name
python persona_from_image.py --image photo.jpg --name "Sophia"

# Set NSFW level
python persona_from_image.py --image photo.jpg --nsfw medium
```

### Features

- ✅ **Analyzes photo appearance**: Hair, eyes, body type, style
- ✅ **Matches personality to look**: Creates fitting persona
- ✅ **NSFW levels**: soft/medium/high
- ✅ **Twitter strategy**: 10-12 tweet examples
- ✅ **WhatsApp chat guide**: Conversation patterns
- ✅ **Attraction profile**: Male follower strategy
- ✅ **English output**: All content in English
- ✅ **Real person vibe**: No OnlyFans mentions

### NSFW Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| `soft` | Innocent-flirty, girl-next-door | Sweet, approachable |
| `medium` | Balanced, teasing but classy | **Default** - Most versatile |
| `high` | Openly sexual, bold content | Maximum male attention |

### Test It

```bash
# Run test with sample image
./test_image_generator.sh

# Generate from multiple images
./demo_image_personas.sh
```

### Sample Images Available

The `image/` directory contains 13 sample portrait photos:
- `keti_one__.jpg`
- `hollyjai.jpg`
- `jazmynmakenna.jpg`
- `chloemariedub.jpg`
- And 9 more...

Try any of them:
```bash
python persona_from_image.py --image image/hollyjai.jpg --nsfw medium
```

### 📖 Full Documentation

See [IMAGE_PERSONA_GUIDE.md](IMAGE_PERSONA_GUIDE.md) for:
- Detailed NSFW level explanations
- Photo requirements and tips
- Output structure details
- Troubleshooting guide
- Examples by photo type

---

## ✍️ persona_generator.py - Generate from Text

**Use this when**: You have specific requirements but no photo.

### Quick Start

```bash
# Interactive mode
python persona_generator.py --interactive

# Command line mode
python persona_generator.py --name "Emily" --type "fitness-girl" --age 24
```

### Features

- ✅ **Text-based creation**: Describe what you want
- ✅ **Flexible parameters**: Age, type, personality, occupation
- ✅ **Interactive mode**: Step-by-step guidance
- ✅ **No photo needed**: Pure text generation

### Common Types

```bash
# Fitness girl
python persona_generator.py --name "Kayla" --type "fitness-girl"

# College student
python persona_generator.py --name "Sophie" --type "college-student"

# California girl
python persona_generator.py --name "Mia" --type "california-girl"

# Artist
python persona_generator.py --name "Luna" --type "artist"
```

### Test It

```bash
./test_generator.sh
```

### 📖 Full Documentation

See [PERSONA_GENERATOR_GUIDE.md](PERSONA_GENERATOR_GUIDE.md) for:
- All available parameters
- Persona type suggestions
- Batch generation
- Custom API configuration

---

## 🆚 Which Tool to Use?

### Use **persona_from_image.py** when:

- ✅ You have a portrait photo
- ✅ You want appearance to match perfectly
- ✅ You're creating persona for a specific look
- ✅ You need visual consistency
- ✅ You want to attract based on appearance

**Example**: You have a photo of a blonde gym girl and want a matching fitness influencer persona.

### Use **persona_generator.py** when:

- ✅ You don't have a photo
- ✅ You have very specific text requirements
- ✅ You want to experiment with different types
- ✅ You're creating multiple varied personas
- ✅ You want full control over all attributes

**Example**: You want to create 5 different persona types without photos.

---

## 📦 Output Files

Both tools save to:
```
personas/
├── {name}_{identifier}.json
└── README.md
```

File naming:
- Image tool: `{name}_{image_filename}.json`
- Text tool: `{name}_{timestamp}.json`

---

## 🎯 Generated Persona Structure

Both tools generate Character Card V2 format with:

### Core Fields
- `name`, `description`, `personality`, `system_prompt`
- `core_info` (age, birthday, location)
- `background_info` (education, occupation)

### Appearance (Image tool adds)
- `appearance` (hair, eyes, body_type, style)
- Matched to actual photo

### Social Media Strategy
- `twitter_persona`
  - Content strategy distribution
  - 10-12 tweet examples
  - Handle, bio, posting schedule

### Chat Strategy
- `whatsapp_persona`
  - Texting style
  - Response patterns
  - Conversation examples

### Attraction
- `attraction_profile`
  - What attracts men
  - Teasing style
  - Escalation comfort

---

## 🚀 Quick Examples

### Example 1: Create from Photo

```bash
# Use a photo from the image directory
python persona_from_image.py \
  --image image/hollyjai.jpg \
  --name "Holly" \
  --nsfw medium \
  --output holly_fitness.json
```

### Example 2: Create from Text

```bash
# Describe what you want
python persona_generator.py \
  --name "Mia" \
  --age 22 \
  --type "california-girl" \
  --personality "bubbly, flirty, carefree" \
  --nsfw medium
```

### Example 3: Batch from Photos

```bash
# Generate from all images in directory
for img in image/*.jpg; do
  python persona_from_image.py --image "$img" --nsfw medium
  sleep 5
done
```

---

## 🔧 Configuration

### API Settings

Both tools support:

**Environment variables** (recommended):
```bash
export OPENAI_API_KEY="your-key"
export OPENAI_API_BASE="https://api.example.com/v1"
```

**Command line**:
```bash
--api-key "your-key" --api-base "https://api.example.com/v1"
```

**Default**: Pre-configured API (works out of the box)

### Models

- **Image tool**: `gpt-4-turbo` (vision required)
- **Text tool**: `grok-4-fast` (text only)

Change with `--model` flag.

---

## 📚 Key Principles

Both tools follow these principles:

1. ✅ **Attract male followers** naturally
2. ✅ **Include NSFW/flirty** content (adjustable)
3. ✅ **Seem like real person** (real job, real life)
4. ✅ **Never mention OnlyFans** or content selling
5. ✅ **English output** only
6. ✅ **Detailed and complete** personas

---

## 🎓 Learning Path

### Beginner
1. Run test scripts:
   ```bash
   ./test_image_generator.sh
   ./test_generator.sh
   ```

2. Try interactive mode:
   ```bash
   python persona_generator.py --interactive
   ```

3. Generate from sample image:
   ```bash
   python persona_from_image.py --image image/hollyjai.jpg
   ```

### Intermediate
1. Experiment with NSFW levels:
   ```bash
   python persona_from_image.py --image photo.jpg --nsfw soft
   python persona_from_image.py --image photo.jpg --nsfw high
   ```

2. Try different persona types:
   ```bash
   python persona_generator.py --name "X" --type "fitness-girl"
   python persona_generator.py --name "Y" --type "college-student"
   ```

3. Compare outputs and refine

### Advanced
1. Batch process multiple photos
2. Customize prompts (edit source code)
3. Integrate with ComfyUI workflows
4. Fine-tune for specific audiences

---

## 🐛 Troubleshooting

### Common Issues

**"Image not found"**
- Check file path
- Use absolute path
- Verify file exists

**"API call failed"**
- Check API key
- Verify network connection
- Check API endpoint

**Output doesn't match photo**
- Use higher resolution image
- Ensure good lighting
- Try different NSFW level
- Regenerate (LLM has randomness)

**JSON parsing error**
- Retry generation
- Try different model
- Check API response in error

---

## 🔗 Using Generated Personas

### In ComfyUI

1. Load generated JSON in PersonaLoader node
2. Set mode to `json_file`
3. Path: `custom_nodes/comfyui-twitterchat/personas/your_file.json`

### For Twitter Automation

Generated personas include:
- Content strategy
- Tweet examples
- Posting schedule
- Engagement tactics

### For WhatsApp/DM Automation

Generated personas include:
- Chat style
- Response patterns
- Conversation examples
- Escalation guide

---

## 📊 Comparison Table

| Feature | Image Tool | Text Tool |
|---------|-----------|-----------|
| Input | Portrait photo | Text description |
| Appearance matching | ✅ Exact match | ❌ Generic |
| NSFW levels | 3 levels | 4 levels |
| Visual consistency | ✅ Perfect | ❌ N/A |
| Customization | Medium | High |
| Speed | Slower (vision) | Faster |
| Use case | Real person persona | Creative persona |
| Batch processing | ✅ Supported | ✅ Supported |

---

## 🎉 Get Started Now!

### Quick Test (30 seconds)

```bash
cd custom_nodes/comfyui-twitterchat

# Test image-based generation
./test_image_generator.sh

# Or test text-based generation
./test_generator.sh
```

### Generate Your First Persona

```bash
# From photo
python persona_from_image.py --image your_photo.jpg

# From text
python persona_generator.py --interactive
```

---

## 📖 Documentation Files

- [IMAGE_PERSONA_GUIDE.md](IMAGE_PERSONA_GUIDE.md) - Complete image tool guide
- [PERSONA_GENERATOR_GUIDE.md](PERSONA_GENERATOR_GUIDE.md) - Complete text tool guide
- [personas/README.md](personas/README.md) - Output directory info

---

## 💡 Tips for Success

1. **For image tool**: Use clear, well-lit portrait photos
2. **For text tool**: Provide detailed, specific parameters
3. **NSFW level**: Medium is most versatile
4. **Multiple attempts**: Regenerate if first output isn't perfect
5. **Manual editing**: You can edit JSON files after generation
6. **Test variations**: Try different settings to find what works

---

**Ready to create engaging personas?** Choose your tool and start generating! 🚀
