#!/usr/bin/env python3
"""调试 JSON 解析问题"""
import json
import sys

def debug_json_string(json_str):
    """详细调试 JSON 字符串"""
    print("=" * 80)
    print("JSON 字符串诊断")
    print("=" * 80)

    # 1. 基本信息
    print(f"\n【基本信息】")
    print(f"总长度: {len(json_str)} 字符")
    print(f"类型: {type(json_str)}")

    # 2. 开头字符分析
    print(f"\n【开头分析】")
    print(f"前 50 个字符: {repr(json_str[:50])}")
    print(f"前 10 个字符的 ASCII 码:")
    for i, ch in enumerate(json_str[:10]):
        print(f"  位置 {i}: '{ch}' (ASCII: {ord(ch)}, hex: {hex(ord(ch))})")

    # 3. 结尾字符分析
    print(f"\n【结尾分析】")
    print(f"后 50 个字符: {repr(json_str[-50:])}")
    print(f"后 10 个字符的 ASCII 码:")
    for i, ch in enumerate(json_str[-10:]):
        print(f"  位置 {len(json_str)-10+i}: '{ch}' (ASCII: {ord(ch)}, hex: {hex(ord(ch))})")

    # 4. 检查 BOM
    print(f"\n【BOM 检查】")
    if json_str.startswith('\ufeff'):
        print("⚠️  发现 UTF-8 BOM (U+FEFF)")
        json_str = json_str.lstrip('\ufeff')
        print("已移除 BOM")
    else:
        print("✓ 没有 BOM")

    # 5. 检查空白字符
    print(f"\n【空白字符检查】")
    stripped = json_str.strip()
    if len(stripped) != len(json_str):
        print(f"⚠️  发现前后空白字符，移除后长度: {len(stripped)}")
        print(f"原始前 10 字符: {repr(json_str[:10])}")
        print(f"去除后前 10 字符: {repr(stripped[:10])}")
    else:
        print("✓ 没有多余空白字符")

    # 6. 尝试解析
    print(f"\n【解析测试】")
    try:
        # 尝试 1: 原始字符串
        data = json.loads(json_str)
        print("✓ 原始字符串解析成功！")
        return True, None
    except json.JSONDecodeError as e:
        print(f"✗ 原始字符串解析失败: {e}")
        print(f"   错误位置: line {e.lineno}, column {e.colno}")
        print(f"   错误字符位置: {e.pos}")

        # 显示错误位置附近的内容
        start = max(0, e.pos - 50)
        end = min(len(json_str), e.pos + 50)
        print(f"\n   错误位置附近的内容:")
        print(f"   {repr(json_str[start:end])}")
        print(f"   错误字符: {repr(json_str[e.pos:e.pos+1]) if e.pos < len(json_str) else 'EOF'}")

        # 尝试 2: 去除空白字符
        try:
            data = json.loads(stripped)
            print("\n✓ 去除空白字符后解析成功！")
            print("   建议: 在传递前使用 .strip() 去除空白字符")
            return True, None
        except json.JSONDecodeError as e2:
            print(f"\n✗ 去除空白字符后仍然失败: {e2}")

        # 尝试 3: 逐行解析（检查是否有多个 JSON 对象）
        print(f"\n【检查多 JSON 对象】")
        lines = json_str.split('\n')
        json_objects = []
        current_json = ""
        depth = 0

        for line in lines:
            current_json += line + '\n'
            # 简单的括号计数
            depth += line.count('{') - line.count('}')

            if depth == 0 and current_json.strip():
                try:
                    obj = json.loads(current_json)
                    json_objects.append(obj)
                    print(f"✓ 发现有效 JSON 对象 (长度: {len(current_json)} 字符)")
                    current_json = ""
                except:
                    pass

        if len(json_objects) > 1:
            print(f"⚠️  发现 {len(json_objects)} 个 JSON 对象！")
            print("   这就是 'Extra data' 错误的原因")
            print("   解决方案: 只传递一个 JSON 对象")
            return False, "multiple_objects"

        return False, str(e)


def test_file():
    """测试从文件加载"""
    print("\n" + "=" * 80)
    print("测试从文件加载")
    print("=" * 80)

    file_path = "examples/bdsm_sub_kitten.json"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"✓ 文件读取成功: {file_path}")
        print(f"  文件大小: {len(content)} 字符")

        success, error = debug_json_string(content)

        if success:
            print("\n✓✓✓ 文件内容是有效的 JSON！")
            return content
        else:
            print(f"\n✗✗✗ 文件内容解析失败: {error}")
            return None

    except Exception as e:
        print(f"✗ 文件读取失败: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 从命令行参数接收 JSON 字符串
        json_input = sys.argv[1]
        print("从命令行参数接收 JSON")
        debug_json_string(json_input)
    else:
        # 测试文件
        test_file()
