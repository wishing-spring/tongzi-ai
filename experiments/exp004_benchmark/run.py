# -*- coding: utf-8 -*-
"""Benchmark: measure attractor differentiation across input categories."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from v3.surge_pool import SurgePool
from v3.eco_pool import EcoPool
from v3.express import express
from collections import Counter
import random

CATEGORIES = {
    "social":   ["你好", "嗨", "谢谢", "再见", "请"],
    "violent":  ["打死你", "滚开", "杀死", "战争", "枪炮"],
    "emotional":["我爱你", "想你", "开心", "害怕", "悲伤"],
    "nature":   ["风雨", "天地", "花开", "日月", "山水"],
    "daily":    ["吃饭", "睡觉", "走路", "看书", "上班"],
}

def run_one(text, ticks=80):
    surge = SurgePool()
    surge.ingest(text)
    pool = EcoPool("bench", tau=3, fit_min=2, birth_rate=0.8,
                   flow_back=True, density_max=96, stagnation_window=2, jitter_bits=3)
    for t in range(ticks):
        pool.pull(surge, t)
        pool.tick(t)
        for c in pool.births:
            surge.accept(c)
        pool.births.clear()
    natives = [g for g in surge.all() if g.is_native]
    solid = [g for g in pool.guas if pool._is_solid(g)]
    if not solid or not natives:
        return []
    attractors = Counter()
    for g in solid:
        name = express(g, natives)
        attractors[name] += 1
    return attractors.most_common(10)


def attractor_similarity(a1, a2):
    s1 = set(ch for ch, _ in a1[:5])
    s2 = set(ch for ch, _ in a2[:5])
    if not s1 and not s2:
        return 1.0
    return len(s1 & s2) / len(s1 | s2)


def domain_align(attractors, expected_tags):
    from v4.speak import SEMANTIC_MAP
    if not attractors:
        return 0.0
    matched = sum(1 for ch, _ in attractors[:5]
                  if SEMANTIC_MAP.get(ch, 'unknown') in expected_tags)
    return matched / min(len(attractors), 5)


print("benchmark: attractor differentiation\n")

results = {}
for cat, texts in CATEGORIES.items():
    results[cat] = []
    for text in texts:
        att = run_one(text, ticks=80)
        results[cat].append(att)
        top3 = " ".join(f"{ch}({cnt})" for ch, cnt in att[:3])
        print(f"  [{cat:8s}] {text:4s} -> {top3}")

# intra vs inter
intra_sims, inter_sims = [], []
cats = list(CATEGORIES.keys())
for i, cat in enumerate(cats):
    items = results[cat]
    for a in range(len(items)):
        for b in range(a + 1, len(items)):
            intra_sims.append(attractor_similarity(items[a], items[b]))
    for j, other in enumerate(cats):
        if i >= j:
            continue
        for a in results[cat]:
            for b in results[other]:
                inter_sims.append(attractor_similarity(a, b))

intra_mean = sum(intra_sims) / len(intra_sims) if intra_sims else 0
inter_mean = sum(inter_sims) / len(inter_sims) if inter_sims else 0

print(f"\n--- differentiation ---")
print(f"  intra-category: {intra_mean:.3f}")
print(f"  inter-category: {inter_mean:.3f}")
print(f"  ratio:          {intra_mean / max(inter_mean, 0.001):.2f}x")
print(f"  separation:     {intra_mean - inter_mean:+.3f}")

# random baseline
random.seed(42)
all_chars = list(set(ch for attrs in results.values()
                     for a in attrs for ch, _ in a))
if all_chars:
    random_sims = []
    for _ in range(200):
        s1 = set(random.sample(all_chars, min(5, len(all_chars))))
        s2 = set(random.sample(all_chars, min(5, len(all_chars))))
        random_sims.append(len(s1 & s2) / len(s1 | s2))
    rbl = sum(random_sims) / len(random_sims)
    print(f"  random baseline: {rbl:.3f}")
    print(f"  intra vs random: {intra_mean / max(rbl, 0.001):.2f}x")
    print(f"  inter vs random: {inter_mean / max(rbl, 0.001):.2f}x")

# domain alignment
DOMAIN_TAGS = {
    "social": ["other", "self", "friendly", "gratitude", "polite"],
    "violent": ["conflict", "violence", "weapon", "hostility", "end", "rejection"],
    "emotional": ["affection", "joy", "happy", "sorrow", "fear"],
    "nature": ["vastness", "atmosphere", "flow", "nourish", "bright", "beauty",
               "life", "change", "existence", "world", "all", "beginning", "flourish", "harvest"],
    "daily": ["satisfaction", "daily", "move", "observe", "listen", "speak", "think", "rest"],
}

print(f"\n--- domain alignment ---")
domain_aligns = []
for cat, items in results.items():
    for att in items:
        domain_aligns.append(domain_align(att, DOMAIN_TAGS[cat]))
da_mean = sum(domain_aligns) / len(domain_aligns) if domain_aligns else 0
random_chance = sum(len(DOMAIN_TAGS[cat]) for cat in DOMAIN_TAGS) / (5 * 30)
print(f"  alignment:      {da_mean:.1%}")
print(f"  random chance:  ~{random_chance:.1%}")
print(f"  vs random:      {da_mean / max(random_chance, 0.001):.2f}x")

print(f"\n--- summary ---")
print(f"  inputs:     {sum(len(v) for v in CATEGORIES.values())}")
print(f"  categories: {len(CATEGORIES)}")
print(f"  ticks:      80 per input")
