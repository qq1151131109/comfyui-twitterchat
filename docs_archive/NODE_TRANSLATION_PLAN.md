# 🌐 Node Code Translation Plan

## Overview

Total Chinese characters in node code: **4,760 characters** across 7 files

**Goal**: Translate all Chinese prompts to English while preserving:
- ✅ Variable placeholders (`{name}`, `{date_info}`, etc.)
- ✅ Code structure and logic
- ✅ Special markers (【】, ⚠️, ✅, ❌, etc.)
- ✅ Formatting and indentation

---

## Priority Ranking

### P0 - Critical (Must translate first)

#### 1. tweet_generator.py (3,009 Chinese chars)
**Why critical**: Core tweet generation node, contains all main prompt templates

**Major Chinese sections**:
- Line 200-214: Background info section (`【今日背景】`)
- Line 241-257: Style guidance (`【推文风格要求】`)
- Line 274-279: Output format (`【输出格式规范】`)
- Line 286-383: Scene description standards (`【场景描述标准】`)
- Line 390-447: Authenticity principles (`【真实感核心原则】`)
- Line 474-496: Plan guidance (`今日运营计划：`)
- Line 502-512: Examples text (`参考以下人设推文示例...`)
- Line 532-533: KB info (`相关背景知识:`)
- Line 556-580: User prompt template (`请以 {name} 的身份撰写...`)

**Estimated time**: 2-3 hours

---

### P1 - Important (Core functionality)

#### 2. calendar_manager.py (512 Chinese chars)
**Purpose**: Generate monthly calendar plans

**Key areas**: Calendar generation prompts, planning guidelines

**Estimated time**: 30-45 minutes

---

#### 3. persona_loader.py (344 Chinese chars)
**Purpose**: Load and validate persona data

**Key areas**: Error messages, validation messages, UI descriptions

**Estimated time**: 20-30 minutes

---

#### 4. image_prompt_builder.py (280 Chinese chars)
**Purpose**: Build image generation prompts from scene hints

**Key areas**: Prompt enhancement logic, system prompts

**Estimated time**: 20-30 minutes

---

### P2 - Supporting (Minor content)

#### 5. output_manager.py (257 Chinese chars)
**Purpose**: Manage output files and formatting

**Key areas**: Status messages, file naming

**Estimated time**: 15-20 minutes

---

#### 6. lora_loader.py (188 Chinese chars)
**Purpose**: Load LoRA models from persona

**Key areas**: Status messages, error messages

**Estimated time**: 10-15 minutes

---

#### 7. context_gatherer.py (170 Chinese chars)
**Purpose**: Gather date, weather, and context info

**Key areas**: Error messages, date formatting

**Estimated time**: 10-15 minutes

---

## Translation Strategy

### Step-by-Step Approach

1. **Backup all files**
   ```bash
   cp nodes/{file}.py nodes/{file}.py.backup
   ```

2. **Translate section by section**
   - Extract Chinese text block
   - Translate while preserving structure
   - Test variable substitution
   - Verify no syntax errors

3. **Preserve special markers**
   - Keep: 【】, ⚠️, ✅, ❌
   - Keep: Variable placeholders `{name}`, `{date_info}`, etc.
   - Keep: Code indentation and string formatting

4. **Test after each file**
   - Import the module: `python -c "from nodes.xxx import *"`
   - Run basic workflow test

---

## Translation Checklist

For each file:
- [ ] Create backup
- [ ] Translate all Chinese prompts
- [ ] Verify variable placeholders intact
- [ ] Check no syntax errors (`python -c "import nodes.xxx"`)
- [ ] Test in actual workflow (optional for P2)
- [ ] Update translation status

---

## Example Translation

**Before** (tweet_generator.py:214):
```python
background_info = "【今日背景】\n" + "，".join(bg_parts) + "。\n\n"
```

**After**:
```python
background_info = "【Today's Context】\n" + ", ".join(bg_parts) + ".\n\n"
```

**Before** (tweet_generator.py:556):
```python
user_prompt = f"""请以 {name} 的身份撰写一条{topic_desc}。
{plan_guidance}
"""
```

**After**:
```python
user_prompt = f"""Write a tweet as {name} about {topic_desc}.
{plan_guidance}
"""
```

---

## Progress Tracking

| File | Chinese Chars | Status | Notes |
|------|---------------|--------|-------|
| tweet_generator.py | 3,009 | ⏸️ Pending | P0 - Start here |
| calendar_manager.py | 512 | ⏸️ Pending | P1 |
| persona_loader.py | 344 | ⏸️ Pending | P1 |
| image_prompt_builder.py | 280 | ⏸️ Pending | P1 |
| output_manager.py | 257 | ⏸️ Pending | P2 |
| lora_loader.py | 188 | ⏸️ Pending | P2 |
| context_gatherer.py | 170 | ⏸️ Pending | P2 |

**Total**: 4,760 characters → 0 translated

---

## Validation Tests

After translation, run:

```bash
# 1. Import all nodes (syntax check)
python -c "
from nodes.tweet_generator import TweetGenerator
from nodes.calendar_manager import CalendarManager
from nodes.persona_loader import PersonaLoader
from nodes.image_prompt_builder import ImagePromptBuilder
from nodes.context_gatherer import ContextGatherer
from nodes.lora_loader import LoraLoaderFromPersona
from nodes.output_manager import OutputManager
print('✅ All nodes import successfully')
"

# 2. Run basic workflow test
# (Load a workflow in ComfyUI and execute)

# 3. Check output language
# (Verify all generated content is in English)
```

---

## Notes

- Translation should preserve the **meaning** and **tone** of the original Chinese
- Some section headers with 【】markers should keep the markers but translate the text inside
- Example prompts within the code should also be translated
- Error messages and user-facing text are also important to translate

---

**Ready to start translation!**
**First target: tweet_generator.py** 🎯
