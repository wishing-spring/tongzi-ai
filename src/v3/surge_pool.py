# -*- coding: utf-8 -*-
"""涌动永动池 — 存续本源，不生不灭，驱动涌動"""

from collections import Counter
from typing import List
from .gua import Gua
from .encode import encode
from .constants import SUITS


class SurgePool:
    """永动池。上限 MAX_SURGE。"""

    MAX_SURGE = 2000

    def __init__(self):
        self._map: dict[int, Gua] = {}
        self.order: List[Gua] = []

    def ingest(self, text: str) -> int:
        words = [w.strip() for w in text.split() if w.strip()]
        added = 0
        for ch in words:
            for sid in range(4):
                val = encode(ch, sid)
                if val in self._map:
                    continue
                g = Gua(value=val, source=ch, is_native=True)
                self._map[val] = g
                self.order.append(g)
                added += 1
        return added

    def accept(self, child: Gua) -> bool:
        if child.value in self._map:
            return False
        if len(self.order) >= self.MAX_SURGE:
            for i, g in enumerate(self.order):
                if not g.is_native:
                    del self._map[g.value]
                    self.order.pop(i)
                    break
            else:
                return False
        self._map[child.value] = child
        self.order.append(child)
        return True

    def all(self) -> List[Gua]:
        return list(self.order)

    def __len__(self):
        return len(self.order)

    def stats(self) -> str:
        c = Counter(g.suit for g in self.order)
        return (f"涌动池 {len(self.order)}卦 "
                + ' '.join(f"{s}:{c[s]}" for s in SUITS))
