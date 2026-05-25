# -*- coding: utf-8 -*-
"""童子 v3.0 · 完整实验 · 四池 + 涌動"""

import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from v3.tongzi import TongziV3
from v3.eco_pool import EcoPool

tz = TongziV3()

# ═══ 池子配置 ═══
# 降低门槛让涌動子卦更容易碰撞
tz.add(EcoPool("快生·回流",   tau=5,   fit_min=3, birth_rate=1.0, flow_back=True,  density_max=96))
tz.add(EcoPool("慢生·不回流", tau=12,  fit_min=4, birth_rate=0.5, flow_back=False, density_max=48))
tz.add(EcoPool("沉淀·不生",   tau=999, fit_min=6, birth_rate=0.0, flow_back=False, density_max=16))
tz.add(EcoPool("涌动·快生",   tau=6,   fit_min=3, birth_rate=1.0, flow_back=True,  density_max=64))

# ═══ 喂入 ═══
print("喂入 20 字 × 4 花色 = 80 卦\n")
tz.feed("水 火 天 地 山 雷 风 泽 日 月")
tz.feed("星 光 暗 冷 热 干 湿 动 静 空")

# ═══ 运行 ═══
total_ticks = 200
interval = 10

print(f"运行 {total_ticks} tick")
print(f"  pool规则 (fit_min): 快生=3 慢生=4 涌动=3 沉淀=6")
t0 = time.time()

for _ in range(total_ticks):
    tz.tick()
    t = tz.global_tick
    if t % interval == 0 or t <= 15:
        births = sum(e.total_births for e in tz.eco)
        solid  = sum(e.total_solid  for e in tz.eco)
        alive  = sum(len([g for g in e.guas if not e._is_solid(g)]) for e in tz.eco)
        activity = ''
        if t <= 10:
            for e in tz.eco:
                ac = len([g for g in e.guas if not e._is_solid(g) and e._energy_of(g) >= 96])
                if ac > 0:
                    activity += f' {e.name}:{ac}ac'
        print(f"  t{t:03d} alive={alive:4d} solid={solid:4d} "
              f"births={births:6d} surge={len(tz.surge):4d}{activity}", flush=True)

elapsed = time.time() - t0

# ═══ 报告 ═══
print(f"\n耗时 {elapsed:.1f}s · {total_ticks/elapsed:.0f} tick/s\n")
print(tz.report())

# ═══ 涌動窗口演示 ═══
from v3.surge import surge_mask, SURGE_CYCLE
print("\n── 涌動滑动窗口 (灵犀八卦盘等效) ──")
for phase in range(10):
    tick = phase * SURGE_CYCLE
    mask = surge_mask(tick)
    # 可视化: 28位中 1=窗口内 0=窗外
    vis = ''.join('█' if (mask >> i) & 1 else '·' for i in range(27, -1, -1))
    print(f"  φ{phase}(t{tick:02d}) [{vis}]")
