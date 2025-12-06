#!/usr/bin/env python3
"""
Update LoRA trigger words to 'sunway' for all personas
"""

import json
from pathlib import Path

# 需要更新的人设列表
PERSONAS_TO_UPDATE = [
    '_avrupali_turkler__persona.json',
    'byrecarvalho_persona.json',
    'hollyjai_persona.json',
    'jazmynmakenna_persona.json',
    'keti_one___persona.json',
    '_krkrk__persona.json',
    'mila_bala__persona.json',
    'taaarannn.z_persona.json',
    'vasilinskiy.z_persona.json',
    'veronika_berezhnaya_persona.json',
]

def update_trigger_words(persona_path):
    """更新人设文件的LoRA触发词"""

    # 读取人设JSON
    with open(persona_path, 'r', encoding='utf-8') as f:
        persona_data = json.load(f)

    # 检查是否有lora配置
    if 'lora' not in persona_data['data']:
        print(f"  ⚠️  没有LoRA配置，跳过")
        return False

    # 更新触发词
    old_trigger_words = persona_data['data']['lora']['trigger_words']
    persona_data['data']['lora']['trigger_words'] = ['sunway']
    persona_data['data']['lora']['note'] = '此LoRA用于生成该角色的专属图像，触发词：sunway'

    # 写回文件
    with open(persona_path, 'w', encoding='utf-8') as f:
        json.dump(persona_data, f, ensure_ascii=False, indent=2)

    print(f"  ✅ 触发词更新: {old_trigger_words} → ['sunway']")
    return True

def main():
    personas_dir = Path(__file__).parent / 'personas'

    print("🎯 更新LoRA触发词为 'sunway'")
    print("=" * 60)
    print()

    updated = 0
    skipped = 0

    for persona_file_name in PERSONAS_TO_UPDATE:
        persona_path = personas_dir / persona_file_name

        if not persona_path.exists():
            print(f"❌ {persona_file_name}")
            print(f"  文件不存在")
            skipped += 1
            print()
            continue

        print(f"📝 {persona_file_name}")

        if update_trigger_words(persona_path):
            updated += 1
        else:
            skipped += 1

        print()

    print("=" * 60)
    print("🎉 更新完成！")
    print("=" * 60)
    print()
    print(f"📊 统计:")
    print(f"  总计: {len(PERSONAS_TO_UPDATE)} 个人设")
    print(f"  已更新: {updated} 个")
    print(f"  已跳过: {skipped} 个")
    print()
    print("✨ 所有LoRA现在使用触发词: sunway")
    print()

if __name__ == '__main__':
    main()
