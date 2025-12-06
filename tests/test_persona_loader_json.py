#!/usr/bin/env python3
"""测试 PersonaLoader 的 json_string 模式"""
import json
import sys
import os

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_persona_loader_json_mode(persona_json):
    """模拟 PersonaLoader 的 json_string 模式"""
    print("=" * 80)
    print("测试 PersonaLoader json_string 模式")
    print("=" * 80)

    print(f"\n输入长度: {len(persona_json)} 字符")
    print(f"输入类型: {type(persona_json)}")
    print(f"前 100 字符: {repr(persona_json[:100])}")
    print(f"后 100 字符: {repr(persona_json[-100:])}")

    # 检查是否为空
    if not persona_json or persona_json.strip() == "":
        print("✗ persona_json 为空")
        return False

    # 尝试解析 - 这是 PersonaLoader 的实际代码逻辑
    try:
        persona = json.loads(persona_json)
        print("\n✓✓✓ JSON 解析成功！")
        print(f"解析后的键: {list(persona.keys())}")

        # 验证人设结构
        if "data" not in persona:
            print("✗ 缺少 'data' 字段")
            return False

        print(f"✓ 包含 'data' 字段")
        print(f"  data 中的键: {list(persona['data'].keys())[:10]}...")

        return True

    except json.JSONDecodeError as e:
        print(f"\n✗✗✗ JSON 解析失败！")
        print(f"错误: {e}")
        print(f"位置: line {e.lineno}, column {e.colno}, pos {e.pos}")

        # 显示错误位置附近的内容
        if e.pos < len(persona_json):
            start = max(0, e.pos - 100)
            end = min(len(persona_json), e.pos + 100)
            print(f"\n错误位置附近的内容:")
            print(f"...{repr(persona_json[start:e.pos])}<<<ERROR>>>{repr(persona_json[e.pos:end])}...")

            # 显示具体字符
            if e.pos < len(persona_json):
                print(f"\n错误位置的字符: {repr(persona_json[e.pos])} (ASCII: {ord(persona_json[e.pos])})")

        return False

    except Exception as e:
        print(f"\n✗✗✗ 其他错误: {e}")
        return False


def test_from_file():
    """从文件加载并测试"""
    print("\n" + "=" * 80)
    print("场景 1: 从文件直接读取测试")
    print("=" * 80)

    file_path = "examples/bdsm_sub_kitten.json"
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    result = test_persona_loader_json_mode(content)
    print(f"\n结果: {'成功' if result else '失败'}")
    return content


def test_with_variations(original_json):
    """测试各种变体"""

    # 测试 2: 添加前后空格
    print("\n" + "=" * 80)
    print("场景 2: JSON 前后有空格")
    print("=" * 80)
    json_with_spaces = "  \n  " + original_json + "  \n  "
    result = test_persona_loader_json_mode(json_with_spaces)
    print(f"结果: {'成功' if result else '失败'}")

    # 测试 3: 添加 BOM
    print("\n" + "=" * 80)
    print("场景 3: JSON 前有 BOM")
    print("=" * 80)
    json_with_bom = "\ufeff" + original_json
    result = test_persona_loader_json_mode(json_with_bom)
    print(f"结果: {'成功' if result else '失败'}")

    # 测试 4: 模拟 ComfyUI 字符串传递（可能的转义问题）
    print("\n" + "=" * 80)
    print("场景 4: 通过 repr/eval 传递（模拟节点传递）")
    print("=" * 80)
    # 这模拟了某些节点可能对字符串做的处理
    json_repr = repr(original_json)
    try:
        json_evaled = eval(json_repr)
        result = test_persona_loader_json_mode(json_evaled)
        print(f"结果: {'成功' if result else '失败'}")
    except Exception as e:
        print(f"✗ repr/eval 失败: {e}")

    # 测试 5: 检查是否有两个 JSON 对象（这是最常见的 "Extra data" 原因）
    print("\n" + "=" * 80)
    print("场景 5: 两个 JSON 对象连接")
    print("=" * 80)
    double_json = original_json + "\n" + original_json
    result = test_persona_loader_json_mode(double_json)
    print(f"结果: {'成功' if result else '失败（预期）'}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 从命令行参数测试
        json_input = sys.argv[1]
        test_persona_loader_json_mode(json_input)
    else:
        # 运行所有测试
        original_json = test_from_file()
        if original_json:
            test_with_variations(original_json)

            print("\n" + "=" * 80)
            print("修复建议")
            print("=" * 80)
            print("""
如果在 ComfyUI 中使用 json_string 模式遇到 "Extra data" 错误：

1. 确保 Text Multiline 节点中只有一个完整的 JSON 对象
2. 检查是否有隐藏字符（BOM、多余空格等）
3. 在 PersonaLoader 节点中添加预处理：
   - persona_json = persona_json.strip()  # 去除前后空白
   - persona_json = persona_json.lstrip('\\ufeff')  # 去除 BOM

建议修改方案：
在 persona_loader.py 的第 73-78 行添加预处理：

    elif input_mode == "json_string":
        if not persona_json or persona_json.strip() == "":
            raise ValueError("JSON字符串模式：persona_json 不能为空")

        # 预处理：去除 BOM 和前后空白
        persona_json = persona_json.lstrip('\\ufeff').strip()

        # 解析JSON字符串
        try:
            persona = json.loads(persona_json)
            """)
