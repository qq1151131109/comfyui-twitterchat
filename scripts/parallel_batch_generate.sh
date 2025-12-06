#!/bin/bash
# Parallel batch generation - 20 concurrent processes

cd /home/ubuntu/shenglin/ComfyUI/custom_nodes/comfyui-twitterchat

echo "🚀 并发批量人设生成器"
echo "=================================="
echo "并发数: 20"
echo "NSFW等级: high"
echo "模型: gpt-4.1"
echo ""

# 检查目录
if [ ! -d "image" ]; then
    echo "❌ 错误: image/ 目录不存在"
    exit 1
fi

# 获取所有图片（主目录）
IMAGES=(image/*.jpg image/*.jpeg image/*.png image/*.webp)
VALID_IMAGES=()
for img in "${IMAGES[@]}"; do
    [ -f "$img" ] && VALID_IMAGES+=("$img")
done

# 获取tmp子目录图片
TMP_IMAGES=(image/tmp/*.jpg image/tmp/*.jpeg image/tmp/*.png image/tmp/*.webp)
VALID_TMP_IMAGES=()
for img in "${TMP_IMAGES[@]}"; do
    [ -f "$img" ] && VALID_TMP_IMAGES+=("$img")
done

MAIN_COUNT=${#VALID_IMAGES[@]}
TMP_COUNT=${#VALID_TMP_IMAGES[@]}
TOTAL_COUNT=$((MAIN_COUNT + TMP_COUNT))

echo "📸 主目录: $MAIN_COUNT 张"
echo "📸 TMP目录: $TMP_COUNT 张"
echo "📸 总计: $TOTAL_COUNT 张"
echo ""

if [ $TOTAL_COUNT -eq 0 ]; then
    echo "❌ 没有找到图片文件"
    exit 1
fi

# 创建tmp输出目录
mkdir -p personas/tmp

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 开始并发生成..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

START_TIME=$(date +%s)

# 定义生成函数
generate_persona() {
    local img=$1
    local is_tmp=$2
    local filename=$(basename "$img")
    local name_without_ext="${filename%.*}"

    if [ "$is_tmp" = "true" ]; then
        local output="tmp/${name_without_ext}_persona.json"
        local prefix="[TMP]"
    else
        local output="${name_without_ext}_persona.json"
        local prefix="[MAIN]"
    fi

    echo "🤖 $prefix 开始: $filename"

    if python persona_from_image.py \
        --image "$img" \
        --nsfw high \
        --output "$output" > "/tmp/persona_${name_without_ext}.log" 2>&1; then
        echo "✅ $prefix 完成: $filename → $output"
        return 0
    else
        echo "❌ $prefix 失败: $filename"
        return 1
    fi
}

export -f generate_persona

# 并发处理 - 使用后台任务
MAX_JOBS=20
job_count=0
success_count=0
fail_count=0

# 创建临时目录存储结果
RESULT_DIR=$(mktemp -d)

# 处理主目录图片
for img in "${VALID_IMAGES[@]}"; do
    generate_persona "$img" "false" &
    job_count=$((job_count + 1))

    # 达到最大并发数时等待
    if [ $job_count -ge $MAX_JOBS ]; then
        wait -n
        job_count=$((job_count - 1))
    fi
done

# 处理tmp子目录图片
for img in "${VALID_TMP_IMAGES[@]}"; do
    generate_persona "$img" "true" &
    job_count=$((job_count + 1))

    # 达到最大并发数时等待
    if [ $job_count -ge $MAX_JOBS ]; then
        wait -n
        job_count=$((job_count - 1))
    fi
done

# 等待所有任务完成
echo ""
echo "⏳ 等待所有任务完成..."
wait

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# 统计结果
MAIN_DONE=$(ls -1 personas/*_persona.json 2>/dev/null | grep -v "/tmp/" | wc -l)
TMP_DONE=$(ls -1 personas/tmp/*_persona.json 2>/dev/null | wc -l)
TOTAL_DONE=$((MAIN_DONE + TMP_DONE))

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 并发生成完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 统计:"
echo "  总计: $TOTAL_COUNT 张"
echo "  主目录: $MAIN_DONE / $MAIN_COUNT 张"
echo "  TMP目录: $TMP_DONE / $TMP_COUNT 张"
echo "  总完成: $TOTAL_DONE 张"
echo "  成功率: $(( TOTAL_DONE * 100 / TOTAL_COUNT ))%"
echo ""
echo "⏱️  耗时: ${DURATION} 秒 (约 $(( DURATION / 60 )) 分钟)"
echo "⚡ 平均速度: $(( DURATION / TOTAL_DONE )) 秒/张"
echo ""
echo "📂 输出目录:"
echo "  主目录: $(pwd)/personas/"
echo "  TMP目录: $(pwd)/personas/tmp/"
echo ""

# 显示生成的文件
if [ $MAIN_DONE -gt 0 ]; then
    echo "📝 主目录人设 (最近5个):"
    ls -lt personas/*_persona.json 2>/dev/null | grep -v "/tmp/" | head -5 | awk '{print "  " $9, "(" $5 ")"}'
    echo ""
fi

if [ $TMP_DONE -gt 0 ]; then
    echo "📝 TMP目录人设 (全部):"
    ls -lt personas/tmp/*_persona.json 2>/dev/null | awk '{print "  " $9, "(" $5 ")"}'
    echo ""
fi

echo "✨ 全部完成！"

# 清理临时日志
rm -rf /tmp/persona_*.log
