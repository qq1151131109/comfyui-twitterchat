#!/bin/bash
# Batch generate personas for all images in the image/ directory

echo "🎭 批量人设生成器"
echo "=================================="
echo ""

# 检查目录
if [ ! -d "image" ]; then
    echo "❌ 错误: image/ 目录不存在"
    exit 1
fi

# 统计图片数量
IMAGE_COUNT=$(find image/ -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.webp" \) | wc -l)

if [ $IMAGE_COUNT -eq 0 ]; then
    echo "❌ 错误: image/ 目录中没有图片文件"
    exit 1
fi

echo "📸 找到 $IMAGE_COUNT 张图片"
echo ""

# 询问NSFW等级
echo "🔥 选择NSFW等级:"
echo "  1. soft   - 清纯撩人"
echo "  2. medium - 平衡性感"
echo "  3. high   - 极度露骨 (推荐)"
echo ""
read -p "请选择 (1-3, 默认3): " nsfw_choice

case $nsfw_choice in
    1) NSFW_LEVEL="soft" ;;
    2) NSFW_LEVEL="medium" ;;
    3|"") NSFW_LEVEL="high" ;;
    *) NSFW_LEVEL="high" ;;
esac

echo ""
echo "✅ 使用NSFW等级: $NSFW_LEVEL"
echo ""

# 询问延迟时间
read -p "每张图片间隔秒数 (避免限流, 默认5): " delay
delay=${delay:-5}

echo ""
echo "⏳ 延迟时间: ${delay}秒"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "开始批量生成..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 计数器
success_count=0
fail_count=0
current=0

# 遍历所有图片
for img in image/*.{jpg,jpeg,png,webp}; do
    # 跳过不存在的文件（glob未匹配时）
    [ -f "$img" ] || continue

    current=$((current + 1))
    filename=$(basename "$img")
    name_without_ext="${filename%.*}"

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📸 [$current/$IMAGE_COUNT] $filename"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # 生成人设
    if python persona_from_image.py \
        --image "$img" \
        --nsfw "$NSFW_LEVEL" \
        --output "${name_without_ext}_persona.json"; then

        success_count=$((success_count + 1))
        echo ""
        echo "✅ 成功生成: ${name_without_ext}_persona.json"
        echo ""
    else
        fail_count=$((fail_count + 1))
        echo ""
        echo "❌ 失败: $filename"
        echo ""
    fi

    # 如果不是最后一张，等待延迟
    if [ $current -lt $IMAGE_COUNT ]; then
        echo "⏳ 等待 ${delay} 秒..."
        sleep $delay
        echo ""
    fi
done

# 总结
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 批量生成完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 统计:"
echo "  总计: $IMAGE_COUNT 张"
echo "  成功: $success_count 张"
echo "  失败: $fail_count 张"
echo ""
echo "📂 生成的文件位置:"
echo "  custom_nodes/comfyui-twitterchat/personas/"
echo ""

# 列出生成的文件
echo "📝 生成的人设文件:"
ls -lh personas/*_persona.json 2>/dev/null | tail -$success_count | awk '{print "  " $9, "(" $5 ")"}'
echo ""
echo "✨ 全部完成！"
