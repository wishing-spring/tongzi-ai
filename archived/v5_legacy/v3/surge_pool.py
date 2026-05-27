# -*- coding: utf-8 -*-
"""Surge Pool — Eternal pool. Stores all gua, drives surge-based matching.

The surge pool is the source of all gua. Native gua (direct encodings)
never leave. Collision-born children flow in from eco pools via accept().
When full (MAX_SURGE), oldest non-native gua are evicted to make room.
"""

from collections import Counter
from typing import List
from .gua import Gua
from .encode import encode
from .constants import SUITS


class SurgePool:
    """Eternal gua pool. Upper bound: MAX_SURGE."""

    MAX_SURGE = 2000

    def __init__(self):
        self._map: dict[int, Gua] = {}
        self.order: List[Gua] = []

    def ingest(self, text: str) -> int:
        """Encode each space-separated word into 4-suit gua and add to pool.

        Returns number of new gua added (duplicates skipped).
        """
        added = 0
        for ch in text:
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
        """Accept a collision-born child into the pool.

        If at capacity, evicts the oldest non-native gua.
        Returns True if accepted, False if rejected.
        """
        if child.value in self._map:
            return False
        if len(self.order) >= self.MAX_SURGE:
            for i, g in enumerate(self.order):
                if not g.is_native:
                    if g.value in self._map:
                        del self._map[g.value]
                    self.order.pop(i)
                    break
            else:
                return False  # all native, no room
        self._map[child.value] = child
        self.order.append(child)
        return True

    def all(self) -> List[Gua]:
        return list(self.order)

    def _ingest_raw(self, g: Gua):
        """持久化恢复: 直接插入卦"""
        if g.value in self._map:
            return  # 跳过重复
        self._map[g.value] = g
        self.order.append(g)

    def __len__(self):
        return len(self.order)

    def stats(self) -> str:
        c = Counter(g.suit for g in self.order)
        return (f"SurgePool {len(self.order)} gua "
                + ' '.join(f"{s}:{c[s]}" for s in SUITS))
