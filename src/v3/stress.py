# -*- coding: utf-8 -*-
"""童子 v3.0 · 暴力测试 · 全速·激进·20000tick"""

import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from v3.tongzi import TongziV3
from v3.eco_pool import EcoPool

# ═══ 超参：激进模式 ═══
import v3.eco_pool as ep
ep.F0 = 32           # 超低门槛

tz = TongziV3()

# ═══ 四池：全开回流 + 激进反熵 ═══
tz.add(EcoPool("🔥快生",  tau=3,   fit_min=2, birth_rate=1.5, flow_back=True,  density_max=128, stagnation_window=2, jitter_bits=5))
tz.add(EcoPool("⚡涌动",  tau=5,   fit_min=2, birth_rate=1.2, flow_back=True,  density_max=96,  stagnation_window=2, jitter_bits=5))
tz.add(EcoPool("💀慢生",  tau=8,   fit_min=3, birth_rate=0.8, flow_back=False, density_max=64,  stagnation_window=3, jitter_bits=4))
tz.add(EcoPool("🧊沉淀",  tau=999, fit_min=5, birth_rate=0.0, flow_back=False, density_max=16))

# ═══ 喂入：40字 ═══
print("喂入 40 字 × 4 花色 = 160 原生卦\n")
tz.feed("水 火 天 地 山 雷 风 泽 日 月 星 光 暗 冷 热 干 湿 动 静 空")
tz.feed("春 夏 秋 冬 东 西 南 北 金 木 土 石 云 雨 雪 霜 花 草 树 叶")

# ═══ 开跑 ═══
TOTAL = 5000
INTERVAL = 200

print(f"暴力模式: F0=32 JITTER=5bit/3tick 全速 {TOTAL}tick")
print(f"{'tick':>6s} {'孩子':>8s} {'固':>6s} {'活':>5s} {'涌池':>5s} {'反熵':>4s} {'tick/s':>7s}")
print(f"{'─'*6} {'─'*8} {'─'*6} {'─'*5} {'─'*5} {'─'*4} {'─'*7}")

t0 = time.time()
last_t = 0
last_b = 0

for _ in range(TOTAL):
    tz.tick()
    t = tz.global_tick

    if t % INTERVAL == 0:
        now = time.time()
        births = sum(e.total_births for e in tz.eco)
        solid  = sum(e.total_solid  for e in tz.eco)
        alive  = sum(len([g for g in e.guas if not e._is_solid(g)]) for e in tz.eco)
        jitters = sum(e.antientropy.total_jitters for e in tz.eco)
        tps = INTERVAL / (now - last_t) if last_t else 0
        
        delta = births - last_b
        print(f"{t:6d} {births:8d} {solid:6d} {alive:5d} "
              f"{len(tz.surge):5d} {jitters:4d} {tps:7.0f}")
        
        last_t = now
        last_b = births

elapsed = time.time() - t0
print(f"\n{'='*50}")
print(f"耗时 {elapsed:.1f}s · {TOTAL/elapsed:.0f} tick/s")

# ═══ 终报 ═══
print(tz.report())

# ═══ 读环 ═══
from v3.express import express
from collections import Counter
natives = [g for g in tz.surge.all() if g.is_native]

print(f"\n── 读环 · 热点碰撞链 ──")
for ep in tz.eco:
    sol = [g for g in ep.guas if ep._is_solid(g)]
    if sol:
        names = Counter(express(g, natives) for g in sol[-50:])
        chain = ' → '.join(f"{n}({c})" for n, c in names.most_common(4))
        print(f"  {ep.name}: {chain}")
