"""输出管理节点"""
import os
import json
from datetime import datetime
from PIL import Image
import numpy as np
import torch


class OutputManager:
    """统一输出管理器（按user_id/date组织）"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "user_id": ("STRING", {
                    "default": "",
                    "placeholder": "用户ID"
                }),
                "date": ("STRING", {
                    "default": "",
                    "placeholder": "日期 (YYYY-MM-DD)"
                }),
                "tweet_text": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "forceInput": True
                }),
                "scene_hint": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "forceInput": True
                }),
                "images": ("IMAGE", {
                    "tooltip": "生成的图片"
                }),
                "persona": ("PERSONA", {
                    "tooltip": "人设数据（用于元数据）"
                }),
            },
            "optional": {
                "base_output_dir": ("STRING", {
                    "default": "output",
                    "placeholder": "基础输出目录"
                }),
                "workflow_id": ("STRING", {
                    "default": "",
                    "placeholder": "工作流ID（可选）"
                }),
                "additional_metadata": ("STRING", {
                    "default": "{}",
                    "multiline": True,
                    "placeholder": "额外的元数据JSON"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("output_dir", "image_path", "metadata_path")
    FUNCTION = "save_content"
    CATEGORY = "TwitterChat"
    DESCRIPTION = "Organize outputs by user_id and date with metadata"
    OUTPUT_NODE = True

    def save_content(
        self,
        user_id,
        date,
        tweet_text,
        scene_hint,
        images,
        persona,
        base_output_dir="output",
        workflow_id="",
        additional_metadata="{}"
    ):
        """
        保存内容到规范的目录结构

        目录结构:
            output/
            └── user_abc123/
                └── 2025-12-03/
                    ├── tweet.txt
                    ├── image.png
                    ├── scene_hint.txt
                    └── metadata.json

        参数:
            user_id: 用户ID
            date: 日期字符串 (YYYY-MM-DD)
            tweet_text: 推文文本
            scene_hint: 场景描述
            images: 生成的图片张量
            persona: 人设数据
            base_output_dir: 基础输出目录
            workflow_id: 工作流ID
            additional_metadata: 额外元数据JSON字符串

        返回:
            (output_dir, image_path, metadata_path)
        """
        try:
            # 1. 创建输出目录
            if not user_id:
                user_id = "default_user"
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")

            output_dir = os.path.join(base_output_dir, user_id, date)
            os.makedirs(output_dir, exist_ok=True)

            # 2. 保存推文文本
            tweet_path = os.path.join(output_dir, "tweet.txt")
            with open(tweet_path, "w", encoding="utf-8") as f:
                f.write(tweet_text)

            # 3. 保存场景描述
            scene_path = os.path.join(output_dir, "scene_hint.txt")
            with open(scene_path, "w", encoding="utf-8") as f:
                f.write(scene_hint)

            # 4. 保存图片
            image_path = os.path.join(output_dir, "image.png")
            self._save_image(images, image_path)

            # 5. 保存元数据
            metadata_path = os.path.join(output_dir, "metadata.json")
            metadata = self._build_metadata(
                user_id=user_id,
                date=date,
                tweet_text=tweet_text,
                scene_hint=scene_hint,
                persona=persona,
                workflow_id=workflow_id,
                additional_metadata=additional_metadata
            )
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            print(f"[OutputManager] 内容已保存到: {output_dir}")
            print(f"  - 推文: {tweet_path}")
            print(f"  - 图片: {image_path}")
            print(f"  - 元数据: {metadata_path}")

            return (output_dir, image_path, metadata_path)

        except Exception as e:
            raise RuntimeError(f"保存输出失败: {str(e)}")

    def _save_image(self, images, output_path):
        """
        保存图片张量到文件

        参数:
            images: 图片张量 (B, H, W, C) 或 (H, W, C)
            output_path: 输出路径
        """
        # 确保是numpy数组
        if isinstance(images, torch.Tensor):
            images = images.cpu().numpy()

        # 如果是批次，取第一张
        if len(images.shape) == 4:
            image = images[0]
        else:
            image = images

        # 转换到 [0, 255] 并确保是uint8
        if image.max() <= 1.0:
            image = (image * 255).astype(np.uint8)
        else:
            image = image.astype(np.uint8)

        # 保存图片
        pil_image = Image.fromarray(image)
        pil_image.save(output_path, format="PNG", optimize=True)

    def _build_metadata(
        self,
        user_id,
        date,
        tweet_text,
        scene_hint,
        persona,
        workflow_id,
        additional_metadata
    ):
        """构建元数据字典"""
        # 从人设提取信息
        persona_data = persona.get("data", {})
        persona_name = persona_data.get("name", "Unknown")

        # 提取LoRA信息（如果有）
        lora_config = persona_data.get("lora", {})
        lora_model = lora_config.get("model_name", "")
        lora_weight = lora_config.get("recommended_weight", 0.7)

        # 解析额外元数据
        extra_meta = {}
        if additional_metadata:
            try:
                extra_meta = json.loads(additional_metadata)
            except json.JSONDecodeError:
                print("[OutputManager] 警告: 无法解析additional_metadata")

        # 构建完整元数据
        metadata = {
            "user_id": user_id,
            "persona_name": persona_name,
            "date": date,
            "generated_at": datetime.now().isoformat(),
            "workflow_id": workflow_id,
            "content": {
                "tweet_text": tweet_text,
                "tweet_length": len(tweet_text),
                "scene_hint": scene_hint,
            },
            "lora": {
                "model": lora_model,
                "weight": lora_weight
            },
            **extra_meta  # 合并额外元数据
        }

        return metadata


# 节点注册
NODE_CLASS_MAPPINGS = {
    "OutputManager": OutputManager
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OutputManager": "Output Manager"
}
