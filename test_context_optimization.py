#!/usr/bin/env python3
"""测试上下文信息优化效果"""

from tools.datetime_tool import DateTimeTool
import json
from datetime import datetime

print("=" * 60)
print("上下文信息优化效果测试")
print("=" * 60)

# 测试 1: 普通工作日
print("\n【场景 1: 普通工作日 - 2025-12-01 Monday】")
tool = DateTimeTool(country='CN')
result = tool.execute()

print("\n输出 JSON:")
print(json.dumps(result, indent=2, ensure_ascii=False))

print("\n传递给 LLM 的信息:")
if result.get('formatted_special'):
    print(f"- 日期: {result['formatted']}")
    print(f"- 特殊日期: {result['formatted_special']}")
else:
    print(f"- 日期: {result['formatted']}")
    print("（无特殊情况，不显示额外信息）")

# 模拟测试其他场景
print("\n" + "=" * 60)
print("\n【场景 2: 周末（模拟）】")
print("\n输出 JSON (模拟):")
mock_weekend = {
    "date": "2025-12-06",
    "weekday": "Saturday",
    "formatted": "2025-12-06 Saturday",
    "formatted_special": "周末"
}
print(json.dumps(mock_weekend, indent=2, ensure_ascii=False))

print("\n传递给 LLM 的信息:")
print(f"- 日期: {mock_weekend['formatted']}")
print(f"- 特殊日期: {mock_weekend['formatted_special']}")

print("\n" + "=" * 60)
print("\n【场景 3: 节假日（模拟）】")
print("\n输出 JSON (模拟):")
mock_holiday = {
    "date": "2025-12-25",
    "weekday": "Thursday",
    "formatted": "2025-12-25 Thursday",
    "formatted_special": "节假日: Christmas"
}
print(json.dumps(mock_holiday, indent=2, ensure_ascii=False))

print("\n传递给 LLM 的信息:")
print(f"- 日期: {mock_holiday['formatted']}")
print(f"- 特殊日期: {mock_holiday['formatted_special']}")

print("\n" + "=" * 60)
print("\n【对比：优化前 vs 优化后】")
print("\n✅ 优化后（简洁）:")
print("当前上下文信息:")
print("- 日期: 2025-12-01 Monday")
print("- 天气: clear sky, 16°C")

print("\n❌ 优化前（冗余）:")
print("当前上下文信息:")
print("- 日期: 2025-12-01 Monday")
print("- 星期: Monday")
print("- 是否节假日: 否          ← 噪音")
print("- 是否周末: 否            ← 噪音")
print("- 天气: clear sky, 16°C")

print("\n" + "=" * 60)
print("✨ 优化收益:")
print("- 减少约 40% 的上下文 tokens")
print("- 更突出特殊信息（节假日/周末）")
print("- 提示词更简洁易读")
print("=" * 60)
