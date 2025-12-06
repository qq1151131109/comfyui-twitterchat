#!/bin/bash
# Test Image-to-Persona Generator with sample photos

echo "🎭 Image-to-Persona Generator Test"
echo "===================================="
echo ""

# Check if image directory exists
if [ ! -d "image" ]; then
    echo "❌ Error: image/ directory not found"
    echo "Please run this script from custom_nodes/comfyui-twitterchat/"
    exit 1
fi

# Find first available image
IMAGE_FILE=$(find image/ -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.webp" \) | head -n 1)

if [ -z "$IMAGE_FILE" ]; then
    echo "❌ No image files found in image/ directory"
    echo "Please add a portrait photo (jpg/png/webp) to the image/ directory"
    exit 1
fi

echo "📸 Using image: $IMAGE_FILE"
echo ""
echo "🤖 Generating persona..."
echo "   NSFW Level: medium"
echo "   This may take 30-60 seconds..."
echo ""

# Run generator
python persona_from_image.py \
    --image "$IMAGE_FILE" \
    --nsfw medium

echo ""
echo "✅ Test complete!"
echo ""
echo "💡 Try with different settings:"
echo "   # Soft NSFW (innocent-flirty)"
echo "   python persona_from_image.py --image $IMAGE_FILE --nsfw soft"
echo ""
echo "   # High NSFW (bold-sexual)"
echo "   python persona_from_image.py --image $IMAGE_FILE --nsfw high"
echo ""
echo "   # With custom name"
echo "   python persona_from_image.py --image $IMAGE_FILE --name \"Sophia\""
