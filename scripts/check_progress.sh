#!/bin/bash
# Monitor batch generation progress

cd /home/ubuntu/shenglin/ComfyUI/custom_nodes/comfyui-twitterchat

echo "📊 批量生成进度监控"
echo "=================================="
echo ""

# 检查主目录生成
echo "📂 主目录 (image/):"
MAIN_TOTAL=13
MAIN_DONE=$(ls -1 personas/*_persona.json 2>/dev/null | grep -v "/tmp/" | wc -l)
echo "  进度: $MAIN_DONE / $MAIN_TOTAL"
if [ $MAIN_DONE -gt 0 ]; then
    echo "  完成率: $(( MAIN_DONE * 100 / MAIN_TOTAL ))%"
fi

# 检查最新生成的文件
if [ $MAIN_DONE -gt 0 ]; then
    echo "  最新生成:"
    ls -lt personas/*_persona.json 2>/dev/null | grep -v "/tmp/" | head -3 | awk '{print "    " $9}'
fi

echo ""

# 检查tmp子目录生成
echo "📂 TMP子目录 (image/tmp/):"
TMP_TOTAL=7
TMP_DONE=$(ls -1 personas/tmp/*_persona.json 2>/dev/null | wc -l)
echo "  进度: $TMP_DONE / $TMP_TOTAL"
if [ $TMP_DONE -gt 0 ]; then
    echo "  完成率: $(( TMP_DONE * 100 / TMP_TOTAL ))%"
fi

# 检查最新生成的文件
if [ $TMP_DONE -gt 0 ]; then
    echo "  最新生成:"
    ls -lt personas/tmp/*_persona.json 2>/dev/null | head -3 | awk '{print "    " $9}'
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 总计
TOTAL_ALL=$(( MAIN_TOTAL + TMP_TOTAL ))
DONE_ALL=$(( MAIN_DONE + TMP_DONE ))
echo "📊 总进度: $DONE_ALL / $TOTAL_ALL ($(( DONE_ALL * 100 / TOTAL_ALL ))%)"

# 检查日志文件
echo ""
echo "📄 日志文件:"
ls -lt batch_generate_*.log 2>/dev/null | head -5 | awk '{print "  " $9, "(" $6, $7, $8 ")"}'

echo ""

# 检查是否有进程在运行
if pgrep -f "persona_from_image.py" > /dev/null; then
    echo "🔄 状态: 正在生成中..."
    echo ""
    echo "💡 查看实时日志:"
    LATEST_LOG=$(ls -t batch_generate_*.log 2>/dev/null | head -1)
    if [ -n "$LATEST_LOG" ]; then
        echo "  tail -f $LATEST_LOG"
    fi
else
    echo "✅ 状态: 所有任务已完成"
fi

echo ""
