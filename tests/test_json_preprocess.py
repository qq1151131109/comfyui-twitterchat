#!/usr/bin/env python3
"""测试 JSON 预处理逻辑"""
import json

def preprocess_json_string(persona_json):
    """PersonaLoader 中的 JSON 预处理逻辑"""
    # 1. 去除 UTF-8 BOM（如果存在）
    persona_json_cleaned = persona_json.lstrip('\ufeff')

    # 2. 去除前后空白字符
    persona_json_cleaned = persona_json_cleaned.strip()

    # 3. 检查是否有多个 JSON 对象（"Extra data" 的常见原因）
    # 尝试找到第一个完整的 JSON 对象
    if persona_json_cleaned.startswith('{'):
        # 简单的括号匹配，找到第一个完整的 JSON 对象
        depth = 0
        in_string = False
        escape = False
        first_json_end = -1

        for i, char in enumerate(persona_json_cleaned):
            if escape:
                escape = False
                continue
            if char == '\\':
                escape = True
                continue
            if char == '"' and not escape:
                in_string = not in_string
            if not in_string:
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        first_json_end = i + 1
                        break

        if first_json_end > 0 and first_json_end < len(persona_json_cleaned):
            # 发现有额外内容
            extra_content = persona_json_cleaned[first_json_end:].strip()
            if extra_content:
                print(f"⚠️  警告: 检测到JSON对象后有额外内容，已自动截取第一个JSON对象")
                print(f"   额外内容的前100字符: {repr(extra_content[:100])}")
                persona_json_cleaned = persona_json_cleaned[:first_json_end]

    return persona_json_cleaned


def test_scenarios():
    """测试各种场景"""
    # 读取测试文件
    with open("examples/bdsm_sub_kitten.json", 'r', encoding='utf-8') as f:
        original_json = f.read()

    print("=" * 80)
    print("测试 JSON 预处理逻辑")
    print("=" * 80)

    scenarios = [
        ("正常 JSON", original_json),
        ("JSON 前后有空格", "  \n\n  " + original_json + "  \n\n  "),
        ("JSON 前有 UTF-8 BOM", "\ufeff" + original_json),
        ("两个 JSON 对象", original_json + "\n\n" + original_json),
        ("JSON 后面有文本", original_json + "\n\n这是额外的文本"),
        ("组合问题", "\ufeff  \n" + original_json + "\n\n  额外内容"),
    ]

    for i, (name, test_json) in enumerate(scenarios, 1):
        print(f"\n场景 {i}: {name}")
        print("-" * 80)
        print(f"输入长度: {len(test_json)} 字符")

        try:
            # 预处理
            cleaned = preprocess_json_string(test_json)
            print(f"预处理后长度: {len(cleaned)} 字符")

            # 尝试解析
            data = json.loads(cleaned)
            print(f"✓ 解析成功！")
            print(f"  Persona name: {data['data']['name']}")

        except json.JSONDecodeError as e:
            print(f"✗ 解析失败: {e}")
            print(f"  错误位置: line {e.lineno}, column {e.colno}, pos {e.pos}")
        except Exception as e:
            print(f"✗ 其他错误: {e}")

    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)


if __name__ == "__main__":
    test_scenarios()
