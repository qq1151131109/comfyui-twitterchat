"""
Persona Input Nodes
人设输入节点 - 从图片或文本开始生成人设
"""

import os
import base64
import json
import requests
import torch
import numpy as np
from PIL import Image
import io


class PersonaImageInput:
    """
    从图片开始生成人设的输入节点
    使用Vision LLM分析图片外貌，作为人设生成的基础
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),  # ComfyUI图像输入
                "name": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "留空则自动生成名字"
                }),
                "age": ("INT", {
                    "default": 23,
                    "min": 18,
                    "max": 35,
                    "step": 1
                }),
                "persona_type": ([
                    "bdsm_sub",
                    "bdsm_dom",
                    "fitness_girl",
                    "artist",
                    "neighbor",
                    "office_worker",
                    "student",
                    "attractive-woman"
                ], {
                    "default": "attractive-woman"
                }),
                "nsfw_level": (["soft", "medium", "high"], {
                    "default": "medium"
                }),
                "api_key": ("STRING", {
                    "default": "sk-7U0E6zRslf3aUM2Z9DcEIbaWxDY3aRZbR5Wq4g0TKw0IPe1L",
                    "multiline": False
                }),
                "api_base": ("STRING", {
                    "default": "https://www.dmxapi.cn/v1",
                    "multiline": False
                }),
                "vision_model": ("STRING", {
                    "default": "gpt-4-turbo",
                    "multiline": False,
                    "placeholder": "gpt-4-turbo, gpt-4o, gpt-4.1等"
                })
            },
            "optional": {
                "location": ("STRING", {
                    "default": "United States",
                    "multiline": False
                })
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("image", "appearance_analysis", "base_params_json", "suggested_name")
    FUNCTION = "analyze_image"
    CATEGORY = "twitterchat/persona"

    def tensor_to_pil(self, tensor):
        """将ComfyUI的tensor转换为PIL Image"""
        # tensor shape: [B, H, W, C]
        i = 255. * tensor.cpu().numpy().squeeze()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        return img

    def pil_to_base64(self, pil_image):
        """将PIL Image转换为base64"""
        buffered = io.BytesIO()
        pil_image.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')

    def analyze_image(self, image, name, age, persona_type, nsfw_level,
                     api_key, api_base, vision_model, location="United States"):
        """
        分析图片外貌，生成人设基础参数
        """

        print(f"\n{'='*70}")
        print(f"🎭 PersonaImageInput: Analyzing image")
        print(f"{'='*70}")

        # 转换图像为PIL和base64
        pil_image = self.tensor_to_pil(image)
        base64_image = self.pil_to_base64(pil_image)
        image_url = f"data:image/png;base64,{base64_image}"

        # 构建vision prompt
        vision_prompt = self._build_vision_prompt(persona_type, nsfw_level)

        # 调用Vision API
        try:
            appearance_analysis = self._call_vision_api(
                image_url,
                vision_prompt,
                api_key,
                api_base,
                vision_model
            )

            print(f"✅ Image analysis complete ({len(appearance_analysis)} characters)")
            print(f"\n📝 Appearance Analysis Preview:")
            print(f"{appearance_analysis[:300]}...")

        except Exception as e:
            print(f"❌ Vision API call failed: {str(e)}")
            # 使用fallback
            appearance_analysis = f"Unable to analyze image: {str(e)}"

        # 从分析中提取建议的名字（如果未指定）
        suggested_name = name if name.strip() else self._extract_name_from_analysis(appearance_analysis, persona_type)

        # 构建base_params
        base_params = {
            "name": suggested_name,
            "age": age,
            "persona_type": persona_type,
            "nsfw_level": nsfw_level,
            "location": location,
            "image_analyzed": True
        }

        base_params_json = json.dumps(base_params, ensure_ascii=False, indent=2)

        print(f"\n📋 Base Parameters:")
        print(f"   Name: {suggested_name}")
        print(f"   Age: {age}")
        print(f"   Type: {persona_type}")
        print(f"   NSFW Level: {nsfw_level}")
        print(f"{'='*70}\n")

        return (image, appearance_analysis, base_params_json, suggested_name)

    def _build_vision_prompt(self, persona_type, nsfw_level):
        """构建vision分析的prompt"""

        nsfw_desc = {
            'soft': 'subtle sensuality, flirty but classy',
            'medium': 'moderately sexual, comfortable with suggestive content',
            'high': 'very explicit, comfortable with NSFW content'
        }.get(nsfw_level, 'moderately sexual')

        type_desc = {
            'bdsm_sub': 'BDSM submissive persona',
            'bdsm_dom': 'BDSM dominant persona',
            'fitness_girl': 'Fitness enthusiast',
            'artist': 'Creative artist',
            'neighbor': 'Girl-next-door',
            'office_worker': 'Professional office worker',
            'student': 'College/university student',
            'attractive-woman': 'Attractive, confident woman'
        }.get(persona_type, 'Attractive woman')

        return f"""Analyze this portrait photo in detail for creating a social media persona.

Target persona type: {type_desc}
Content style: {nsfw_desc}

Provide a detailed analysis covering:

1. **Physical Appearance**:
   - Hair: Exact color (platinum blonde/dark brown/auburn/etc.), length (shoulder-length/long/short), style (straight/wavy/curly)
   - Eyes: Exact color (blue/green/brown/hazel)
   - Face: Facial structure, features, makeup style if visible
   - Body type: Slim/athletic/curvy/petite/etc. Be specific
   - Estimated age range
   - Ethnicity/background (for name suggestions)

