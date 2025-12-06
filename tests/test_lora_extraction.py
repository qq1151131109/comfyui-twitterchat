#!/usr/bin/env python3
"""测试 LoRA 提取功能"""
import json
import sys

# 读取人设文件
persona_file = "examples/tea_girl_meilin.json"
with open(persona_file, 'r', encoding='utf-8') as f:
    persona = json.load(f)

print("=" * 60)
print("测试 LoRA 提取")
print("=" * 60)

# 检查人设结构
data = persona.get("data", {})
print(f"\n1. 人设名称: {data.get('name', 'Unknown')}")

# 检查 lora 配置
lora_config = data.get("lora") or data.get("extensions", {}).get("lora")
print(f"\n2. LoRA 配置存在: {lora_config is not None}")

if lora_config:
    print(f"   - model_name: {lora_config.get('model_name', 'N/A')}")
    print(f"   - trigger_words: {lora_config.get('trigger_words', [])}")
    print(f"   - recommended_weight: {lora_config.get('recommended_weight', 0.7)}")
    
    # 模拟提取逻辑
    model_name = lora_config.get("model_name", "")
    trigger_words = lora_config.get("trigger_words", [])
    recommended_weight = lora_config.get("recommended_weight", 0.7)
    
    if model_name:
        lora_parts = [f"<lora:{model_name}:{recommended_weight}>"]
        if isinstance(trigger_words, list):
            lora_parts.extend(trigger_words)
        result = ", ".join(lora_parts)
        
        print(f"\n3. 提取结果:")
        print(f"   {result}")
    else:
        print("\n3. 错误: model_name 为空")
else:
    print("\n3. 错误: 未找到 lora 配置")
    print(f"   data.keys(): {list(data.keys())[:10]}")

print("\n" + "=" * 60)
