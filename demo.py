# -*- coding: utf-8 -*-
"""Tongzi v4 · F₂ Collision Engine Demo

Zero dependencies. Pure Python. Zero floats, zero matrices, zero gradients.
pip install nothing && python demo.py

Pipeline:
  Chinese char → 4-suit pinball encode → Surge Pool (XOR/AND collision)
  → Eco Pool (birth/solidify) → Attractor emergence
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from v3.constants import CT_MASK
from v3.encode import encode
from v3.gua import Gua
from v3.express import express
from v3.surge_pool import SurgePool
from v3.eco_pool import EcoPool
from collections import Counter

print("=" * 60)
print("  Tongzi v4 · F₂ Collision Engine")
print("  Zero floats · Zero matrices · Zero gradients")
print("=" * 60)

# ═══════════════════════════════════════════════════════
# Step 1: Encoding — char → 28-bit F₂ vector
# ═══════════════════════════════════════════════════════

print("\n─── Step 1: Four-Suit Pinball Encoding ───")
print("Each char passes 4 pinball tracks (♥♦♣♠), producing 4×28bit vectors\n")

CHARS = "\u6c34\u706b\u7a7a\u6e7f\u5730\u52a8\u96f7\u9759\u98ce\u65e5\u6708\u5149\u5c71\u96e8\u4e91\u8349\u6728\u660e\u6e05\u6697"  # 20 chars

gua_list = []
for ch in CHARS:
    for suit in range(4):
        value = encode(ch, suit)
        g = Gua(value, source=ch)
        gua_list.append(g)

print(f"  Input: {len(CHARS)} chars × 4 suits = {len(gua_list)} gua")
print(f"  Sample: '{CHARS[0]}' ♥={gua_list[0].ct:07x}")

# ═══════════════════════════════════════════════════════
# Step 2: Surge Pool — F₂ collision engine
# ═══════════════════════════════════════════════════════

print("\n─── Step 2: Surge Pool · XOR/AND Collision ───")
print("Gua enter the pool. XOR+AND collision spawns children.\n")

surge = SurgePool()
surge.ingest(' '.join(CHARS))  # auto 4-suit encode → 80 gua

print(f"  Surge pool initial: {len(surge)} gua (80 native)")

pool = EcoPool("fast-birth", tau=3, fit_min=2, birth_rate=1.5,
               flow_back=True, density_max=256, stagnation_window=2, jitter_bits=5)

# ═══════════════════════════════════════════════════════
# Step 3: Run — 300 ticks of collision
# ═══════════════════════════════════════════════════════

print("\n─── Step 3: Run 300 Ticks ───")
print("Each tick: pull → XOR/AND collision → flowback\n")

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
    print(f"  tick {t:3d}: pool {sz:4d} gua, births {births:6d}, "
          f"solidified {solid:4d}, anti-entropy jitters {ae}")

# ═══════════════════════════════════════════════════════
# Step 4: Attractor Emergence
# ═══════════════════════════════════════════════════════

print("\n─── Step 4: Attractor Emergence ───")
print("XOR/AND collision → solidified children → express() back to nearest char\n")

natives = [g for g in surge.all() if g.is_native]
solid_kids = [g for g in pool.guas if pool._is_solid(g)]

names = Counter()
for g in solid_kids:
    name = express(g, natives)
    names[name] += 1

print(f"  Solidified children: {len(solid_kids)}")
print(f"  Unique attractors: {len(names)}")
print(f"\n  Top 10 Attractors:")
for name, count in names.most_common(10):
    bar = "\u2588" * (count // 10)
    print(f"    {name:4s} {count:5d} {bar}")

# ═══════════════════════════════════════════════════════
# Step 5: Collision Trace
# ═══════════════════════════════════════════════════════

print("\n─── Step 5: Collision Trace ───")
print("XOR/AND at the bit level\n")

natives_by_char = {}
for g in natives:
    if g.source not in natives_by_char:
        natives_by_char[g.source] = g

chars_list = list(natives_by_char.keys())
pairs = []
for i in range(len(chars_list) - 1):
    a = natives_by_char[chars_list[i]]
    b = natives_by_char[chars_list[i + 1]]
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
          f"Hamming={ham}  (collision window: 5-11)")

# ═══════════════════════════════════════════════════════
# Step 6: Input Sensitivity
# ═══════════════════════════════════════════════════════

print("\n─── Step 6: Input Sensitivity ───")
print("Different inputs → different attractor distributions\n")

from v4.v4 import LingxiV4

def test_input(text, label):
    from v3.eco_pool import EcoPool as EP
    v4 = LingxiV4()
    v4.add_pool(EP("fast", tau=3, fit_min=2, birth_rate=1.5, flow_back=True,
                    density_max=128, stagnation_window=2, jitter_bits=5))
    v4.add_pool(EP("surge", tau=5, fit_min=2, birth_rate=1.2, flow_back=True,
                    density_max=96, stagnation_window=2, jitter_bits=5))
    reply, r = v4.chat(text, ticks_per_round=100)
    print(f"  [{label}] '{text}'")
    print(f"         attractors: {', '.join(r.attractors[:4])}")
    print(f"         response: {reply}\n")

test_input("\u4f60\u597d",          "greeting")     # 你好
test_input("\u6253\u6b7b\u4f60",    "violent")      # 打死你
test_input("\u6211\u7231\u4f60",    "affection")    # 我爱你
test_input("\u5929\u6c14\u771f\u597d", "nature")    # 天气真好

# ═══════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════

print("=" * 60)
print("  Summary")
print("=" * 60)
print(f"  Input: {len(CHARS)} Chinese characters")
print(f"  Encoding: 4-suit pinball → {len(gua_list)} native gua (28-bit F₂)")
print(f"  Collision: XOR + AND + surge sliding window")
print(f"  Births: {pool.total_births}")
print(f"  Solidified (irreversible): {pool.total_solid}")
print(f"  Unique attractors: {len(names)}")
print(f"  Anti-entropy jitters: {pool.antientropy.total_jitters}")
print()
print("  Iron rules: zero floats · zero matrix multiplication · zero gradients")
print("              zero embeddings · zero attention · zero autoregression")
print("              zero external deps · pure Python · pure bit operations")
print()
print("  Code: src/v3/ (collision engine) + src/v4/ (self-model)")
print("  Entry: python demo.py")
print("=" * 60)
