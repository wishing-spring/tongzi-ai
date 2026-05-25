"""快速测试: 反熵验证 · 跑够触发"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from v3.tongzi import TongziV3
from v3.eco_pool import EcoPool

tz = TongziV3()
tz.add(EcoPool("Test", tau=5, fit_min=3, birth_rate=1.0, flow_back=True, density_max=96))
tz.feed("水 火 天 地 山 雷 风 泽 日 月 星 光 暗 冷 热 干 湿 动 静 空")

print("跑 600 tick, 目标: 触发反熵\n")
last_b = 0
last_ae = 0
stag_count = 0

for _ in range(600):
    b_before = sum(e.total_births for e in tz.eco)
    tz.tick()
    t = tz.global_tick
    b_now = sum(e.total_births for e in tz.eco)
    ae = tz.eco[0].antientropy

    # 进度
    if t % 50 == 0:
        print(f"  t{t:03d} births={b_now:6d} surge={len(tz.surge):4d} "
              f"jitter={ae.total_jitters} stag={ae.stagnation_ticks}")

    # 反熵触发
    if ae.total_jitters > last_ae:
        print(f"  ⚡ t{t:03d} 反熵#{ae.total_jitters}!  "
              f"僵化{stag_count}tick后注入 births→{b_now}")
        last_ae = ae.total_jitters
        stag_count = 0

    if b_now == last_b:
        stag_count += 1
    else:
        stag_count = 0
        if b_now - last_b > 500 and t > 50:
            print(f"  ✓  t{t:03d} 新生! +{b_now-last_b} → {b_now}")
    last_b = b_now

print(f"\n最终: t={tz.global_tick} births={last_b} "
      f"反熵={tz.eco[0].antientropy.total_jitters}次 "
      f"surge={len(tz.surge)}")
