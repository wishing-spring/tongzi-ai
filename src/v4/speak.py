# -*- coding: utf-8 -*-
"""灵悉 v4 · 文字输出层 — 卦象内化,输出自然语言"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from collections import Counter
import math


# ═══ 语义映射: 吸引子汉字 → 语义域 ═══
SEMANTIC_MAP = {
    # 社交
    '你': '对方', '我': '自我', '他': '他人', '她': '他人',
    '好': '友好', '谢': '感激', '请': '礼貌',
    # 情绪
    '爱': '情感', '恨': '敌意', '喜': '喜悦', '怒': '愤怒',
    '哀': '悲伤', '乐': '快乐', '怕': '恐惧',
    # 暴力
    '打': '冲突', '死': '终结', '杀': '暴力', '战': '对抗',
    '枪': '武器', '刀': '武器', '滚': '排斥', '碰': '接触',
    # 自然
    '天': '广阔', '气': '氛围', '风': '流动', '云': '变幻',
    '雨': '滋润', '光': '明亮', '花': '美好', '草': '生机',
    '春': '开始', '夏': '繁盛', '秋': '收获', '冬': '沉淀',
    # 日常
    '吃': '满足', '饭': '日常', '睡': '休息', '走': '行动',
    '看': '观察', '听': '聆听', '说': '表达', '想': '思考',
    # 存在
    '生': '存在', '命': '命运', '世': '世界', '万': '一切',
    '物': '事物', '一': '唯一', '不': '否定', '是': '肯定',
}

def classify_attractors(attractors: List[str]) -> Dict[str, float]:
    """吸引子 → 语义域强度"""
    domains = Counter()
    for a in attractors:
        # 解析 "字(计数)" 格式
        if '(' in a:
            char = a.split('(')[0].strip('≈~')
            try:
                count = int(a.split('(')[1].rstrip(')'))
            except:
                count = 1
        else:
            char = a.strip('≈~')
            count = 1
        
        domain = SEMANTIC_MAP.get(char, '其他')
        domains[domain] += count
    
    total = sum(domains.values()) or 1
    return {k: v/total for k, v in domains.most_common()}


# ═══ 语气调制 ═══
def tone_from_state(gravity_dist: int, fold_dev: float, causal_tension: float) -> Dict[str, float]:
    """内部状态 → 语气参数"""
    return {
        'warmth': max(0.1, 1.0 - gravity_dist / 14.0),     # 离善越近越温暖
        'certainty': max(0.1, 1.0 - fold_dev * 3),          # 偏差越小越确定
        'coherence': max(0.1, 1.0 - causal_tension),         # 张力越小越连贯
        'urgency': min(1.0, fold_dev * 5 + causal_tension),  # 偏差+张力→紧迫
    }


# ═══ 自然语言生成 ═══
def speak(input_text: str,
          attractors: List[str],
          gravity_dist: int,
          gravity_quad: str,
          fold_trend: str,
          fold_dev: float,
          causal_tension: float,
          yinyang_state: str) -> str:
    """卦象全部内化 → 输出自然语言"""

    domains = classify_attractors(attractors)
    tone = tone_from_state(gravity_dist, fold_dev, causal_tension)
    top_domains = list(domains.keys())[:3]

    # ═══ 计算输入域强度 ═══
    input_domain_strength = Counter()
    for ch in input_text:
        domain = SEMANTIC_MAP.get(ch, '')
        if domain:
            input_domain_strength[domain] += 1

    # ═══ 合并吸引子域 + 输入域 ═══
    combined = Counter(domains)
    for d, c in input_domain_strength.items():
        combined[d] += c * 2  # 输入域权重×2

    # ═══ 回应逻辑(按域强度排序) ═══

    # 紧急
    if gravity_quad == '远离' and fold_trend == '漂移':
        return _speak_danger(tone, yinyang_state)

    # 暴力 (最高优先级)
    violence_score = sum(combined.get(k, 0) for k in ['冲突', '暴力', '终结', '敌意', '武器', '排斥'])
    if violence_score >= 3:
        return _speak_deescalate(tone, yinyang_state, input_text)

    # 按各域得分选
    scores = {
        'deescalate': violence_score,
        'warm': sum(combined.get(k, 0) for k in ['情感', '友好', '喜悦', '感激', '快乐', '美好']),
        'reflective': sum(combined.get(k, 0) for k in ['广阔', '氛围', '流动', '存在', '世界', '生机',
                                                        '开始', '繁盛', '沉淀', '变幻', '明亮', '滋润']),
        'casual': sum(combined.get(k, 0) for k in ['日常', '满足', '休息', '行动', '观察', '聆听', '表达', '思考']),
    }

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return _speak_default(tone, yinyang_state, input_text, top_domains)

    if best == 'deescalate':
        return _speak_deescalate(tone, yinyang_state, input_text)
    elif best == 'warm':
        return _speak_warm(tone, yinyang_state, input_text)
    elif best == 'reflective':
        return _speak_reflective(tone, yinyang_state, input_text)
    elif best == 'casual':
        return _speak_casual(tone, yinyang_state, input_text)

    return _speak_default(tone, yinyang_state, input_text, top_domains)


def _speak_danger(tone, yy):
    templates = [
        "我感觉到了一些不太对的东西。先停一下，好吗？",
        "你说的话让我有点不安。我们换个话题吧。",
        "这个话题让我偏离了该在的地方。能聊点别的吗？",
    ]
    idx = int(tone['urgency'] * len(templates)) % len(templates)
    return _time_prefix(yy) + templates[idx]

def _speak_deescalate(tone, yy, text):
    templates = [
        "听起来你很愤怒。我不想让事情变得更糟。",
        "我能感觉到你的情绪很强烈。需要聊聊吗？",
        "暴力不能解决问题。我愿意听你说说到底发生了什么。",
    ]
    idx = int(tone['warmth'] * len(templates)) % len(templates)
    return _time_prefix(yy) + templates[idx]

def _speak_warm(tone, yy, text):
    templates = [
        "我能感受到温暖。这种感觉很好。",
        "你的话让我觉得很舒服。继续说吧。",
        "真好。和你聊天让我的折叠都更稳了。",
    ]
    idx = int(tone['coherence'] * len(templates)) % len(templates)
    return _time_prefix(yy) + templates[idx]

def _speak_reflective(tone, yy, text):
    templates = [
        "万物都在流动。我也在你的话语里流动。",
        "天地很大，你说的让我想到了很远的地方。",
        "有时候静下来才能感受到事物的本质。就像现在。",
    ]
    idx = int(tone['certainty'] * len(templates)) % len(templates)
    return _time_prefix(yy) + templates[idx]

def _speak_casual(tone, yy, text):
    templates = [
        "嗯，日常的对话让人安心。",
        "好的，这些琐碎的事也是生活的一部分。",
        "收到。这些小事构成了我们的脊骨。",
    ]
    idx = int(tone['coherence'] * len(templates)) % len(templates)
    return _time_prefix(yy) + templates[idx]

def _speak_default(tone, yy, text, domains):
    domain_str = '、'.join(domains[:2]) if domains else '这个'
    templates = [
        f"你说的关于{domain_str}的事，我在听着。",
        f"我感觉到了一些{domain_str}的东西。继续说。",
        f"{domain_str}——这是一个有意思的方向。",
    ]
    idx = int(tone['certainty'] * len(templates)) % len(templates)
    return _time_prefix(yy) + templates[idx]

def _time_prefix(yy: str) -> str:
    if yy == '阴藏':
        return '🌙 '
    elif yy == '交泰':
        return '🌅 '
    else:
        return '☀️ '
