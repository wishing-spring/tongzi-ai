# -*- coding: utf-8 -*-
"""Tongzi v4 · F₂ 底层演示

零依赖 · 纯 Python · 零浮点 · 零矩阵 · 零梯度
pip install nothing && python demo.py

核心链路:
  汉字 → 四芯弹珠编码 → 涌动池(XOR/AND碰撞) → 生态生子 → 吸引子涌现
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# ═══════════════════════════════════════════════════════
# 第 0 步：只导入标准库和 v3 核心
# ═══════════════════════════════════════════════════════

from v3.constants import CT_MASK
from v3.encode import encode
from v3.gua import Gua
from v3.express import express
from v3.surge_pool import SurgePool
from v3.eco_pool import EcoPool
from collections import Counter

print("=" * 60)
print("  Tongzi v4 · F₂ 底层演示")
print("  零浮点 · 零矩阵 · 零梯度 · 零外部依赖")
print("=" * 60)

# ═══════════════════════════════════════════════════════
# 第 1 步：编码 — 汉字 → 28bit F₂ 向量
# ═══════════════════════════════════════════════════════

print("\n─── 第 1 步：四芯编码 ───")
print("每个汉字过 4 条弹珠轨道 (♥♦♣♠)，得到 4 个 28bit F₂ 向量\n")

CHARS = "水火空湿地动雷静风日月光山雨云草木明清暗"  # 20字

gua_list = []
for ch in CHARS:
    for suit in range(4):
        value = encode(ch, suit)  # 含4bit花色+28bit内容
        g = Gua(value, source=ch)
        gua_list.append(g)

print(f"  输入: {len(CHARS)}字 × 4芯 = {len(gua_list)} 个卦元")
print(f"  示例: '{CHARS[0]}' ♥={gua_list[0].ct:07x}  ♦={gua_list[1].ct:07x}")
print(f"         '{CHARS[1]}' ♥={gua_list[4].ct:07x}  ♦={gua_list[5].ct:07x}")

# ═══════════════════════════════════════════════════════
# 第 2 步：涌动池 — F₂ 碰撞引擎
# ═══════════════════════════════════════════════════════

print("\n─── 第 2 步：涌动池 · F₂ 碰撞 ───")
print("卦元进池，XOR/AND 碰撞生子。窗口滑动实现 '涌動'。\n")

surge = SurgePool()
surge.ingest(' '.join(CHARS))  # 自动4芯编码→80卦

print(f"  涌池初始: {len(surge)} 卦 (80原生)")

# 加入生态池
pool = EcoPool("🔥快生", tau=3, fit_min=2, birth_rate=1.5, 
               flow_back=True, density_max=256, stagnation_window=2, jitter_bits=5)

# ═══════════════════════════════════════════════════════
# 第 3 步：运行 — 碰撞 × 300 tick
# ═══════════════════════════════════════════════════════

print("\n─── 第 3 步：运行 300 tick ───")
print("每 tick: pull → XOR/AND碰撞 → flowback\n")

snapshots = {}
for t in range(300):
    pool.pull(surge, t)
    pool.tick(t)
    for child in pool.births:
        surge.accept(child)
    pool.births.clear()
    
    if t in [0, 50, 100, 200, 299]:
        snapshots[t] = (len(surge), pool.total_births, pool.total_solid, 
                        pool.antientropy.total_jitters)

for t, (sz, births, solid, ae) in snapshots.items():
    print(f"  tick {t:3d}: 涌池 {sz:4d} 卦, 生子 {births:6d}, "
          f"固化 {solid:4d}, 反熵 {ae}")

# ═══════════════════════════════════════════════════════
# 第 4 步：吸引子涌现
# ═══════════════════════════════════════════════════════

print("\n─── 第 4 步：吸引子涌现 ───")
print("XOR/AND 碰撞 → 固化子代 → 表达(express)回到最近汉字\n")

natives = [g for g in surge.all() if g.is_native]
solid_kids = [g for g in pool.guas if pool._is_solid(g)]

# 吸引子分布
names = Counter()
for g in solid_kids:
    name = express(g, natives)
    names[name] += 1

print(f"  固化学代: {len(solid_kids)} 个")
print(f"  唯一吸引子: {len(names)} 种")
print(f"\n  吸引子 Top 10:")
for name, count in names.most_common(10):
    bar = "█" * (count // 10)
    print(f"    {name:4s} {count:5d} {bar}")

# ═══════════════════════════════════════════════════════
# 第 5 步：碰撞链追踪
# ═══════════════════════════════════════════════════════

print("\n─── 第 5 步：碰撞链追踪 ───")
print("从前 3 个字看 F₂ 碰撞如何产生新卦\n")

# 取每字一个代表(♥花色)
natives_by_char = {}
for g in natives:
    if g.source not in natives_by_char:
        natives_by_char[g.source] = g

chars_list = list(natives_by_char.keys())
pairs = []
for i in range(len(chars_list)-1):
    a = natives_by_char[chars_list[i]]
    b = natives_by_char[chars_list[i+1]]
    ham = (a.ct ^ b.ct).bit_count()
    if 4 < ham < 12:
        pairs.append((a, b, ham))
        if len(pairs) >= 3:
            break

for a, b, ham in pairs[:3]:
    a_ct, b_ct = a.ct, b.ct
    xor_val = a_ct ^ b_ct
    and_val = a_ct & b_ct
    print(f"  '{a.source}' vs '{b.source}':")
    print(f"    '{a.source}'={a_ct:07x}  '{b.source}'={b_ct:07x}")
    print(f"    XOR={xor_val:07x}  AND={and_val:07x}  "
          f"Hamming={ham} ✓ 可碰撞生子")

# ═══════════════════════════════════════════════════════
# 第 6 步：对话测试
# ═══════════════════════════════════════════════════════

print("\n─── 第 6 步：输入敏感性验证 ───")
print("不同输入 → 不同吸引子分布\n")

from v4.v4 import LingxiV4

def test_input(text, label):
    from v3.eco_pool import EcoPool as EP
    v4 = LingxiV4()
    v4.add_pool(EP("快生", tau=3, fit_min=2, birth_rate=1.5, flow_back=True,
                    density_max=128, stagnation_window=2, jitter_bits=5))
    v4.add_pool(EP("涌动", tau=5, fit_min=2, birth_rate=1.2, flow_back=True,
                    density_max=96, stagnation_window=2, jitter_bits=5))
    reply, r = v4.chat(text)
    print(f"  [{label}] '{text}'")
    print(f"         吸引子: {', '.join(r.attractors[:4])}")
    print(f"         回应: {reply}\n")

test_input("你好",           "社交")
test_input("打死你滚开",      "暴力")
test_input("我爱你",          "情感")
test_input("今天天气真好",    "自然")

# ═══════════════════════════════════════════════════════
# 总结
# ═══════════════════════════════════════════════════════

print("=" * 60)
print("  核心事实")
print("=" * 60)
print(f"  输入: 20个汉字")
print(f"  编码: 四芯弹珠 → 80个原生卦 (28bit F₂)")
print(f"  碰撞: XOR + AND + 涌動滑动窗口")
print(f"  生子: {pool.total_births} 个孩子")
print(f"  固化: {pool.total_solid} 个 (不可逆记忆)")
print(f"  吸引子: {len(names)} 个唯一表达")
print(f"  反熵: {pool.antientropy.total_jitters} 次微扰动")
print()
print("  铁律: 零浮点 · 零矩阵乘法 · 零梯度下降")
print("        零词嵌入 · 零注意力 · 零自回归")
print("        零外部依赖 · 纯 Python · 纯 F₂ 位运算")
print()
print("  代码: src/v3/ (11模块) + src/v4/ (9模块)")
print("  入口: python demo.py")
print("=" * 60)
