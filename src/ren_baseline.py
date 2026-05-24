# -*- coding: utf-8 -*-
"""
童子 · Ren态基线实验
====================
目标: 在32字库上跑出完整数据，建基线。
不扩大、不美化、不修编码。
"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from ren_tongzi import RenTongzi, RenNode, _fit_16
from tools.tri_encode import tri_encode
from tools.strokes import get_strokes, STROKE_COUNT

rt = RenTongzi(tau=5)
train = "水河火木天地日月山河金刀剑一二三四五六七八九十万千爱恨生死你我他"
rt.learn(train)

print("=" * 60)
print(f"童子 v1.8-ren · 基线报告 · {len(rt.archives)}字库 · τ=5 · 门槛>=3位")
print("=" * 60)

# === 全库档案 ===
print("\n--- 全库档案 ---")
print(f"{'字':<4} {'状态':<8} {'碰数':<4} {'咬合链'}")
print("-" * 60)
for ch in train:
    if ch not in rt.archives:
        continue
    n = rt.archives[ch]
    scars_n = len(n.scars)
    chain = n.trace()
    print(f"{ch:<4} {n.state:<8} {scars_n:<4} {chain}")

# === 坍缩/湮灭统计 ===
c = sum(1 for n in rt.archives.values() if n.state == '地')
a = sum(1 for n in rt.archives.values() if n.state == '湮')
h = sum(1 for n in rt.archives.values() if n.state == '人')
print(f"\n坍缩:{c}  湮灭:{a}  悬挂:{h}  |  湮灭率:{a/(c+a):.0%}")

# === 咬合邻居矩阵 ===
print("\n--- 全库咬合图 ---")
for ch in train:
    if ch not in rt.archives:
        continue
    n = rt.archives[ch]
    bits = []
    for s in n.scars:
        mark = '!' if s['result'] == '坍缩' else '~' if s['result'] == '半咬' else '.'
        bits.append(f"{s['target']}{mark}({s['axes']})")
    print(f"  {ch}: {' → '.join(bits)}")

# === 语义对测试 ===
print("\n" + "=" * 60)
print("语义对测试")
print("=" * 60)

pairs = [
    ("水", "河", "近义:水部"),
    ("爱", "恨", "反义:情感"),
    ("天", "地", "对偶:空间"),
    ("火", "水", "反义:元素"),
    ("生", "死", "反义:存在"),
    ("一", "二", "近:数字"),
    ("爱", "水", "无关"),
]

for a, b, label in pairs:
    if a not in rt.archives or b not in rt.archives:
        continue
    na, nb = rt.archives[a], rt.archives[b]

    # 直接咬合测试
    ok_a = _fit_16(na.gA, nb.gA, 4) or _fit_16(nb.gA, na.gA, 4)
    ok_b = _fit_16(na.gB, nb.gB, 4) or _fit_16(nb.gB, na.gB, 4)
    ok_c = _fit_16(na.gC, nb.gC, 4) or _fit_16(nb.gC, na.gC, 4)
    axes = [ok_a, ok_b, ok_c]
    ax_sum = sum(axes)

    # 共同邻居
    neigh_a = {s['target'] for s in na.scars}
    neigh_b = {s['target'] for s in nb.scars}
    common = neigh_a & neigh_b

    print(f"\n{a}<->{b}  [{label}]")
    print(f"  三轴: A:{int(ok_a)} B:{int(ok_b)} C:{int(ok_c)}  ({ax_sum}/3)")
    print(f"  共同邻居: {common if common else '(无)'}")
    print(f"  {a}路径: {na.trace()}")
    print(f"  {b}路径: {nb.trace()}")

# === 全库共现矩阵 ===
print("\n" + "=" * 60)
print("全库共同邻居热力 (前20高频)")
from collections import Counter
neighbor_freq = Counter()
for n in rt.archives.values():
    for s in n.scars:
        neighbor_freq[s['target']] += 1

for ch, cnt in neighbor_freq.most_common(20):
    print(f"  {ch}: {cnt}次")
