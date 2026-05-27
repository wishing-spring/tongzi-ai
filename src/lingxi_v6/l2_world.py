# -*- coding: utf-8 -*-
"""L2 世界层 — 字团卦元池 · 三态 · 做梦 · 零浮点"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from guayuan import MASK28, hamming, xor_reduce, pool_average, nearest, random_gua, gua_hash


class WorldPool:
    """字团卦元池: 天·地·山·石·水·脉... = 卦元"""

    # 字团种子词库
    SEED_WORDS = "天地山水火风雷泽日月星云雨雪雾冰河海湖泉溪浪潮沙石泥尘灰烟光影暗明深".split()

    def __init__(self, capacity: int = 1024, active_threshold: int = 12,
                 flowing_threshold: int = 20):
        self.capacity = capacity
        self.active_th = active_threshold    # ≤12 = 激活
        self.flowing_th = flowing_threshold  # ≤20 = 流动
        self.pool: list[int] = []            # 卦元池
        self.idle_ticks = 0
        self.tick = 0
        self._init_pool()

    def _init_pool(self):
        """出厂: 字团种子卦元"""
        for w in self.SEED_WORDS:
            g = gua_hash(w)
            if g not in self.pool:
                self.pool.append(g)
        # 填充到capacity
        while len(self.pool) < self.capacity:
            g = random_gua(len(self.pool))
            if g not in self.pool:
                self.pool.append(g)

    # ── 状态查询 ──
    def pool_avg(self) -> int:
        return pool_average(self.pool)

    def active_count(self) -> int:
        avg = self.pool_avg()
        return sum(1 for g in self.pool if hamming(g, avg) <= self.active_th)

    def flowing_count(self) -> int:
        avg = self.pool_avg()
        return sum(1 for g in self.pool
                   if self.active_th < hamming(g, avg) <= self.flowing_th)

    def dormant_count(self) -> int:
        return len(self.pool) - self.active_count() - self.flowing_count()

    def state_str(self, g: int, avg: int = None) -> str:
        if avg is None:
            avg = self.pool_avg()
        d = hamming(g, avg)
        if d <= self.active_th:
            return '激活'
        elif d <= self.flowing_th:
            return '流动'
        return '休眠'

    # ── 核心tick ──
    def tick_once(self, yin_inject: int = 0, has_input: bool = True) -> dict:
        """一帧: 接收阴阳注入 → 扩散 → 三态更新 → 做梦"""
        self.tick += 1

        # 接收L1注入
        if yin_inject:
            self._inject(yin_inject)

        # 池内扩散: 邻近卦元对做pairwise XOR
        self._diffuse()

        # 做梦检测
        if not has_input:
            self.idle_ticks += 1
        else:
            self.idle_ticks = 0

        if self.idle_ticks > 60:
            self._dream()

        # 低密度注入噪声
        if len(self.pool) < self.capacity * 0.5:
            self._noise_inject()

        return {
            'total': len(self.pool),
            'active': self.active_count(),
            'flowing': self.flowing_count(),
            'dormant': self.dormant_count(),
            'idle': self.idle_ticks,
            'dreaming': self.idle_ticks > 60,
        }

    def _inject(self, gua: int):
        """接收卦元，不重复"""
        if gua not in self.pool:
            self.pool.append(gua)
        self._trim()

    def _diffuse(self):
        """池内扩散: 随机选邻近卦元对 XOR"""
        import random
        avg = self.pool_avg()

        # 激活阈值在梦境时放宽
        threshold = self.active_th + (8 if self.idle_ticks > 60 else 0)

        for _ in range(min(len(self.pool) // 4, 32)):
            if len(self.pool) < 2:
                break
            # 随机选两个邻近卦元
            a = random.choice(self.pool)
            b = nearest(self.pool, a, exclude={a})
            if hamming(a, b) <= threshold:
                child = (a ^ b) & MASK28
                if child not in self.pool:
                    self.pool.append(child)

        self._trim()

    def _dream(self):
        """做梦: 低频扩散 + Hebbian候选"""
        # D降低 → 更多卦元进入激活态 (由_diffuse的threshold放宽实现)
        # Hebbian候选: 共同激活卦元对 → 记录
        avg = self.pool_avg()
        self._active_pairs = []
        for i in range(min(len(self.pool), 64)):
            for j in range(i + 1, min(len(self.pool), 64)):
                a, b = self.pool[i], self.pool[j]
                if hamming(a, avg) <= self.active_th and hamming(b, avg) <= self.active_th:
                    self._active_pairs.append((a, b))

    def _noise_inject(self):
        """低密度噪声注入"""
        for _ in range(4):
            g = random_gua(self.tick * 100 + _)
            if g not in self.pool:
                self.pool.append(g)

    def _trim(self):
        """容量控制"""
        if len(self.pool) <= self.capacity:
            return
        # 淘汰休眠卦元
        avg = self.pool_avg()
        dormant = [g for g in self.pool if hamming(g, avg) > self.flowing_th]
        remove = min(len(dormant), len(self.pool) - self.capacity)
        for g in dormant[:remove]:
            self.pool.remove(g)

    def get_active_guas(self) -> list[int]:
        """返回激活卦元列表 (送Φ场)"""
        avg = self.pool_avg()
        return [g for g in self.pool if hamming(g, avg) <= self.active_th]


if __name__ == '__main__':
    world = WorldPool(128, active_threshold=10, flowing_threshold=18)
    print(f"世界: {world.active_count()}激活 {world.flowing_count()}流动 {world.dormant_count()}休眠")

    inject = 0x1234567
    for i in range(5):
        st = world.tick_once(yin_inject=inject if i < 2 else 0, has_input=(i < 2))
        print(f"  tick{i+1}: {st['active']}激活 {st['flowing']}流动 "
              f"{st['dormant']}休眠 idle={st['idle']}")
        inject ^= (inject << 7) & MASK28
