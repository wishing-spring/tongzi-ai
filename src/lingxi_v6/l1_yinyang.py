# -*- coding: utf-8 -*-
"""L1 阴阳层 — 卦元对池永动振荡 · 零浮点"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from guayuan import MASK28, hamming, xor_reduce, pool_average, nearest, random_gua


class YinYangPool:
    """卦元对池: 阴池⊕阳池互易振荡"""

    def __init__(self, capacity: int = 128, swap_rate: int = 4):
        self.capacity = capacity
        self.swap_rate = swap_rate  # 每tick互易对数
        self.yin: list[int] = []    # 阴池
        self.yang: list[int] = []   # 阳池
        self.tick = 0
        self._init_pools()

    def _init_pools(self):
        """出厂烧制: 种子卦元填充"""
        for i in range(self.capacity):
            seed = random_gua(i)
            self.yin.append(seed & MASK28)
            seed2 = random_gua(i + 1000)
            self.yang.append(seed2 & MASK28)

    # ── 状态查询 ──
    def yin_sum(self) -> int:
        return xor_reduce(self.yin)

    def yang_sum(self) -> int:
        return xor_reduce(self.yang)

    def coherence(self) -> float:
        """阴阳平衡度 0(平衡)~1(失衡)"""
        return hamming(self.yin_sum(), self.yang_sum()) / 28.0

    # ── 核心tick ──
    def tick_once(self) -> int:
        """
        一帧:
          1. 池内碰撞 → 产出卦元
          2. 阴阳互易
          3. 容量控制
        返回: 注入L2的卦元
        """
        self.tick += 1

        # 1. 池内碰撞: pairwise XOR采样
        yin_out = self._collide(self.yin)
        yang_out = self._collide(self.yang)
        inject = (yin_out ^ yang_out) & MASK28

        # 2. 阴阳互易: 远Hamming→阳, 近Hamming→阴
        self._swap()

        # 3. 容量控制
        self._trim()

        return inject

    def _collide(self, pool: list[int]) -> int:
        """池内碰撞: 随机选4对 XOR"""
        if len(pool) < 2:
            return 0
        import random
        n = min(4, len(pool))
        idxs = random.sample(range(len(pool)), min(n * 2, len(pool)))
        result = 0
        for i in range(0, len(idxs) - 1, 2):
            result ^= (pool[idxs[i]] ^ pool[idxs[i+1]]) & MASK28
        return result

    def _swap(self):
        """阴阳互易: 远→阳近→阴"""
        if len(self.yin) < 2 or len(self.yang) < 2:
            return

        yin_avg = pool_average(self.yin)
        yang_avg = pool_average(self.yang)

        swaps = min(self.swap_rate, len(self.yin), len(self.yang))
        for _ in range(swaps):
            # 阴→阳: 距阴平均最近 → 注入阳
            yin_g = nearest(self.yin, yin_avg)
            yin_avg = pool_average(self.yin)  # 重新计算
            yang_avg = pool_average(self.yang)
            if yin_g in self.yin:
                self.yin.remove(yin_g)
                self.yang.append(yin_g)

            # 阳→阴: 距阳平均最远 → 注入阴
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
        """容量控制: 淘汰中位Hamming卦元"""
        for pool in [self.yin, self.yang]:
            if len(pool) <= self.capacity:
                continue
            avg = pool_average(pool)
            # 按Hamming距离排序
            ranked = sorted(pool, key=lambda g: hamming(g, avg))
            # 去掉中位
            mid = len(ranked) // 2
            discard = ranked[mid - self.swap_rate:mid + self.swap_rate]
            for g in discard:
                pool.remove(g)

    def bias(self) -> str:
        """阴阳偏向"""
        c = self.coherence()
        if c < 0.2:
            return '平衡'
        elif hamming(self.yin_sum(), 0) > hamming(self.yang_sum(), 0):
            return '阴盛'
        else:
            return '阳盛'


if __name__ == '__main__':
    yy = YinYangPool(64, swap_rate=2)
    print(f"阴阳: 阴{len(yy.yin)} 阳{len(yy.yang)} coherence={yy.coherence():.3f} bias={yy.bias()}")
    for _ in range(5):
        g = yy.tick_once()
        print(f"  tick{yy.tick}: inject=0x{g:07X} coherence={yy.coherence():.3f} {yy.bias()}")
