# -*- coding: utf-8 -*-
"""
童子 · 基准任务 #1: 语义分组 v3
=================================
用连续位匹配计数 (非二元门槛) 做相似度
"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from ren_tongzi import RenTongzi
from collections import Counter
import math

rt = RenTongzi(tau=5)
train = "水河火木天地日月山河金刀剑一二三四五六七八九十爱恨生死你我他万千万"
rt.learn(train)

# 去重
all_chars = []
seen = set()
for c in train:
    if c not in seen:
        seen.add(c)
        all_chars.append(c)

# === 人类预期 ===
expected = {
    '水':0,'河':0,'火':0,'木':0,'天':0,'地':0,'日':0,'月':0,'山':0,'金':0,'刀':0,'剑':0,
    '一':1,'二':1,'三':1,'四':1,'五':1,'六':1,'七':1,'八':1,'九':1,'十':1,
    '爱':2,'恨':2,'生':2,'死':2,'你':2,'我':2,'他':2,
    '万':3,'千':3,
}
group_names = {0:'自然', 1:'数字', 2:'生命', 3:'其它'}

# === 连续相似度 ===
def tri_sim_cont(a, b):
    """三轴连续位匹配计数 / 48。"""
    if a not in rt.archives or b not in rt.archives:
        return 0
    na, nb = rt.archives[a], rt.archives[b]
    # 每轴: a凸b凹 匹配位数
    m_a = ((na.gA.value ^ nb.gA.value) & 0xFFFF).bit_count()
    m_b = ((na.gB.value ^ nb.gB.value) & 0xFFFF).bit_count()
    m_c = ((na.gC.value ^ nb.gC.value) & 0xFFFF).bit_count()
    # 距离 → 相似度 (16-汉明距离)/16
    sim_a = (16 - m_a) / 16
    sim_b = (16 - m_b) / 16
    sim_c = (16 - m_c) / 16
    return (sim_a + sim_b + sim_c) / 3

# === K-means K=4 ===
def kmeans_fit(chars, K=4, iters=15):
    # 最远初始化
    centers = [chars[0]]
    for _ in range(K-1):
        best, best_d = None, -1
        for c in chars:
            if c in centers: continue
            d = min(1-tri_sim_cont(c, cc) for cc in centers)
            if d > best_d:
                best_d, best = d, c
        centers.append(best)

    labels = {}
    for _ in range(iters):
        for c in chars:
            sims = [tri_sim_cont(c, cc) for cc in centers]
            labels[c] = sims.index(max(sims))

        for kidx in range(K):
            members = [c for c in chars if labels.get(c) == kidx]
            if not members: continue
            best_c, best_avg = members[0], -1
            for c in members:
                avg = sum(tri_sim_cont(c, m) for m in members if m != c) / max(len(members)-1, 1)
                if avg > best_avg:
                    best_avg, best_c = avg, c
            centers[kidx] = best_c
    return labels, centers

labels, centers = kmeans_fit(all_chars, K=4)

groups = {}
for c, g in labels.items():
    groups.setdefault(g, []).append(c)

print("=" * 60)
print("童子 v1.8-ren · 基准任务 #1 · 语义分组 (连续相似度 K=4)")
print("=" * 60)
for gid, members in sorted(groups.items(), key=lambda x: -len(x[1])):
    print(f"  G{gid} ({len(members)}字): {members}")

# 投票映射
sys_to_human = {}
for gid, members in groups.items():
    votes = Counter()
    for c in members:
        if c in expected: votes[expected[c]] += 1
    best = votes.most_common(1)
    if best: sys_to_human[gid] = best[0][0]

# 评估
correct, total = 0, 0
print(f"\n{'字':<4} {'系统':<10} {'预期':<8} {'对/错'}")
for c in all_chars:
    if c not in expected or c not in labels: continue
    g = labels[c]
    m = sys_to_human.get(g, -1)
    ok = (m == expected[c])
    if ok: correct += 1
    total += 1
    print(f"  {c:<4} G{g}({group_names.get(m,'?'):<6}) {group_names[expected[c]]:<8} {'OK' if ok else 'XX'}")

acc = correct/total
print(f"\n准确率: {correct}/{total} = {acc:.1%}")

# NMI
def entropy(counts):
    t = sum(counts)
    return -sum((c/t)*math.log2(c/t) for c in counts if c>0)

sys_sizes = [len(m) for m in groups.values()]
hum_sizes = [sum(1 for c in all_chars if c in expected and expected[c]==g) for g in range(4)]

joint = {}
for gid, members in groups.items():
    for c in members:
        if c in expected:
            joint[(gid, expected[c])] = joint.get((gid, expected[c]), 0) + 1

h_sys = entropy(sys_sizes)
h_hum = entropy(hum_sizes)
n = sum(1 for c in all_chars if c in expected)
mi = sum(
    (cnt/n) * math.log2((cnt/n) / ((len(groups[gid])/n)*(hum_sizes[hgid]/n)))
    for (gid, hgid), cnt in joint.items() if cnt>0
)
nmi_score = 2*mi/(h_sys+h_hum) if h_sys>0 and h_hum>0 else 0

print(f"NMI: {nmi_score:.4f}")

# 混淆矩阵
print(f"\n--- 混淆矩阵 ---")
for gid in sorted(groups):
    counts = Counter()
    for c in groups[gid]:
        if c in expected: counts[expected[c]] += 1
    parts = [f"{group_names.get(k,'?')}:{v}" for k,v in counts.most_common()]
    print(f"  G{gid}: {', '.join(parts)}")

# === 随机基线 ===
import random
rands = [random.random() for _ in range(20)]
rand_accs = []
for _ in range(100):
    random.shuffle(all_chars)
    rlabels = {c: i%4 for i,c in enumerate(all_chars)}
    rc = sum(1 for c in all_chars if c in expected and rlabels[c]==expected[c])
    rand_accs.append(rc/total)
rand_mean = sum(rand_accs)/len(rand_accs)
print(f"\n随机基线 (100次): {rand_mean:.1%}  ({acc:.1%} vs {rand_mean:.1%} = {acc/rand_mean:.1f}x)")

# === 理想情况 (4组平均分配) ===
ideal_acc = 1/4
print(f"均匀随机基线: {ideal_acc:.1%}  ({acc:.1%} vs {ideal_acc:.1%} = {acc/ideal_acc:.1f}x)")
