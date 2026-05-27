# -*- coding: utf-8 -*-
"""灵犀天元+脊骨 — 双漂移点 + 时间轨迹"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from ref8 import BAGUA, BAGUA_NAMES
from collections import deque


class TianYuan:
    """天元: 八卦盘上一个漂移的位点。8卦之一 + 偏移量 + 惯性方向。"""

    def __init__(self, start: str = '坤'):
        self.bagua = start           # 当前所在卦
        self.offset = 0.0            # 偏离当前卦中心的量 (-0.5 ~ +0.5)
        self.last_move = 0
        self.momentum_dir = 0        # 惯性方向: -1(逆时针) / 0(静止) / +1(顺时针)
        self.momentum_strength = 0.0 # 惯性强度 0~1

    def position_idx(self) -> float:
        """连续索引: 0.0(乾) ~ 7.999...(坤)"""
        base = BAGUA_NAMES.index(self.bagua)
        return base + self.offset

    def attract(self, target: str, rate: float = 0.05):
        """吸收目标卦，天元向目标漂移。同时累积惯性。"""
        cur = BAGUA_NAMES.index(self.bagua)
        tgt = BAGUA_NAMES.index(target)

        if cur == tgt:
            return

        d_forward = (tgt - cur) % 8
        d_backward = (cur - tgt) % 8

        if d_forward <= d_backward:
            step = +1 if d_forward <= 4 else -1
        else:
            step = -1 if d_backward <= 4 else +1

        # 偏移累加
        self.offset += step * rate * 8
        while self.offset >= 0.5:
            self.offset -= 1.0
            self.bagua = BAGUA_NAMES[(BAGUA_NAMES.index(self.bagua) + 1) % 8]
        while self.offset <= -0.5:
            self.offset += 1.0
            self.bagua = BAGUA_NAMES[(BAGUA_NAMES.index(self.bagua) - 1) % 8]

        # 惯性累积: 同方向加强，反方向减弱
        if step == self.momentum_dir:
            self.momentum_strength = min(1.0, self.momentum_strength + rate * 2)
        elif self.momentum_dir == 0:
            self.momentum_dir = step
            self.momentum_strength = rate
        else:
            self.momentum_strength = max(0.0, self.momentum_strength - rate * 3)

        if self.momentum_strength < 0.02:
            self.momentum_dir = 0
            self.momentum_strength = 0.0

    def drift_by_momentum(self):
        """惯性自主漂移: 沿累积方向自然移动。偶尔随机踢脚破僵局。"""
        if self.momentum_dir == 0 or self.momentum_strength < 0.05:
            # 静止过久 → 随机微踢
            import random
            if random.random() < 0.08:
                self.momentum_dir = random.choice([-1, +1])
                self.momentum_strength = 0.15
            return
        # 惯性漂移步长
        self.offset += self.momentum_dir * self.momentum_strength * 0.3
        while self.offset >= 0.5:
            self.offset -= 1.0
            self.bagua = BAGUA_NAMES[(BAGUA_NAMES.index(self.bagua) + 1) % 8]
        while self.offset <= -0.5:
            self.offset += 1.0
            self.bagua = BAGUA_NAMES[(BAGUA_NAMES.index(self.bagua) - 1) % 8]
        # 惯性衰减
        self.momentum_strength *= 0.93

    def meaning(self) -> str:
        return BAGUA[self.bagua]['meaning']

    def mood(self) -> str:
        return BAGUA[self.bagua]['mood']


class Spine:
    """脊骨: 天元轨迹FIFO。365天滚动。"""

    def __init__(self, maxlen: int = 365):
        self.points = deque(maxlen=maxlen)  # [(bagua, offset, tick), ...]
        self.maxlen = maxlen

    def record(self, ty: TianYuan, tick: int):
        self.points.append((ty.bagua, ty.offset, tick))

    def lookback(self, n: int = 5) -> list:
        """回溯最近N个点"""
        pts = list(self.points)
        return pts[-n:] if len(pts) >= n else pts

    def inertia(self) -> float:
        """最近移动的方向和幅度"""
        pts = list(self.points)
        if len(pts) < 2:
            return 0.0
        a = BAGUA_NAMES.index(pts[-2][0]) + pts[-2][1]
        b = BAGUA_NAMES.index(pts[-1][0]) + pts[-1][1]
        return b - a

    def dominant(self, n: int = 10) -> str:
        """最近N步最常待的卦"""
        pts = list(self.points)[-n:]
        if not pts:
            return '坤'
        from collections import Counter
        return Counter(p[0] for p in pts).most_common(1)[0][0]


if __name__ == '__main__':
    ty = TianYuan('坤')
    sp = Spine()

    targets = ['离', '坎', '离', '坤', '乾', '兑', '艮', '坤']
    for i, t in enumerate(targets):
        ty.attract(t, rate=0.05)
        sp.record(ty, i)
        print(f"t{i} 目标{t} → 天元={ty.bagua}({ty.meaning()}) 偏移={ty.offset:+.3f}")

    print(f"\n脊骨最近5: {sp.lookback(5)}")
    print(f"惯性: {sp.inertia():.3f}")
    print(f"主导卦: {sp.dominant()}")
