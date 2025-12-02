#!/usr/bin/env python3
"""
环境验证脚本 - 检查 ComfyUI TwitterChat 是否配置正确
运行: python verify_setup.py
"""

import sys
import os

print("="*70)
print("ComfyUI TwitterChat - 环境验证")
print("="*70)

# 1. 检查 Python 版本
print("\n[1/6] 检查 Python 版本...")
py_version = sys.version_info
if py_version >= (3, 8):
    print(f"   ✅ Python {py_version.major}.{py_version.minor}.{py_version.micro}")
else:
    print(f"   ❌ Python 版本过低: {py_version.major}.{py_version.minor}")
    print("      需要 Python 3.8+")
    sys.exit(1)

# 2. 检查依赖包
print("\n[2/6] 检查依赖包...")
required_packages = {
    'requests': 'HTTP 请求库',
    'PIL': '图像处理库 (Pillow)',
    'holidays': '节假日查询库',
    'pytrends': 'Google Trends 库'
}

missing_packages = []
for pkg, desc in required_packages.items():
    try:
        if pkg == 'PIL':
            import PIL
        else:
            __import__(pkg)
        print(f"   ✅ {pkg:15s} - {desc}")
    except ImportError:
        print(f"   ❌ {pkg:15s} - {desc} (缺失)")
        missing_packages.append(pkg)

if missing_packages:
    print("\n   ⚠️  请运行: pip install -r requirements.txt")
    sys.exit(1)

# 3. 检查节点文件
print("\n[3/6] 检查节点文件...")
node_files = [
    'nodes/persona_loader.py',
    'nodes/context_gatherer.py',
    'nodes/image_prompt_builder.py',
    'nodes/tweet_generator.py',
]

all_files_ok = True
for node_file in node_files:
    if os.path.exists(node_file):
        print(f"   ✅ {node_file}")
    else:
        print(f"   ❌ {node_file} (缺失)")
        all_files_ok = False

if not all_files_ok:
    print("\n   ⚠️  节点文件缺失，请检查项目完整性")
    sys.exit(1)

# 4. 测试节点导入
print("\n[4/6] 测试节点导入...")
try:
    from nodes.persona_loader import PersonaLoader
    from nodes.context_gatherer import ContextGatherer
    from nodes.image_prompt_builder import ImagePromptBuilder
    from nodes.tweet_generator import TweetGenerator
    print("   ✅ 所有节点导入成功")
except Exception as e:
    print(f"   ❌ 节点导入失败: {e}")
    sys.exit(1)

# 5. 测试工具模块
print("\n[5/6] 测试工具模块...")
try:
    from tools.datetime_tool import DateTimeTool
    from tools.weather_tool import WeatherTool
    from tools.trending_tool import TrendingTopicsTool
    from utils.llm_client import LLMClient
    from utils.sillytavern import load_persona_from_json
    print("   ✅ 所有工具模块正常")
except Exception as e:
    print(f"   ❌ 工具模块导入失败: {e}")
    sys.exit(1)

# 6. 测试示例人设
print("\n[6/6] 测试示例人设...")
try:
    persona = load_persona_from_json('examples/fitness_girl_emily.json')
    print(f"   ✅ 成功加载示例人设: {persona['data']['name']}")
except Exception as e:
    print(f"   ❌ 加载示例人设失败: {e}")
    sys.exit(1)

# 7. 检查配置文件
print("\n[额外] 检查配置文件...")
if os.path.exists('config.py'):
    try:
        import config
        config.validate_config()
        print("   ✅ config.py 已配置且有效")
    except Exception as e:
        print(f"   ⚠️  config.py 配置有误: {e}")
        print("      请检查 API keys 是否正确填写")
else:
    print("   ℹ️  未找到 config.py")
    print("      可选：复制 config.example.py 为 config.py 并填写 API keys")
    print("      也可以直接在 ComfyUI 节点中配置")

# 最终总结
print("\n" + "="*70)
print("✅ 环境验证完成！")
print("="*70)
print("\n下一步:")
print("  1. 重启 ComfyUI")
print("  2. 在节点菜单中找到 'TwitterChat' 分类")
print("  3. 创建工作流并配置 API keys")
print("  4. 参考 QUICKSTART.md 开始使用")
print("\n📖 文档:")
print("  - 完整文档: README.md")
print("  - 快速开始: QUICKSTART.md")
print("  - 示例人设: examples/fitness_girl_emily.json")
print("\n🚀 祝使用愉快!")
