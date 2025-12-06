#!/usr/bin/env python3
"""测试增强后的 PersonaLoader"""
import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 直接导入修改后的 PersonaLoader
from nodes.persona_loader import PersonaLoader

def test_scenarios():
    """测试各种场景"""
    loader = PersonaLoader()

    # 读取测试文件
    with open("examples/bdsm_sub_kitten.json", 'r', encoding='utf-8') as f:
        original_json = f.read()

    print("=" * 80)
    print("测试增强后的 PersonaLoader")
    print("=" * 80)

    # 场景 1: 正常 JSON
    print("\n场景 1: 正常 JSON")
    print("-" * 80)
    try:
        result = loader.load(
            input_mode="json_string",
            persona_file="",
            persona_json=original_json,
            user_id="test_user_1"
        )
        print(f"✓ 成功！返回类型: {type(result)}")
        print(f"  Persona name: {result[0]['data']['name']}")
        print(f"  Summary 长度: {len(result[1])} 字符")
    except Exception as e:
        print(f"✗ 失败: {e}")

    # 场景 2: JSON 前后有空格
    print("\n场景 2: JSON 前后有空格和换行")
    print("-" * 80)
    try:
        result = loader.load(
            input_mode="json_string",
            persona_file="",
            persona_json="  \n\n  " + original_json + "  \n\n  ",
            user_id="test_user_2"
        )
        print(f"✓ 成功！")
        print(f"  Persona name: {result[0]['data']['name']}")
    except Exception as e:
        print(f"✗ 失败: {e}")

    # 场景 3: JSON 前有 BOM
    print("\n场景 3: JSON 前有 UTF-8 BOM")
    print("-" * 80)
    try:
        result = loader.load(
            input_mode="json_string",
            persona_file="",
            persona_json="\ufeff" + original_json,
            user_id="test_user_3"
        )
        print(f"✓ 成功！")
        print(f"  Persona name: {result[0]['data']['name']}")
    except Exception as e:
        print(f"✗ 失败: {e}")

    # 场景 4: 两个 JSON 对象（关键测试！）
    print("\n场景 4: 两个 JSON 对象（Extra data 场景）")
    print("-" * 80)
    try:
        result = loader.load(
            input_mode="json_string",
            persona_file="",
            persona_json=original_json + "\n\n" + original_json,
            user_id="test_user_4"
        )
        print(f"✓ 成功！（自动截取了第一个JSON对象）")
        print(f"  Persona name: {result[0]['data']['name']}")
    except Exception as e:
        print(f"✗ 失败: {e}")

    # 场景 5: JSON 后面有文本
    print("\n场景 5: JSON 后面有额外文本")
    print("-" * 80)
    try:
        result = loader.load(
            input_mode="json_string",
            persona_file="",
            persona_json=original_json + "\n\n这是一些额外的文本",
            user_id="test_user_5"
        )
        print(f"✓ 成功！（自动截取了JSON对象）")
        print(f"  Persona name: {result[0]['data']['name']}")
    except Exception as e:
        print(f"✗ 失败: {e}")

    # 场景 6: 组合问题（BOM + 空格 + 额外内容）
    print("\n场景 6: 组合问题（BOM + 空格 + 额外内容）")
    print("-" * 80)
    try:
        result = loader.load(
            input_mode="json_string",
            persona_file="",
            persona_json="\ufeff  \n" + original_json + "\n\n  额外内容",
            user_id="test_user_6"
        )
        print(f"✓ 成功！（处理了所有问题）")
        print(f"  Persona name: {result[0]['data']['name']}")
    except Exception as e:
        print(f"✗ 失败: {e}")

    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)


if __name__ == "__main__":
    test_scenarios()
