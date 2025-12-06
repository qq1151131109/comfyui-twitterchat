#!/bin/bash
# 快速测试脚本 - 生成一个示例人设

echo "🎭 人设生成器快速测试"
echo "======================="
echo ""
echo "正在生成示例人设: Zoe (健身女孩)..."
echo ""

python persona_generator.py \
  --name "Zoe" \
  --age 24 \
  --type "fitness-girl" \
  --location "Los Angeles, California" \
  --personality "energetic, confident, playful" \
  --occupation "fitness influencer" \
  --interests "yoga, healthy cooking, beach workouts" \
  --style "athletic-feminine, colorful activewear" \
  --nsfw soft \
  --output zoe_fitness.json

echo ""
echo "✅ 测试完成!"
echo ""
echo "如果成功，你应该看到生成的文件:"
echo "  custom_nodes/comfyui-twitterchat/personas/zoe_fitness.json"
