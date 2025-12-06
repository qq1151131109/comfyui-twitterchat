#!/bin/bash
# Quick demo: Generate persona from multiple sample images

echo "🎭 Batch Image-to-Persona Demo"
echo "==============================="
echo ""
echo "This will generate personas from 3 sample images"
echo "with different NSFW levels to show the variety."
echo ""
read -p "Press Enter to continue..."
echo ""

# Find up to 3 images
IMAGES=($(find image/ -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.webp" \) | head -n 3))

if [ ${#IMAGES[@]} -eq 0 ]; then
    echo "❌ No images found in image/ directory"
    exit 1
fi

echo "Found ${#IMAGES[@]} image(s)"
echo ""

# Process each image with different NSFW level
NSFW_LEVELS=("soft" "medium" "high")

for i in "${!IMAGES[@]}"; do
    img="${IMAGES[$i]}"
    nsfw="${NSFW_LEVELS[$i]}"

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📸 Image $((i+1))/${#IMAGES[@]}: $(basename "$img")"
    echo "🔥 NSFW Level: $nsfw"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    python persona_from_image.py \
        --image "$img" \
        --nsfw "$nsfw"

    echo ""
    echo "✅ Completed $((i+1))/${#IMAGES[@]}"
    echo ""

    # Small delay between requests
    if [ $i -lt $((${#IMAGES[@]} - 1)) ]; then
        echo "⏳ Waiting 3 seconds before next generation..."
        sleep 3
        echo ""
    fi
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 All personas generated!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📂 Check personas/ directory for output files"
echo ""
echo "💡 Notice the difference between NSFW levels:"
echo "   - soft:   Innocent-flirty, girl-next-door"
echo "   - medium: Balanced, teasing and playful"
echo "   - high:   Bold, openly sexual"
