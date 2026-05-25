# -*- coding: utf-8 -*-
"""F₂ spine memory: tianyuan trajectory = permanent memory. ~40B per point."""

from dataclasses import dataclass, field
from typing import List, Optional
import time as _time


@dataclass
class SpinePoint:
    ts: int = 0
    ct: int = 0
    suit: int = 0


@dataclass
class Spine:
    points: List[SpinePoint] = field(default_factory=list)
    max_points: int = 365

    def record(self, ct: int, suit: int = 0, ts: int = None):
        if ts is None:
            ts = int(_time.time())
        if len(self.points) >= self.max_points:
            self.points.pop(0)
        self.points.append(SpinePoint(ts=ts, ct=ct, suit=suit))

    def lookback(self, steps: int) -> Optional[SpinePoint]:
        if steps <= 0 or steps > len(self.points):
            return None
        return self.points[-steps]

    def recent_inertia(self, n: int = 5) -> int:
        if len(self.points) < n + 1:
            return 0
        recent = self.points[-n - 1:]
        inertia = 0
        for i in range(len(recent) - 1):
            inertia ^= recent[i + 1].ct ^ recent[i].ct
        return inertia

    def range_hamming_spread(self, start_step: int, end_step: int) -> float:
        pts = self.points[-end_step:] if end_step <= len(self.points) else self.points
        pts = pts[-start_step:] if start_step > 0 else pts
        if len(pts) < 2:
            return 0.0
        total = 0
        count = 0
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                total += (pts[i].ct ^ pts[j].ct).bit_count()
                count += 1
        return total / max(count, 1) / 28.0

    def dominant_quadrant(self, steps: int = 30) -> int:
        pts = self.points[-steps:] if steps <= len(self.points) else self.points
        if not pts:
            return 0
        from collections import Counter
        quadrants = Counter(p.ct >> 24 for p in pts)
        return quadrants.most_common(1)[0][0]

    @property
    def count(self) -> int:
        return len(self.points)
