#!/usr/bin/env python3
"""测试各种异常 JSON 输入"""
import json

# 模拟一个开头缺少 { 的 JSON
test_cases = [
    ("正常 JSON", '{"spec": "test", "data": {"name": "test"}}'),
    ("缺少开头 {", '"spec": "test", "data": {"name": "test"}}'),
    ("多余空格 + 正常", '   {"spec": "test", "data": {"name": "test"}}'),
    ("BOM + 正常", '\ufeff{"spec": "test", "data": {"name": "test"}}'),
]

for name, test_json in test_cases:
    print(f"\n{'='*60}")
    print(f"测试: {name}")
    print(f"{'='*60}")
    print(f"长度: {len(test_json)}")
    print(f"前 50 字符: {repr(test_json[:50])}")
    print(f"第一个字符: {repr(test_json[0])} (ASCII: {ord(test_json[0])})")

    # 清理
    cleaned = test_json.lstrip('\ufeff').strip()
    print(f"\n清理后:")
    print(f"长度: {len(cleaned)}")
    print(f"第一个字符: {repr(cleaned[0]) if cleaned else 'EMPTY'}")

    # 尝试解析
    try:
        data = json.loads(cleaned)
        print(f"\n✓ 解析成功")
    except json.JSONDecodeError as e:
        print(f"\n✗ 解析失败: {e}")
        print(f"  错误位置: pos {e.pos}, line {e.lineno}, col {e.colno}")
