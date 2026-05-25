# -*- coding: utf-8 -*-
"""F₂ 脊骨记忆 — 天元轨迹 = 永久记忆 · 每条40B"""

from dataclasses import dataclass, field
from typing import List, Optional
import time as _time


@dataclass
class SpinePoint:
    """脊骨上的一个点 = 某个时刻的天元位置。

    不存文本。不存情绪。存天元在那个时刻的28bit位置。
    曲线上有坑=那段不容易。曲线上有峰=那段很好。
    """
    ts: int = 0      # Unix时间戳
    ct: int = 0      # 天元28bit位置
    suit: int = 0    # 花色(主/副天元标记)

    SIZE = 40  # bytes per point (approx in C)


@dataclass
class Spine:
    """脊骨 = 天元的完整轨迹。

    365点/年 × 40B = 14.6KB/年。
    滚动FIFO——满一年删最早的点。
    """
    points: List[SpinePoint] = field(default_factory=list)
    max_points: int = 365

    def record(self, ct: int, suit: int = 0, ts: int = None):
        """记录一个脊骨点"""
        if ts is None:
            ts = int(_time.time())
        
        if len(self.points) >= self.max_points:
            self.points.pop(0)  # FIFO: 删最早
        
        self.points.append(SpinePoint(ts=ts, ct=ct, suit=suit))

    def lookback(self, steps: int) -> Optional[SpinePoint]:
        """回溯N步前的天元位置"""
        if steps <= 0 or steps > len(self.points):
            return None
        return self.points[-steps]

    def recent_inertia(self, n: int = 5) -> int:
        """最近N个点的演化惯性——XOR累计差"""
        if len(self.points) < n + 1:
            return 0
        
        recent = self.points[-n-1:]
        # 惯性 = 相邻点之间的XOR差异累积
        inertia = 0
        for i in range(len(recent) - 1):
            diff = recent[i+1].ct ^ recent[i].ct
            # 累计: 新差异覆盖旧差异
            inertia ^= diff
        return inertia

    def range_hamming_spread(self, start_step: int, end_step: int) -> float:
        """一段范围内的Hamming离散度——衡量波动大小"""
        pts = self.points[-end_step:] if end_step <= len(self.points) else self.points
        pts = pts[-start_step:] if start_step > 0 else pts
        
        if len(pts) < 2:
            return 0.0
        
        total = 0
        count = 0
        for i in range(len(pts)):
            for j in range(i+1, len(pts)):
                total += (pts[i].ct ^ pts[j].ct).bit_count()
                count += 1
        
        return total / max(count, 1) / 28.0  # 归一化到[0,1]

    def dominant_quadrant(self, steps: int = 30) -> int:
        """最近N步天元最常在哪个象限(高4bit分类)"""
        pts = self.points[-steps:] if steps <= len(self.points) else self.points
        if not pts:
            return 0
        
        from collections import Counter
        # 高4bit作为"象限"分类
        quadrants = Counter(p.ct >> 24 for p in pts)
        return quadrants.most_common(1)[0][0]

    @property
    def count(self) -> int:
        return len(self.points)
