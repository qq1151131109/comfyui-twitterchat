#!/bin/bash
# Auto batch generate personas - no interaction needed
# Uses NSFW level: high

cd /home/ubuntu/shenglin/ComfyUI/custom_nodes/comfyui-twitterchat

echo "🎭 自动批量人设生成器"
echo "=================================="
echo "NSFW等级: high (极度露骨)"
echo "模型: gpt-4.1"
echo "延迟: 5秒/张"
echo ""

# 检查目录
if [ ! -d "image" ]; then
    echo "❌ 错误: image/ 目录不存在"
    exit 1
fi

# 获取所有图片
IMAGES=(image/*.jpg image/*.jpeg image/*.png image/*.webp)
# 过滤掉不存在的文件
VALID_IMAGES=()
for img in "${IMAGES[@]}"; do
    [ -f "$img" ] && VALID_IMAGES+=("$img")
done

IMAGE_COUNT=${#VALID_IMAGES[@]}

if [ $IMAGE_COUNT -eq 0 ]; then
    echo "❌ 错误: image/ 目录中没有图片文件"
    exit 1
fi

echo "📸 找到 $IMAGE_COUNT 张图片"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "开始生成..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 计数器
success_count=0
fail_count=0
current=0

# 创建日志文件
LOG_FILE="batch_generate_$(date +%Y%m%d_%H%M%S).log"

# 遍历所有图片
for img in "${VALID_IMAGES[@]}"; do
    current=$((current + 1))
    filename=$(basename "$img")
    name_without_ext="${filename%.*}"

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
    echo "📸 [$current/$IMAGE_COUNT] $filename" | tee -a "$LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"

    # 生成人设
    echo "🤖 正在生成..." | tee -a "$LOG_FILE"

    if python persona_from_image.py \
        --image "$img" \
        --nsfw high \
        --output "${name_without_ext}_persona.json" 2>&1 | tee -a "$LOG_FILE"; then

        success_count=$((success_count + 1))
        echo "" | tee -a "$LOG_FILE"
        echo "✅ 成功: ${name_without_ext}_persona.json" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
    else
        fail_count=$((fail_count + 1))
        echo "" | tee -a "$LOG_FILE"
        echo "❌ 失败: $filename" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
    fi

    # 如果不是最后一张，等待延迟
    if [ $current -lt $IMAGE_COUNT ]; then
        echo "⏳ 等待 5 秒..." | tee -a "$LOG_FILE"
        sleep 5
        echo "" | tee -a "$LOG_FILE"
    fi
done

# 总结
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
echo "🎉 批量生成完成！" | tee -a "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "📊 统计:" | tee -a "$LOG_FILE"
echo "  总计: $IMAGE_COUNT 张" | tee -a "$LOG_FILE"
echo "  成功: $success_count 张" | tee -a "$LOG_FILE"
echo "  失败: $fail_count 张" | tee -a "$LOG_FILE"
echo "  成功率: $(( success_count * 100 / IMAGE_COUNT ))%" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "📂 生成的文件位置:" | tee -a "$LOG_FILE"
echo "  $(pwd)/personas/" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 列出生成的文件
if [ $success_count -gt 0 ]; then
    echo "📝 生成的人设文件:" | tee -a "$LOG_FILE"
    ls -lh personas/*_persona.json 2>/dev/null | tail -$success_count | awk '{print "  " $9, "(" $5 ")"}' | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"
echo "📄 日志文件: $LOG_FILE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "✨ 全部完成！" | tee -a "$LOG_FILE"
