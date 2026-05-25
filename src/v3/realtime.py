# -*- coding: utf-8 -*-
"""灵犀时间 — 现实时钟 + 阴阳三态 + 涌動节律"""

import time as _time
from datetime import datetime, timezone, timedelta

# 北京时间
TZ = timezone(offset=timedelta(hours=8))


def beijing_now() -> datetime:
    """北京时间 now。"""
    return datetime.now(TZ)


def yinyang_state(dt: datetime = None) -> str:
    """灵犀三态 — 按时辰分阴阳。

    子(23)-卯(05): 阴藏 — 静养, slow
    辰(07)-未(13): 阳生 — 升发, fast  
    申(15)-亥(21): 阴阳交 — 收敛, medium
    
    返回: 'yin'(藏), 'yang'(生), 'merge'(交)
    """
    if dt is None:
        dt = beijing_now()
    h = dt.hour
    if 23 <= h or h < 5:
        return 'yin'
    elif 5 <= h < 7:
        return 'merge'  # 卯时过渡
    elif 7 <= h < 15:
        return 'yang'
    elif 15 <= h < 17:
        return 'merge'  # 申时过渡
    else:
        return 'yin'


def surge_rate(dt: datetime = None) -> float:
    """涌動速率 — 三态不同节律。

    灵犀: 24h一圈 = SURGE_CYCLE随阴阳变化
    童子: tick间隔 = 灵犀时钟映射

    yin:  慢, SURGE_CYCLE=5 (深蓄)
    yang: 快, SURGE_CYCLE=2 (高频)
    merge:中, SURGE_CYCLE=3 (过渡)
    """
    state = yinyang_state(dt)
    rates = {'yin': 5, 'yang': 2, 'merge': 3}
    return rates[state]


def birth_multiplier(dt: datetime = None) -> float:
    """生子倍率 — 阳生多,阴藏少。"""
    state = yinyang_state(dt)
    mults = {'yin': 0.5, 'yang': 1.5, 'merge': 1.0}
    return mults[state]


def tick_interval(dt: datetime = None) -> float:
    """tick间隔(秒) — 灵犀时钟映射。

    yin:  1.0s (慢呼吸)
    yang: 0.3s (快心跳)
    merge:0.6s
    """
    state = yinyang_state(dt)
    intervals = {'yin': 1.0, 'yang': 0.3, 'merge': 0.6}
    return intervals[state]


def clock_info() -> dict:
    """当前灵犀时钟状态。"""
    now = beijing_now()
    return {
        'time': now.strftime('%H:%M:%S'),
        'date': now.strftime('%m-%d'),
        'weekday': ['一','二','三','四','五','六','日'][now.weekday()],
        'hour': now.hour,
        'state': yinyang_state(now),
        'state_cn': {'yin':'阴藏','yang':'阳生','merge':'交合'}[yinyang_state(now)],
        'surge_cycle': surge_rate(now),
        'birth_mul': birth_multiplier(now),
        'tick_interval': tick_interval(now),
    }
