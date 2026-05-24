# -*- coding: utf-8 -*-
"""
童子 v1.8 · 100字扩展测试
==========================
A: A轴笔画高位 B: 全候选最优 C: 100字符库
"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from ren_tongzi import RenTongzi, _fit_16
from tools.strokes import STROKE_COUNT
from collections import Counter

# ==================== 100字符库 ====================
train = (
    # 自然 (20)
    "水河火木天地日月星云风雨雷电山水土金石"
    # 生命 (15)
    "你我他爱恨生死人女男父母心身体家"
    # 动作 (15)
    "走跑飞说看听吃打开关上下出入"
    # 数字 (15)
    "一二三四五六七八九十百千万"
    # 物品 (15)
    "刀剑门车灯书本笔纸桌凳衣帽帽"
    # 抽象 (20)
    "大小长短高多少好坏新旧美丑红白光明暗"
)

# 去重
seen = set()
chars = []
for ch in train:
    if ch not in seen:
        seen.add(ch)
        chars.append(ch)
train = ''.join(chars)

print(f"有效字符: {len(train)}")

# ==================== 学习 ====================
rt = RenTongzi(tau=5)
rt.learn(train)

# ==================== 统计 ====================
r = sum(1 for n in rt.archives.values() if n.state == 'result')
p = sum(1 for n in rt.archives.values() if n.state == 'pruned')
h = sum(1 for n in rt.archives.values() if n.state == 'active')
total = r + p + h

print(f"\n归约:{r}  剪枝:{p}  悬挂:{h}  总计:{total}")
print(f"归约率:{r/total:.1%}  剪枝率:{p/max(1,r+p):.1%}")

# ==================== 语义分组基准 ====================
# 预期分组
expect = {}
for ch in "水河火木天地日月星云风雨雷电山水土金石": expect[ch] = '自然'
for ch in "你我他爱恨生死人女男父母心身体家": expect[ch] = '生命'
for ch in "走跑飞说看听吃打开关上下出入": expect[ch] = '动作'
for ch in "一二三四五六七八九十百千万": expect[ch] = '数字'
for ch in "刀剑门车灯书本笔纸桌凳衣帽": expect[ch] = '物品'
for ch in "大小长短高多少好坏新旧美丑红白光明暗": expect[ch] = '抽象'

# K-means风格简单聚类：连续位距相似度
# 对每个归档节点，找它的 top-3 最近邻居，根据邻居标签投票
def hamming_dist(a, b):
    return (a.value ^ b.value).bit_count()

# 全局相似度矩阵 (只用A轴——笔画主导)
arch_nodes = [(ch, n) for ch, n in rt.archives.items() if n.state != 'pruned']
n_arch = len(arch_nodes)

# 构建邻居图
neighbors = {}
for i, (ch_a, na) in enumerate(arch_nodes):
    dists = []
    for j, (ch_b, nb) in enumerate(arch_nodes):
        if i == j:
            continue
        # 三轴位距和
        d = hamming_dist(na.gA, nb.gA) + hamming_dist(na.gB, nb.gB) + hamming_dist(na.gC, nb.gC)
        dists.append((d, ch_b))
    dists.sort()
    neighbors[ch_a] = [ch for d, ch in dists[:5]]

print(f"\n归档节点: {n_arch} (剪枝:{p}已排除)")
print("\n--- Top-5 邻居 ---")
for ch in train:
    if ch in neighbors:
        print(f"  {ch} → {neighbors[ch][:5]}")

# 简单标签传播: 种子=已知预期，传播3轮
print("\n--- 标签传播(3轮) ---")
labels = {}
# 种子
seeds_5 = ['水','人','走','一','刀','大']  # 每组一个明确种子
seed_map = {'水':'自然','人':'生命','走':'动作','一':'数字','刀':'物品','大':'抽象'}

for ch, label in seed_map.items():
    if ch in rt.archives:
        labels[ch] = label

for round in range(3):
    new_labels = dict(labels)
    for ch in neighbors:
        if ch in labels:
            continue
        # 对邻居标签投票
        votes = Counter()
        for nb in neighbors[ch][:3]:
            if nb in labels:
                votes[labels[nb]] += 1
        if votes:
            new_labels[ch] = votes.most_common(1)[0][0]
    labels = new_labels
    print(f"  第{round+1}轮: {len(labels)}字已标记")

# 准确率
correct = 0
total_checked = 0
for ch, label in labels.items():
    if ch in expect:
        total_checked += 1
        if label == expect[ch]:
            correct += 1
        else:
            print(f"  错: {ch} 预期{expect[ch]} → 系统{label}")

print(f"\n标签传播准确率: {correct}/{total_checked} = {correct/max(1,total_checked):.1%}")

# ==================== 语义对测试 ====================
print("\n--- 语义对位锁定 ---")
pairs = [
    ("水", "河", "近义"),
    ("火", "水", "反义"),
    ("爱", "恨", "反义"),
    ("生", "死", "反义"),
    ("天", "地", "反义"),
    ("一", "二", "数字近"),
    ("一", "十", "数字远"),
    ("大", "小", "反义"),
    ("美", "丑", "反义"),
    ("上", "下", "反义"),
    ("爱", "水", "无关"),
    ("人", "石", "无关"),
]

for a, b, label in pairs:
    if a not in rt.archives or b not in rt.archives:
        continue
    na, nb = rt.archives[a], rt.archives[b]
    ok_a = _fit_16(na.gA, nb.gA, 4) or _fit_16(nb.gA, na.gA, 4)
    ok_b = _fit_16(na.gB, nb.gB, 4) or _fit_16(nb.gB, na.gB, 4)
    ok_c = _fit_16(na.gC, nb.gC, 4) or _fit_16(nb.gC, na.gC, 4)
    ax = sum([ok_a, ok_b, ok_c])
    bar = '█' * ax + '░' * (3 - ax)
    print(f"  {a}↔{b} [{label}]  {bar}  {ax}/3  {'✅' if ax >= 2 else '⚠️'}")

print("\n完成。")
