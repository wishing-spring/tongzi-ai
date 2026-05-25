# -*- coding: utf-8 -*-
"""童子 v3.0 · 真实时间测试 · 灵犀时钟 + 反熵 + 界面"""

import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from v3.tongzi import TongziV3
from v3.eco_pool import EcoPool
from v3.realtime import clock_info, yinyang_state, tick_interval, birth_multiplier
from v3.ui import render, clear

# ═══ 系统初始化 ═══
tz = TongziV3()

tz.add(EcoPool("快生·回流",   tau=5,   fit_min=3, birth_rate=1.0, flow_back=True,  density_max=96))
tz.add(EcoPool("慢生·不回流", tau=12,  fit_min=4, birth_rate=0.5, flow_back=False, density_max=48))
tz.add(EcoPool("沉淀·不生",   tau=999, fit_min=6, birth_rate=0.0, flow_back=False, density_max=16))
tz.add(EcoPool("涌动·快生",   tau=6,   fit_min=3, birth_rate=1.0, flow_back=True,  density_max=64))

# ═══ 真实输入: 20字 + 扩展语境 ═══
print("喂入...")
tz.feed("水 火 天 地 山 雷 风 泽 日 月")
tz.feed("星 光 暗 冷 热 干 湿 动 静 空")
tz.feed("春 夏 秋 冬 东 西 南 北 金 木 土 石 云 雨 雪 霜 花 草 树 木")

print(f"原生: {len(tz.surge)}卦\n")

jitter_log = []
last_render = 0

try:
    while True:
        # ── 灵犀时钟驱动 ──
        info = clock_info()
        interval = info['tick_interval']

        # 根据阴阳调整生子倍率
        bm = birth_multiplier()
        for ep in tz.eco:
            if ep.birth_rate > 0:
                ep.birth_rate = bm

        # ── 运行N个tick ──
        ticks_per_render = 3
        for _ in range(ticks_per_render):
            births_before = sum(e.total_births for e in tz.eco)
            tz.tick()

            # 检测反熵注入
            for ep in tz.eco:
                if ep.antientropy.stagnation_ticks == 5:
                    jitter_log.append(
                        f"t{tz.global_tick:04d} [{ep.name}] 僵化→φ注入5卦 "
                        f"({ep.antientropy.total_jitters}次累计)"
                    )

        # ── 刷新界面 ──
        now = time.time()
        if now - last_render >= interval * ticks_per_render or not last_render:
            render(tz, jitter_log)
            last_render = now

        time.sleep(interval)

except KeyboardInterrupt:
    clear()
    print("\n═══ 童子 v3.0 · 测试结束 ═══\n")
    print(tz.report())
    if jitter_log:
        print(f"\n── 反熵日志 ({len(jitter_log)}条) ──")
        for log in jitter_log:
            print(f"  {log}")
