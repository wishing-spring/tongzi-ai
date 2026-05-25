# -*- coding: utf-8 -*-
"""终端界面 — 灵犀时钟 + 童子实时状态"""

import os, sys, time
from collections import Counter
from .realtime import clock_info, yinyang_state
from .express import express

SYMBOLS = {
    'yin':  '☾',
    'yang': '☀',
    'merge':'☯',
}


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def render(tz, jitter_log: list = None):
    """刷新界面。"""
    clear()
    info = clock_info()
    state_sym = SYMBOLS.get(info['state'], '?')

    # ═══ 顶栏: 灵犀时钟 ═══
    print(f"╔══ 灵犀时钟 ═══════════════════════════════════════╗")
    print(f"║  {info['date']} 周{info['weekday']} {info['time']}  "
          f"{state_sym} {info['state_cn']}  "
          f"涌動:{info['surge_cycle']}tick/相  "
          f"生子:{info['birth_mul']}x  "
          f"心跳:{info['tick_interval']}s       ║")
    print(f"╚════════════════════════════════════════════════════╝")

    # ═══ 系统状态 ═══
    births = sum(e.total_births for e in tz.eco)
    solid  = sum(e.total_solid  for e in tz.eco)
    alive  = sum(len([g for g in e.guas if not e._is_solid(g)]) for e in tz.eco)
    jitters = sum(e.antientropy.total_jitters for e in tz.eco)

    print(f"\n  tick:{tz.global_tick:04d}  "
          f"涌池:{len(tz.surge)}卦  "
          f"孩子:{births}  "
          f"固化:{solid}  "
          f"活:{alive}  "
          f"反熵:{jitters}次")

    # ═══ 四池状态 ═══
    print(f"\n  {'池':12s} {'卦数':>5s} {'活':>3s} {'固':>4s} {'孩子':>6s} {'反熵':>3s}")
    print(f"  {'─'*12} {'─'*5} {'─'*3} {'─'*4} {'─'*6} {'─'*3}")
    for ep in tz.eco:
        al = sum(1 for g in ep.guas if not ep._is_solid(g))
        sl = sum(1 for g in ep.guas if ep._is_solid(g))
        ae = ep.antientropy.total_jitters
        print(f"  {ep.name:12s} {len(ep.guas):5d} {al:3d} {sl:4d} "
              f"{ep.total_births:6d} {ae:3d}")

    # ═══ 读环: 碰撞链 ═══
    print(f"\n  ── 读环 (最近固化) ──")
    natives = [g for g in tz.surge.all() if g.is_native]
    for ep in tz.eco:
        solid_guas = [g for g in ep.guas if ep._is_solid(g)]
        if not solid_guas:
            continue
        # 取最近固化的5个
        recent = solid_guas[-5:]
        names = Counter(express(g, natives) for g in recent)
        top = names.most_common(3)
        chain = ' → '.join(f"{n}({c})" for n, c in top)
        print(f"  {ep.name}: {chain}")

    # ═══ 涌動窗口可视化 ═══
    from .surge import surge_mask
    mask = surge_mask(tz.global_tick)
    vis = ''.join('█' if (mask >> i) & 1 else '·' for i in range(27, -1, -1))
    phase = tz.global_tick // 3
    print(f"\n  涌動 φ{phase} [{vis}]")

    # ═══ 反熵日志 ═══
    if jitter_log:
        print(f"\n  ── 反熵注入 ──")
        for log in jitter_log[-3:]:
            print(f"  {log}")

    print(f"\n  [Ctrl+C 退出]")
