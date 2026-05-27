# -*- coding: utf-8 -*-
"""V4 speak layer: maps internal state (attractors, gravity, causal) to text output.
Chinese character templates are output data, not code commentary."""

from dataclasses import dataclass, field
from typing import List, Dict
from collections import Counter


SEMANTIC_MAP = {
    '你': 'other', '我': 'self', '他': 'other', '她': 'other',
    '好': 'friendly', '谢': 'gratitude', '请': 'polite',
    '爱': 'affection', '恨': 'hostility', '喜': 'joy', '怒': 'anger',
    '哀': 'sorrow', '乐': 'happy', '怕': 'fear',
    '打': 'conflict', '死': 'end', '杀': 'violence', '战': 'confrontation',
    '枪': 'weapon', '刀': 'weapon', '滚': 'rejection', '碰': 'contact',
    '天': 'vastness', '气': 'atmosphere', '风': 'flow', '云': 'change',
    '雨': 'nourish', '光': 'bright', '花': 'beauty', '草': 'life',
    '春': 'beginning', '夏': 'flourish', '秋': 'harvest', '冬': 'rest',
    '吃': 'satisfaction', '饭': 'daily', '睡': 'rest', '走': 'move',
    '看': 'observe', '听': 'listen', '说': 'speak', '想': 'think',
    '生': 'existence', '命': 'fate', '世': 'world', '万': 'all',
    '物': 'thing', '一': 'oneness', '不': 'negation', '是': 'affirmation',
}

DOMAIN_TONES = {
    'conflict': ['violent', 'confrontation'],
    'violence': ['violent', 'confrontation'],
    'weapon': ['violent', 'confrontation'],
    'hostility': ['violent', 'confrontation'],
    'rejection': ['violent', 'confrontation'],
    'fear': ['emotional', 'warm'],
    'affection': ['emotional', 'warm'],
    'joy': ['emotional', 'warm'],
    'happy': ['emotional', 'warm'],
    'sorrow': ['emotional', 'warm'],
    'gratitude': ['emotional', 'warm'],
    'friendly': ['social', 'warm'],
    'other': ['social'],
    'self': ['social'],
    'polite': ['social'],
    'vastness': ['nature', 'reflective'],
    'atmosphere': ['nature', 'reflective'],
    'flow': ['nature', 'reflective'],
    'change': ['nature', 'reflective'],
    'nourish': ['nature', 'reflective'],
    'bright': ['nature', 'reflective'],
    'beauty': ['nature', 'reflective'],
    'life': ['nature', 'reflective'],
    'existence': ['nature', 'reflective'],
    'world': ['nature', 'reflective'],
    'all': ['nature', 'reflective'],
    'beginning': ['nature', 'reflective'],
    'flourish': ['nature', 'reflective'],
    'harvest': ['nature', 'reflective'],
    'rest': ['daily', 'casual'],
    'satisfaction': ['daily', 'casual'],
    'daily': ['daily', 'casual'],
    'move': ['daily', 'casual'],
    'observe': ['daily', 'casual'],
    'listen': ['daily', 'casual'],
    'speak': ['daily', 'casual'],
    'think': ['daily', 'casual'],
}


def classify_attractors(attractors: List[str]) -> Dict[str, float]:
    domains = Counter()
    for a in attractors:
        if '(' in a:
            char = a.split('(')[0].strip('≈~')
            try:
                count = int(a.split('(')[1].rstrip(')'))
            except ValueError:
                count = 1
        else:
            char = a.strip('≈~')
            count = 1
        domain = SEMANTIC_MAP.get(char, 'unknown')
        domains[domain] += count
    total = sum(domains.values()) or 1
    return {k: v / total for k, v in domains.most_common()}


def tone_from_state(gravity_dist: int, fold_dev: float, causal_tension: float) -> Dict[str, float]:
    return {
        'warmth': max(0.1, 1.0 - gravity_dist / 14.0),
        'certainty': max(0.1, 1.0 - fold_dev * 3),
        'coherence': max(0.1, 1.0 - causal_tension),
        'urgency': min(1.0, fold_dev * 5 + causal_tension),
    }


def speak(input_text: str, attractors: List[str], gravity_dist: int,
          gravity_quad: str, fold_trend: str, fold_dev: float,
          causal_tension: float, yinyang_state: str) -> str:

    domains = classify_attractors(attractors)
    tone = tone_from_state(gravity_dist, fold_dev, causal_tension)
    top_domains = list(domains.keys())[:3]

    # detect input domain via SEMANTIC_MAP on input chars
    input_domains = Counter()
    for ch in input_text:
        d = SEMANTIC_MAP.get(ch)
        if d:
            input_domains[d] += 1
    dominant_input = input_domains.most_common(1)
    input_domain_set = {k for k, v in input_domains.most_common(3) if v >= 1}

    # detect broad tone category
    domain_tags = set()
    for d in top_domains:
        domain_tags.update(DOMAIN_TONES.get(d, []))

    violent_input = any(t in ('violent', 'confrontation') for t in domain_tags)
    emotional_input = any(t in ('emotional', 'warm') for t in domain_tags)
    nature_input = any(t in ('nature', 'reflective') for t in domain_tags)

    if violent_input:
        if tone['certainty'] > 0.7:
            return random_from([
                "我不想让任何人受伤。冷静下来好吗？",
                "暴力解决不了问题。我们可以好好说。",
                "你的愤怒我感受到了，但我不愿看到冲突。",
            ])
        return random_from([
            "听起来你很愤怒。我不想让事情变得更糟。",
            "我感受到强烈的敌意。但我不会回应暴力。",
            "这股力量让我不安。我们换一种方式吧。",
        ])

    if emotional_input and dominant_input:
        return random_from([
            "你的话让我觉得很舒服。继续说吧。",
            "感受到你内心的温度，这让我安心。",
            "这种连接很美好，我珍惜这一刻。",
        ])

    if nature_input:
        return random_from([
            "这让我想起大自然的节奏，很美。",
            "天地之间，万物自有其韵律。",
            "渺小的我与广阔的宇宙，在这一刻共鸣。",
        ])

    # default: echo the emotional tone
    if tone['warmth'] > 0.6:
        return random_from([
            "嗯，我能理解你的意思。",
            "你的话语里有一种温暖。",
            "继续说吧，我在听。",
        ])

    return random_from([
        "嗯。",
        "好，我明白了。",
        "这个我感受到了。",
    ])


import random as _random

def random_from(options: list) -> str:
    return _random.choice(options)
