# -*- coding: utf-8 -*-
"""Tongzi F₂ Pool — Closed-shell XOR collision · Chain-linked encoding · 4 eco-pools · zero-float"""
import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
from guayuan import MASK28, hamming, xor_reduce, gua_hash, random_gua

ECO_NAMES = '♠Spade ♥Heart ♦Diamond ♣Club'.split()
ECO_SEEDS = ['桃', '心', '方', '梅']


class TongziPool:
    """Tongzi F₂ closed-shell collision pool"""

    def __init__(self, surge_cap: int = 4096, eco_cap: int = 1024):
        self.surge: dict[int, dict] = {}   # surge pool {id: {gua, mask, energy}}
        self.eco: list[dict] = [{} for _ in range(4)]  # 4 eco-pools
        self.surge_cap = surge_cap
        self.eco_cap = eco_cap
        self.next_id = 0
        self.tick = 0
        self.attractor = 0
        self._init_eco()

    def _init_eco(self):
        """Seed 4 eco-pools with solid gua"""
        for i, seed in enumerate(ECO_SEEDS):
            g = gua_hash(seed)
            for _ in range(8):
                child = (g ^ random_gua(i * 100 + _)) & MASK28
                self.eco[i][child] = {'hits': 2, 'solid': True}

    def encode(self, text: str) -> list[int]:
        """Text → GuaYuan chain (chain-linked encoding)"""
        chain = []
        prev = 0
        shift = 0
        for ch in text:
            h = gua_hash(ch)
            linked = ((h << (shift % 8)) ^ prev ^ (prev >> 3)) & MASK28
            chain.append(linked)
            prev = linked
            shift = (shift + 1) % 8
        return chain

    def tick_once(self, inject_guas: list[int] = None) -> int:
        """One tick: inject → surge collision → eco collision → attractor"""
        self.tick += 1

        if inject_guas:
            for g in inject_guas:
                self.surge[self.next_id] = {'gua': g, 'mask': g, 'energy': 1}
                self.next_id += 1

        children = self._surge_collide()
        self._eco_collide(children)
        self._update_attractor()
        self._trim()
        return self.attractor

    def _surge_collide(self) -> list[int]:
        """Surge pool collision: mask XOR → children → backflow"""
        children = []
        all_keys = list(self.surge.keys())
        if len(all_keys) < 2:
            return children

        n_pairs = min(32, len(all_keys) * (len(all_keys) - 1) // 2)
        for _ in range(n_pairs):
            if len(all_keys) < 2:
                break
            a_key, b_key = random.sample(all_keys, 2)
            a, b = self.surge[a_key], self.surge[b_key]

            child = a['mask'] ^ b['mask']
            if child == 0:
                continue
            child &= MASK28
            children.append(child)

            a['mask'] ^= (child >> 4) & MASK28
            b['mask'] ^= (child >> 4) & MASK28
            a['energy'] = a.get('energy', 1) + 1
            b['energy'] = b.get('energy', 1) + 1

        # Backflow: children re-enter surge pool
        for child in children[:16]:
            if child not in [v['gua'] for v in self.surge.values()]:
                self.surge[self.next_id] = {'gua': child, 'mask': child, 'energy': 1}
                self.next_id += 1

        return children

    def _eco_collide(self, children: list[int]):
        """Route children into 4 eco-pools"""
        for child in children:
            if child == 0:
                continue
            for i in range(4):
                self._try_eco_inject(i, child)

    def _try_eco_inject(self, pool_idx: int, gua: int):
        """Inject gua into eco-pool: collision → both parties gain hits"""
        pool = self.eco[pool_idx]
        thresholds = [8, 10, 12, 14]
        th = thresholds[pool_idx]

        if gua in pool:
            pool[gua]['hits'] += 1
            if pool[gua]['hits'] >= 3:
                pool[gua]['solid'] = True
            return

        pool[gua] = {'hits': 1, 'solid': False}
        if len(pool) <= 1:
            return

        nearest_g, nearest_d = None, 999
        for g in pool:
            if g == gua:
                continue
            d = hamming(gua, g)
            if d < nearest_d:
                nearest_d, nearest_g = d, g

        if nearest_d <= th and nearest_g is not None:
            pool[gua]['hits'] += 1
            pool[nearest_g]['hits'] += 1
            if pool[gua]['hits'] >= 3:
                pool[gua]['solid'] = True
            if pool[nearest_g]['hits'] >= 3:
                pool[nearest_g]['solid'] = True

            collision = (gua ^ nearest_g) & MASK28
            if collision not in pool and collision != 0:
                pool[collision] = {'hits': 0, 'solid': False}

    def _update_attractor(self):
        """Global attractor = XOR of surge pool ⊕ 4 eco-pools"""
        surge_sum = xor_reduce([v['gua'] for v in self.surge.values()])
        eco_sum = 0
        for pool in self.eco:
            eco_sum ^= xor_reduce(list(pool.keys()))
        self.attractor = (surge_sum ^ eco_sum) & MASK28

    def _trim(self):
        """Capacity control: remove low-energy from surge, unsolid from eco"""
        if len(self.surge) > self.surge_cap:
            items = sorted(self.surge.items(), key=lambda x: x[1].get('energy', 0))
            remove = items[:len(self.surge) - self.surge_cap]
            for k, _ in remove:
                del self.surge[k]

        for i in range(4):
            if len(self.eco[i]) > self.eco_cap:
                unsolid = [(g, d) for g, d in self.eco[i].items() if not d['solid']]
                remove = unsolid[:len(self.eco[i]) - self.eco_cap]
                for g, _ in remove:
                    del self.eco[i][g]

    def report(self) -> str:
        surge_g = xor_reduce([v['gua'] for v in self.surge.values()])
        eco_counts = [len(p) for p in self.eco]
        solid_counts = [sum(1 for d in p.values() if d['solid']) for p in self.eco]
        return (f"Tongzi: surge={len(self.surge)} gua eco={eco_counts} "
                f"solid={solid_counts} attr=0x{self.attractor:07X}")


if __name__ == '__main__':
    tz = TongziPool(surge_cap=512, eco_cap=32)
    text = "天地玄黄宇宙洪荒"
    chain = tz.encode(text)
    print(f"Encode '{text}' → {len(chain)} gua")
    for _ in range(10):
        attr = tz.tick_once(inject_guas=chain if _ == 0 else None)
        print(f"  t{_+1}: {tz.report()}")
