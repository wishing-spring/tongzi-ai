# -*- coding: utf-8 -*-
"""童子 v3.0 · 对话测试 · 完整碰撞追踪"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from v3.tongzi import TongziV3
from v3.eco_pool import EcoPool
from v3.express import express
from collections import Counter, defaultdict

# ═══ 初始化 ═══
import v3.eco_pool as ep
ep.F0 = 32

tz = TongziV3()
tz.add(EcoPool("🔥快生", tau=3, fit_min=2, birth_rate=1.5, flow_back=True,
               density_max=128, stagnation_window=2, jitter_bits=5))
tz.add(EcoPool("⚡涌动", tau=5, fit_min=2, birth_rate=1.2, flow_back=True,
               density_max=96, stagnation_window=2, jitter_bits=5))

# ═══ 对话 ═══
question = "今天天气真好风轻云淡阳光灿烂"
answer   = "春风吹过花开满地草长莺飞万物生"

print("╔══════════════════════════════════════════════╗")
print("║           童 子 对 话 测 试                    ║")
print("╚══════════════════════════════════════════════╝")
print(f"\n  问: {question}")
print(f"  答: {answer}")

all_chars = list(dict.fromkeys(list(question) + list(answer)))
tz.feed(" ".join(all_chars))

natives = [g for g in tz.surge.all() if g.is_native]
native_by_ct = {g.ct: g for g in natives}
print(f"\n  喂入 {len(native_by_ct)} 字 × 4 花色 = {len(natives)} 原生卦")

# ═══ 跑 600 tick ═══
print(f"\n{'tick':>5s} {'孩子':>7s} {'反熵':>4s}  碰撞热词")
print(f"{'─'*5} {'─'*7} {'─'*4}  {'─'*35}")

prev_b = 0
for _ in range(600):
    tz.tick()
    
    if tz.global_tick % 150 == 0:
        births = sum(e.total_births for e in tz.eco)
        jitters = sum(e.antientropy.total_jitters for e in tz.eco)
        
        # 采样最近孩子
        recent = Counter()
        for e in tz.eco:
            for g in e.guas[-300:]:
                if not g.is_native:
                    ct = g.ct
                    best, best_dist = "?", 99
                    for nct in native_by_ct:
                        d = bin(ct ^ nct).count('1')
                        if d < best_dist:
                            best_dist = d
                            best = express(native_by_ct[nct], natives)
                    tag = best if best_dist == 0 else f"≈{best}"
                    recent[tag] += 1
        
        top = ' '.join(f'{n}:{c}' for n,c in recent.most_common(5))
        print(f"{tz.global_tick:5d} {births:7d} {jitters:4d}  {top}")

natives = [g for g in tz.surge.all() if g.is_native]
native_by_ct = {g.ct: g for g in natives}

# ═══ 输出 ═══
def short_name(g): 
    ct = g.ct
    best, best_dist = "?", 99
    for nct in native_by_ct:
        d = bin(ct ^ nct).count('1')
        if d < best_dist:
            best_dist = d
            best = express(native_by_ct[nct], natives)
    return best, best_dist

print(f"\n╔══ 对话输出 ═══════════════════════════════════╗")

births = sum(e.total_births for e in tz.eco)
solid = sum(e.total_solid for e in tz.eco)
jitters = sum(e.antientropy.total_jitters for e in tz.eco)

print(f"║  {births} 孩子 · {solid} 固化 · {jitters} 反熵注入")
print(f"║")

# 孩子映射到最近字
name_dist = Counter()
for e in tz.eco:
    for g in e.guas:
        if not g.is_native:
            name, dist = short_name(g)
            tag = name if dist == 0 else f"≈{name}(±{dist})"
            name_dist[tag] += 1

total_children = sum(name_dist.values())
print(f"║  系统回应 (孩子 → 最近输入字):")
for tag, cnt in name_dist.most_common(12):
    bar_len = int(cnt / total_children * 50) if total_children else 0
    bar = '█' * bar_len
    print(f"║  {tag:14s} {cnt:6d} {bar}")

# 碰撞兄弟对
born_groups = defaultdict(list)
for e in tz.eco:
    for g in e.guas:
        if not g.is_native:
            born_groups[g.born_tick].append(g)

collision_pairs = Counter()
for tick, group in born_groups.items():
    if len(group) >= 2:
        for i in range(len(group)):
            for j in range(i+1, len(group)):
                n1, _ = short_name(group[i])
                n2, _ = short_name(group[j])
                if n1 > n2: n1, n2 = n2, n1
                collision_pairs[f"{n1}↔{n2}"] += 1

print(f"║")
print(f"║  最热碰撞对 (同tick出生):")
for pair, cnt in collision_pairs.most_common(8):
    bar_len = min(cnt // 2, 25)
    bar = '─' * bar_len
    print(f"║  {pair:20s} {cnt:4d} {bar}")

# 读环：固化链
print(f"║")
print(f"║  固化链 (读环):")
for e in tz.eco:
    solids = [g for g in e.guas if not g.is_native]
    if solids:
        chain_names = []
        for g in solids[-12:]:
            n, _ = short_name(g)
            if not chain_names or n != chain_names[-1]:
                chain_names.append(n)
        if chain_names:
            print(f"║  {e.name}: {' → '.join(chain_names[-6:])}")

# 输入 vs 输出
input_set = set(all_chars)
output_set = set()
for tag in name_dist:
    output_set.add(tag.split('≈')[-1].split('(')[0])

print(f"║")
print(f"║  输入: {' '.join(sorted(input_set))}")
top_out = [tag.split('≈')[-1].split('(')[0] for tag,_ in name_dist.most_common(5)]
print(f"║  输出: {' '.join(top_out)}")
print(f"║  新增: {' '.join(output_set - input_set)}")
print(f"║  丢失: {' '.join(input_set - output_set)}")

print(f"╚══════════════════════════════════════════════╝")

print(f"\n  问: {question}")
print(f"  答: {answer}")
print(f"  → 童子: {' '.join(top_out)}")
