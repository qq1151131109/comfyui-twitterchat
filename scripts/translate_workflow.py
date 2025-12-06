#!/usr/bin/env python3
"""
Translate Chinese prompts in workflow to English
"""

import json
import os
import sys
import requests

def translate_with_llm(chinese_text, api_key, api_base):
    """Use LLM to translate Chinese to English"""

    url = f"{api_base}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    prompt = f"""Translate the following Chinese prompt/instructions to English.
Keep the same structure, formatting, and technical terms.
Maintain all special markers like 【】, ⚠️, ✅, ❌, etc.

Chinese text:
{chinese_text}

Output ONLY the English translation, no explanations."""

    data = {
        "model": "gpt-4.1",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 10000
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"❌ Translation failed: {str(e)}")
        return None

def has_chinese(text):
    """Check if text contains Chinese characters"""
    if not isinstance(text, str):
        return False
    return any('\u4e00' <= char <= '\u9fff' for char in text)

def translate_workflow(input_file, output_file):
    """Translate all Chinese prompts in workflow"""

    print("🌐 Translating workflow to English")
    print("=" * 70)
    print()

    # Load workflow
    with open(input_file, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    print(f"📂 Loaded: {input_file}")
    print()

    # API config
    api_key = os.environ.get('OPENAI_API_KEY', 'sk-7U0E6zRslf3aUM2Z9DcEIbaWxDY3aRZbR5Wq4g0TKw0IPe1L')
    api_base = os.environ.get('OPENAI_BASE_URL', 'https://www.dmxapi.cn/v1').rstrip('/')

    # Track translations
    translated_count = 0
    total_chinese_fields = 0

    # Iterate through nodes
    for node_id, node in workflow.items():
        if not isinstance(node, dict):
            continue

        node_type = node.get('class_type') or node.get('type')

        # Check widgets_values (common place for prompts)
        if 'widgets_values' in node:
            values = node['widgets_values']
            for i, value in enumerate(values):
                if isinstance(value, str) and has_chinese(value):
                    total_chinese_fields += 1
                    print(f"🔄 Node {node_id} ({node_type}), widget #{i}")
                    print(f"   Chinese length: {len(value)} chars")

                    # Translate
                    translated = translate_with_llm(value, api_key, api_base)
                    if translated:
                        node['widgets_values'][i] = translated
                        translated_count += 1
                        print(f"   ✅ Translated to English")
                    else:
                        print(f"   ❌ Translation failed")
                    print()

        # Check inputs (another common place)
        if 'inputs' in node:
            inputs = node['inputs']
            for key, value in inputs.items():
                if isinstance(value, str) and has_chinese(value):
                    total_chinese_fields += 1
                    print(f"🔄 Node {node_id} ({node_type}), input '{key}'")
                    print(f"   Chinese length: {len(value)} chars")

                    # Translate
                    translated = translate_with_llm(value, api_key, api_base)
                    if translated:
                        node['inputs'][key] = translated
                        translated_count += 1
                        print(f"   ✅ Translated to English")
                    else:
                        print(f"   ❌ Translation failed")
                    print()

    # Save translated workflow
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)

    print("=" * 70)
    print("✨ Translation Complete!")
    print("=" * 70)
    print()
    print(f"📊 Statistics:")
    print(f"  Total Chinese fields found: {total_chinese_fields}")
    print(f"  Successfully translated: {translated_count}")
    print(f"  Failed: {total_chinese_fields - translated_count}")
    print()
    print(f"💾 Saved to: {output_file}")
    print()

    # Verify result
    with open(output_file, 'r', encoding='utf-8') as f:
        new_workflow = json.load(f)

    new_content = json.dumps(new_workflow, ensure_ascii=False)
    chinese_remaining = sum(1 for c in new_content if '\u4e00' <= c <= '\u9fff')

    print(f"🔍 Verification:")
    print(f"  Chinese characters remaining: {chinese_remaining}")
    if chinese_remaining == 0:
        print(f"  ✅ Workflow is now 100% English!")
    else:
        print(f"  ⚠️  Some Chinese text remains (may be in untranslated fields)")

def main():
    input_file = '/home/ubuntu/shenglin/ComfyUI/workflow/自动生成推文-120402.json'
    output_file = '/home/ubuntu/shenglin/ComfyUI/workflow/auto-tweet-generation-en-US.json'

    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return 1

    try:
        translate_workflow(input_file, output_file)
        return 0
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
