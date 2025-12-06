#!/usr/bin/env python3
"""
Add LoRA configuration to all generated personas
"""

import os
import json
import sys
from pathlib import Path

# LoRA映射表：图片文件名 -> LoRA路径
LORA_MAPPING = {
    '_avrupali_turkler_': 'ai-toolkit-output/zimage_lora__avrupali_turkler_/zimage_lora__avrupali_turkler_.safetensors',
    'byrecarvalho': 'ai-toolkit-output/zimage_lora_byrecarvalho/zimage_lora_byrecarvalho.safetensors',
    'hollyjai': 'ai-toolkit-output/zimage_lora_hollyjai/zimage_lora_hollyjai.safetensors',
    'jazmynmakenna': 'ai-toolkit-output/zimage_lora_jazmynmakenna/zimage_lora_jazmynmakenna.safetensors',
    'keti_one__': 'ai-toolkit-output/zimage_lora_keti_one__/zimage_lora_keti_one__.safetensors',
    '_krkrk_': 'ai-toolkit-output/zimage_lora__krkrk_/zimage_lora__krkrk_.safetensors',
    'mila_bala_': 'ai-toolkit-output/zimage_lora_mila_bala_/zimage_lora_mila_bala_.safetensors',
    'taaarannn.z': 'ai-toolkit-output/zimage_lora_taaarannn.z/zimage_lora_taaarannn.z.safetensors',
    'vasilinskiy.z': 'ai-toolkit-output/zimage_lora_vasilinskiy.z/zimage_lora_vasilinskiy.z.safetensors',
    'veronika_berezhnaya': 'ai-toolkit-output/zimage_lora_veronika_berezhnaya/zimage_lora_veronika_berezhnaya.safetensors',
    'anastasiklepnjova': 'ai-toolkit-output/zimage_lora_anastasiklepnjova/zimage_lora_anastasiklepnjova.safetensors',
}

def find_matching_lora(persona_filename):
    """根据人设文件名找到匹配的LoRA"""
    # 移除_persona.json后缀
    base_name = persona_filename.replace('_persona.json', '')

    # 尝试精确匹配
    if base_name in LORA_MAPPING:
        return LORA_MAPPING[base_name]

    # 尝试部分匹配
    for key, lora_path in LORA_MAPPING.items():
        if key in base_name or base_name in key:
            return lora_path

    return None

def add_lora_to_persona(persona_path, lora_path):
    """为人设JSON添加LoRA配置"""

    # 读取人设JSON
    with open(persona_path, 'r', encoding='utf-8') as f:
        persona_data = json.load(f)

    # 检查是否已有lora配置
    if 'lora' in persona_data['data']:
        print(f"  ⚠️  已有LoRA配置，跳过")
        return False

    # 添加LoRA配置
    persona_data['data']['lora'] = {
        "model_path": lora_path,
        "trigger_words": [],
        "strength": 1.0,
        "note": "此LoRA用于生成该角色的专属图像，无需触发词"
    }

    # 写回文件
    with open(persona_path, 'w', encoding='utf-8') as f:
        json.dump(persona_data, f, ensure_ascii=False, indent=2)

    return True

def main():
    personas_dir = Path(__file__).parent / 'personas'

    print("🎨 为所有人设添加LoRA配置")
    print("=" * 60)
    print()

    # 统计
    total = 0
    updated = 0
    skipped = 0
    no_lora = 0

    # 处理主目录
    print("📂 处理主目录人设...")
    print()

    for persona_file in sorted(personas_dir.glob('*_persona.json')):
        total += 1
        filename = persona_file.name

        print(f"📝 {filename}")

        # 查找匹配的LoRA
        lora_path = find_matching_lora(filename)

        if lora_path is None:
            print(f"  ❌ 未找到匹配的LoRA")
            no_lora += 1
            print()
            continue

        print(f"  🎯 匹配LoRA: {lora_path}")

        # 添加LoRA配置
        if add_lora_to_persona(persona_file, lora_path):
            print(f"  ✅ 已添加LoRA配置")
            updated += 1
        else:
            skipped += 1

        print()

    # 处理TMP子目录
    tmp_dir = personas_dir / 'tmp'
    if tmp_dir.exists():
        print("📂 处理TMP子目录人设...")
        print()

        for persona_file in sorted(tmp_dir.glob('*_persona.json')):
            total += 1
            filename = persona_file.name

            print(f"📝 tmp/{filename}")
            print(f"  ⚠️  TMP目录图片无对应LoRA，跳过")
            no_lora += 1
            print()

    # 总结
    print("=" * 60)
    print("🎉 处理完成！")
    print("=" * 60)
    print()
    print(f"📊 统计:")
    print(f"  总计: {total} 个人设")
    print(f"  已更新: {updated} 个")
    print(f"  已跳过: {skipped} 个（已有配置）")
    print(f"  无LoRA: {no_lora} 个")
    print()

    if updated > 0:
        print("✨ LoRA配置已添加到人设文件中")
        print()
        print("💡 在ComfyUI中使用时，LoRA会自动加载并应用到生成的图像")
        print()

if __name__ == '__main__':
    main()