2. **Style & Aesthetic**:
   - Clothing style visible in photo
   - Fashion sense (casual/elegant/sporty/alternative)
   - Overall vibe (sweet/sexy/confident/mysterious)

3. **Inferred Personality** (based on visual cues):
   - Expression: Confident/shy/playful/serious?
   - Energy: High-energy/calm/sultry?
   - Approachability: Girl-next-door/sophisticated/edgy?

4. **Social Media Appeal**:
   - What makes her attractive to followers?
   - Natural "hook" based on appearance
   - Suggested content style

Output in natural paragraph format, be VERY specific about colors, styles, and details."""

    def _call_vision_api(self, image_url, prompt, api_key, api_base, model):
        """调用Vision API分析图片"""

        url = f"{api_base.rstrip('/')}/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        data = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        print(f"🔍 Calling Vision API ({model})...")

        response = requests.post(url, headers=headers, json=data, timeout=120)
        response.raise_for_status()

        result = response.json()
        content = result['choices'][0]['message']['content']

        return content

    def _extract_name_from_analysis(self, analysis, persona_type):
        """从分析中提取或生成建议的名字"""

        # 简单的名字建议逻辑（可以改进为LLM生成）
        name_pools = {
            'bdsm_sub': ['Kitten', 'Pet', 'Luna', 'Chloe', 'Mia', 'Sophia'],
            'bdsm_dom': ['Mistress Luna', 'Lady Victoria', 'Goddess Aria'],
            'fitness_girl': ['Lily', 'Maya', 'Kayla', 'Ashley', 'Brittany'],
            'artist': ['Emily', 'Zoe', 'Luna', 'Aria', 'Indie'],
            'neighbor': ['Emma', 'Olivia', 'Sarah', 'Jessica', 'Amy'],
            'office_worker': ['Rachel', 'Michelle', 'Jennifer', 'Lisa'],
            'student': ['Sophie', 'Hannah', 'Chloe', 'Madison', 'Taylor'],
            'attractive-woman': ['Sophia', 'Isabella', 'Mia', 'Charlotte', 'Amelia']
        }

        import random
        pool = name_pools.get(persona_type, name_pools['attractive-woman'])
        return random.choice(pool)


class PersonaTextInput:
    """
    从文本描述开始生成人设的输入节点
    不需要图片，直接从文字描述创建人设
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "name": ("STRING", {
                    "default": "Emily",
                    "multiline": False
                }),
                "age": ("INT", {
                    "default": 23,
                    "min": 18,
                    "max": 35,
                    "step": 1
                }),
                "persona_type": ([
                    "bdsm_sub",
                    "bdsm_dom",
                    "fitness_girl",
                    "artist",
                    "neighbor",
                    "office_worker",
                    "student",
                    "attractive-woman"
                ], {
                    "default": "attractive-woman"
                }),
                "nsfw_level": (["soft", "medium", "high"], {
                    "default": "medium"
                }),
                "personality": ("STRING", {
                    "default": "friendly, outgoing, creative, confident",
                    "multiline": False,
                    "placeholder": "用逗号分隔的性格特征"
                }),
                "appearance_description": ("STRING", {
                    "default": "Long blonde hair, blue eyes, athletic build, casual style",
                    "multiline": True,
                    "placeholder": "外貌描述：头发、眼睛、身材、风格等"
                })
            },
            "optional": {
                "occupation": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "例如：barista, graphic designer"
                }),
                "interests": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "例如：yoga, photography, coffee"
                }),
                "location": ("STRING", {
                    "default": "United States",
                    "multiline": False
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("appearance_analysis", "base_params_json")
    FUNCTION = "create_params"
    CATEGORY = "twitterchat/persona"

    def create_params(self, name, age, persona_type, nsfw_level, personality,
                     appearance_description, occupation="", interests="", location="United States"):
        """
        从文本创建人设参数
        """

        print(f"\n{'='*70}")
        print(f"📝 PersonaTextInput: Creating parameters")
        print(f"{'='*70}")

        # appearance_analysis就是用户输入的外貌描述
        appearance_analysis = appearance_description

        # 构建base_params
        base_params = {
            "name": name,
            "age": age,
            "persona_type": persona_type,
            "nsfw_level": nsfw_level,
            "location": location,
            "personality": personality,
            "image_analyzed": False
        }

        if occupation:
            base_params["occupation"] = occupation
        if interests:
            base_params["interests"] = interests

        base_params_json = json.dumps(base_params, ensure_ascii=False, indent=2)

        print(f"\n📋 Parameters Created:")
        print(f"   Name: {name}")
        print(f"   Age: {age}")
        print(f"   Type: {persona_type}")
        print(f"   Personality: {personality}")
        print(f"   Appearance: {appearance_description[:100]}...")
        print(f"{'='*70}\n")

        return (appearance_analysis, base_params_json)


# 节点映射
NODE_CLASS_MAPPINGS = {
    "PersonaImageInput": PersonaImageInput,
    "PersonaTextInput": PersonaTextInput
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PersonaImageInput": "Persona Image Input 🎭",
    "PersonaTextInput": "Persona Text Input 📝"
}
