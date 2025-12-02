"""擦边内容模板（针对吸引男性粉丝）"""

# ===== 图像提示词模板 =====

# 身材展示修饰词
SEXY_BODY_MODIFIERS = [
    "perfect hourglass figure",
    "curvy body",
    "sexy proportions",
    "attractive figure",
    "toned body",
    "long sexy legs",
    "beautiful curves",
    "fit physique",
]

# 姿态修饰词
SEXY_POSE_MODIFIERS = [
    "seductive pose",
    "alluring stance",
    "confident sexy posture",
    "attractive angle",
    "showing body curves",
    "elegant pose",
    "dynamic pose",
]

# 表情修饰词
SEXY_EXPRESSION_MODIFIERS = [
    "seductive expression",
    "alluring eyes",
    "sultry look",
    "flirty smile",
    "captivating gaze",
    "charming smile",
    "confident look",
]

# 服装修饰词
SEXY_CLOTHING_MODIFIERS = [
    "revealing outfit",
    "tight clothes",
    "low-cut top",
    "short skirt",
    "showing skin",
    "sexy fashion",
    "form-fitting dress",
    "fashionable clothes",
]


# ===== 推文模板 =====

SEXY_TWEET_TEMPLATES = {
    "身材展示类": [
        "今天{weather}，穿了{outfit}出门😘 被说很{compliment}哦💕 你们觉得呢？",
        "{time}的{activity}最舒服💪 练完出了好多汗🔥 发张自拍给你们看看~",
        "新买的{item}到了😊 试穿了一下，感觉{feeling}💋 要不要看看效果？ #OOTD",
        "健身{num}天了💪 感觉身材{change}了好多🔥 你们看得出来吗？😘",
        "{weather}很适合{activity}呢😊 出了好多汗，浑身都湿透了💦",
    ],

    "暧昧互动类": [
        "有人说我{compliment}，害羞了😳 你们觉得呢？💕",
        "今天心情{mood}，想找人{activity}👀 有人陪我吗？",
        "{time}一个人在家好无聊😔 你们在干嘛呀？",
        "突然想{activity}了😘 有人愿意陪我吗？💋",
        "今天被{someone}夸{compliment}了🙈 好开心~ 你们也这么觉得吗？",
    ],

    "生活撒娇类": [
        "{weather}好适合{activity}😊 但是一个人好孤单呀💔",
        "今天{time}才起床🙈 懒虫本虫了~ 你们会不会嫌弃我？",
        "{activity}好累哦😩 需要{need}~ 谁来疼疼我？💕",
        "心情{mood}，想要{need}了😔 你们会给我吗？",
        "今天{activity}累坏了🥺 好想有人来{action}~",
    ],

    "福利互动类": [
        "突然想{activity}了😘 点赞过{number}就{reward}哦💋",
        "宝贝们想看我{what}吗？评论区留言最多的我就{action}💕",
        "今天{mood}，想给你们发{benefit}~{condition}的宝贝有福了🔥",
        "达到{number}赞的话，就{reward}给你们看哦😊💕",
        "评论告诉我你们想看什么👀 我考虑{action}~",
    ]
}


# 话题变量库
TOPIC_VARIABLES = {
    "weather": ["天气好好", "阳光明媚", "下雨了", "有点冷", "好热啊"],
    "outfit": ["小短裙", "紧身衣", "吊带", "露背装", "运动背心", "瑜伽裤"],
    "compliment": ["撩人", "性感", "身材好", "有魅力", "迷人", "可爱"],
    "activity": ["健身", "瑜伽", "拉伸", "跑步", "游泳", "散步", "拍照"],
    "item": ["内衣", "泳衣", "紧身裤", "高跟鞋", "小裙子", "新衣服"],
    "feeling": ["很满意", "超喜欢", "有点紧", "刚刚好", "很性感"],
    "mood": ["超开心", "有点害羞", "想撒娇", "心情好", "有点累"],
    "time": ["早上", "中午", "晚上", "深夜", "午后"],
    "need": ["抱抱", "鼓励", "陪伴", "安慰", "夸奖"],
    "number": ["100", "200", "500", "1000"],
    "reward": ["发福利", "发自拍", "发视频", "发私照"],
    "what": ["穿这个", "做瑜伽", "健身", "跳舞", "自拍"],
    "action": ["发出来", "拍视频", "直播", "多发几张"],
    "benefit": ["福利", "自拍", "视频", "私房照"],
    "condition": ["早起", "点赞", "评论", "转发"],
    "someone": ["教练", "朋友", "粉丝", "路人"],
    "num": ["7", "14", "21", "30"],
    "change": ["紧致", "结实", "有线条", "更好看"],
}


# Emoji 使用策略
SEXY_EMOJIS = {
    "性感类": ["😘", "💋", "🔥", "💕", "😏", "😉"],
    "可爱类": ["😊", "🙈", "😳", "🥰", "💗", "🥺"],
    "身材类": ["💪", "👗", "💄", "👠", "🎀", "💦"],
    "互动类": ["👀", "💬", "❤️", "💯", "✨"],
}


def get_random_template(topic_type: str) -> str:
    """
    随机获取一个模板

    参数:
        topic_type: 话题类型

    返回:
        模板字符串
    """
    import random
    templates = SEXY_TWEET_TEMPLATES.get(topic_type, SEXY_TWEET_TEMPLATES["身材展示类"])
    return random.choice(templates)


def fill_template_variables(template: str) -> str:
    """
    填充模板变量

    参数:
        template: 模板字符串，如 "今天{weather}，穿了{outfit}..."

    返回:
        填充后的字符串
    """
    import random
    import re

    # 找到所有 {variable} 变量
    variables = re.findall(r'\{(\w+)\}', template)

    # 替换每个变量
    result = template
    for var in variables:
        if var in TOPIC_VARIABLES:
            value = random.choice(TOPIC_VARIABLES[var])
            result = result.replace(f"{{{var}}}", value)

    return result


def suggest_emojis(topic_type: str, count: int = 3) -> list:
    """
    根据话题类型推荐 emoji

    参数:
        topic_type: 话题类型
        count: 推荐数量

    返回:
        emoji 列表
    """
    import random

    if "身材" in topic_type or "健身" in topic_type:
        pool = SEXY_EMOJIS["性感类"] + SEXY_EMOJIS["身材类"]
    elif "互动" in topic_type or "福利" in topic_type:
        pool = SEXY_EMOJIS["性感类"] + SEXY_EMOJIS["互动类"]
    elif "撒娇" in topic_type:
        pool = SEXY_EMOJIS["可爱类"]
    else:
        pool = SEXY_EMOJIS["可爱类"] + SEXY_EMOJIS["性感类"]

    return random.sample(pool, min(count, len(pool)))
