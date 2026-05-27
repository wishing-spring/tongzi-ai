# -*- coding: utf-8 -*-
"""L2 World Layer — Word-cluster GuaYuan pool · three-state · dreaming · zero-float"""
import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
from guayuan import MASK28, hamming, xor_reduce, pool_average, nearest, random_gua, gua_hash

SEED_WORDS = "天地山水火风雷泽日月星云雨雪雾冰河海湖泉溪浪潮沙石泥尘灰烟光影暗明深".split()


class WorldPool:
    """Word-cluster GuaYuan pool: activated/flowing/dormant three-state"""

    def __init__(self, capacity: int = 1024, active_threshold: int = 12,
                 flowing_threshold: int = 20):
        self.capacity = capacity
        self.active_th = active_threshold
        self.flowing_th = flowing_threshold
        self.pool: list[int] = []
        self.idle_ticks = 0
        self.tick = 0
        self._active_pairs: list[tuple] = []
        self._init_pool()

    def _init_pool(self):
        for w in SEED_WORDS:
            g = gua_hash(w)
            if g not in self.pool:
                self.pool.append(g)
        while len(self.pool) < self.capacity:
            g = random_gua(len(self.pool))
            if g not in self.pool:
                self.pool.append(g)

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

    def tick_once(self, yin_inject: int = 0, has_input: bool = True) -> dict:
        """One frame: receive yin injection → diffuse → update states → dream"""
        self.tick += 1
        if yin_inject:
            self._inject(yin_inject)
        self._diffuse()

        if not has_input:
            self.idle_ticks += 1
        else:
            self.idle_ticks = 0

        if self.idle_ticks > 60:
            self._dream()

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
        if gua not in self.pool:
            self.pool.append(gua)
        self._trim()

    def _diffuse(self):
        avg = self.pool_avg()
        threshold = self.active_th + (8 if self.idle_ticks > 60 else 0)

        for _ in range(min(len(self.pool) // 4, 32)):
            if len(self.pool) < 2:
                break
            a = random.choice(self.pool)
            b = nearest(self.pool, a, exclude={a})
            if hamming(a, b) <= threshold:
                child = (a ^ b) & MASK28
                if child not in self.pool:
                    self.pool.append(child)
        self._trim()

    def _dream(self):
        """Dreaming: lower D threshold + record Hebbian candidate pairs"""
        avg = self.pool_avg()
        self._active_pairs = []
        for i in range(min(len(self.pool), 64)):
            for j in range(i + 1, min(len(self.pool), 64)):
                a, b = self.pool[i], self.pool[j]
                if hamming(a, avg) <= self.active_th and hamming(b, avg) <= self.active_th:
                    self._active_pairs.append((a, b))

    def _noise_inject(self):
        """Low-density noise injection"""
        for _ in range(4):
            g = random_gua(self.tick * 100 + _)
            if g not in self.pool:
                self.pool.append(g)

    def _trim(self):
        if len(self.pool) <= self.capacity:
            return
        avg = self.pool_avg()
        dormant = [g for g in self.pool if hamming(g, avg) > self.flowing_th]
        remove = min(len(dormant), len(self.pool) - self.capacity)
        for g in dormant[:remove]:
            self.pool.remove(g)

    def get_active_guas(self) -> list[int]:
        """Return active gua list (fed to Φ-field)"""
        avg = self.pool_avg()
        return [g for g in self.pool if hamming(g, avg) <= self.active_th]


if __name__ == '__main__':
    world = WorldPool(128, active_threshold=10, flowing_threshold=18)
    print(f"World: {world.active_count()} active {world.flowing_count()} flowing {world.dormant_count()} dormant")
    inject = 0x1234567
    for i in range(5):
        st = world.tick_once(yin_inject=inject if i < 2 else 0, has_input=(i < 2))
        print(f"  tick{i+1}: {st['active']}a {st['flowing']}f {st['dormant']}d idle={st['idle']}")
        inject ^= (inject << 7) & MASK28
