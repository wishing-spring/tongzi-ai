# -*- coding: utf-8 -*-
"""童子 v3.0 · 统一系统"""

from collections import Counter
from typing import List
from .surge_pool import SurgePool
from .eco_pool import EcoPool
from .express import express
from .constants import SUITS


class TongziV3:
    """涌动池 + 多生态池。"""

    def __init__(self):
        self.surge = SurgePool()
        self.eco: List[EcoPool] = []
        self.global_tick = 0

    def add(self, pool: EcoPool):
        self.eco.append(pool)

    def feed(self, text: str) -> int:
        return self.surge.ingest(text)

    def tick(self, n: int = 1):
        """驱动一轮。每个生态池: 拉卦→碰撞→生子回流涌动池。"""
        for _ in range(n):
            self.global_tick += 1
            for ep in self.eco:
                ep.pull(self.surge, self.global_tick)
                ep.tick(self.global_tick)
                # 生子回流
                for c in ep.births:
                    self.surge.accept(c)
                ep.births.clear()

    def report(self) -> str:
        L = [f"═══ 童子 v3.0 tick={self.global_tick} ═══",
             self.surge.stats()]
        for ep in self.eco:
            L.append(ep.stats())

        natives = self.surge.all()
        for ep in self.eco:
            sol = [g for g in ep.guas if ep._is_solid(g)]
            if sol:
                names = Counter(express(g, natives) for g in sol)
                L.append(f"\n{ep.name} 吸引子:")
                for name, cnt in names.most_common(5):
                    L.append(f"  {name:4s} {'█' * min(cnt, 40)} {cnt}")

        return '\n'.join(L)
