# -*- coding: utf-8 -*-
"""L1 Yin-Yang Layer — GuaYuan pair-pool perpetual oscillation · zero-float"""
import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
from guayuan import MASK28, hamming, xor_reduce, pool_average, nearest, random_gua


class YinYangPool:
    """GuaYuan pair-pool: Yin ⊕ Yang mutual exchange oscillation"""

    def __init__(self, capacity: int = 128, swap_rate: int = 4):
        self.capacity = capacity
        self.swap_rate = swap_rate
        self.yin: list[int] = []
        self.yang: list[int] = []
        self.tick = 0
        self._init_pools()

    def _init_pools(self):
        for i in range(self.capacity):
            self.yin.append(random_gua(i) & MASK28)
            self.yang.append(random_gua(i + 1000) & MASK28)

    def yin_sum(self) -> int:
        return xor_reduce(self.yin)

    def yang_sum(self) -> int:
        return xor_reduce(self.yang)

    def coherence(self) -> float:
        """Yin-Yang balance: 0=balanced, 1=extreme"""
        return hamming(self.yin_sum(), self.yang_sum()) / 28.0

    def tick_once(self) -> int:
        """One frame: pairwise collision → yin-yang exchange → capacity control"""
        self.tick += 1

        yin_out = self._collide(self.yin)
        yang_out = self._collide(self.yang)
        inject = (yin_out ^ yang_out) & MASK28

        self._swap()
        self._trim()
        return inject

    def _collide(self, pool: list[int]) -> int:
        if len(pool) < 2:
            return 0
        n = min(4, len(pool))
        idxs = random.sample(range(len(pool)), min(n * 2, len(pool)))
        result = 0
        for i in range(0, len(idxs) - 1, 2):
            result ^= (pool[idxs[i]] ^ pool[idxs[i+1]]) & MASK28
        return result

    def _swap(self):
        """Distant → Yang, near → Yin"""
        if len(self.yin) < 2 or len(self.yang) < 2:
            return

        yin_avg = pool_average(self.yin)
        yang_avg = pool_average(self.yang)
        swaps = min(self.swap_rate, len(self.yin), len(self.yang))

        for _ in range(swaps):
            yin_g = nearest(self.yin, yin_avg)
            yin_avg = pool_average(self.yin)
            if yin_g in self.yin:
                self.yin.remove(yin_g)
                self.yang.append(yin_g)

            if not self.yang:
                continue
            best_g, best_d = self.yang[0], hamming(self.yang[0], yang_avg)
            for g in self.yang[1:]:
                d = hamming(g, yang_avg)
                if d > best_d:
                    best_d, best_g = d, g
            if best_g in self.yang:
                self.yang.remove(best_g)
                self.yin.append(best_g)

    def _trim(self):
        for pool in [self.yin, self.yang]:
            if len(pool) <= self.capacity:
                continue
            avg = pool_average(pool)
            ranked = sorted(pool, key=lambda g: hamming(g, avg))
            mid = len(ranked) // 2
            discard = ranked[mid - self.swap_rate:mid + self.swap_rate]
            for g in discard:
                pool.remove(g)

    def bias(self) -> str:
        c = self.coherence()
        if c < 0.2:
            return 'balanced'
        elif hamming(self.yin_sum(), 0) > hamming(self.yang_sum(), 0):
            return 'yin-dominant'
        else:
            return 'yang-dominant'


if __name__ == '__main__':
    yy = YinYangPool(64, swap_rate=2)
    print(f"YinYang: yin{len(yy.yin)} yang{len(yy.yang)} coherence={yy.coherence():.3f} bias={yy.bias()}")
    for _ in range(5):
        g = yy.tick_once()
        print(f"  tick{yy.tick}: inject=0x{g:07X} coherence={yy.coherence():.3f} {yy.bias()}")
