# -*- coding: utf-8 -*-
"""童子F₂池 — 闭壳XOR碰撞 · 连环咬合编码 · 四生态池 · 零浮点"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from guayuan import MASK28, hamming, xor_reduce, gua_hash, random_gua


# ── 四生态池卦名 ──
ECO_NAMES = '♠黑桃 ♥红心 ♦方块 ♣梅花'.split()
ECO_SEEDS = ['桃', '心', '方', '梅']


class TongziPool:
    """童子F₂闭壳碰撞池"""

    def __init__(self, surge_cap: int = 4096, eco_cap: int = 1024):
        self.surge: dict[int, dict] = {}   # 涌动池 {gua_id: {gua, mask, energy}}
        self.eco: list[dict] = [{} for _ in range(4)]  # 四生态池
        self.surge_cap = surge_cap
        self.eco_cap = eco_cap
        self.next_id = 0
        self.tick = 0
        self.attractor = 0
        self._init_eco()

    def _init_eco(self):
        """四池种子"""
        for i, seed in enumerate(ECO_SEEDS):
            g = gua_hash(seed)
            for _ in range(8):
                child = (g ^ random_gua(i * 100 + _)) & MASK28
                self.eco[i][child] = {'hits': 2, 'solid': True}  # 种子天生固化

    # ── 连环咬合编码 ──
    def encode(self, text: str) -> list[int]:
        """文字 → 卦元链 (连环咬合)"""
        chain = []
        prev = 0
        shift = 0
        for ch in text:
            # 哈希索引
            h = gua_hash(ch)
            # 连环咬合: 与前一卦元XOR
            linked = ((h << (shift % 8)) ^ prev ^ (prev >> 3)) & MASK28
            chain.append(linked)
            prev = linked
            shift = (shift + 1) % 8
        return chain

    # ── 核心 tick ──
    def tick_once(self, inject_guas: list[int] = None) -> int:
        """
        一帧:
          1. 注入编码 → 涌动池
          2. 涌动(mask碰撞) → 子卦
          3. 子卦 → 生态池碰撞
          4. 全局attractor
        """
        self.tick += 1

        # 1. 注入
        if inject_guas:
            for g in inject_guas:
                self.surge[self.next_id] = {'gua': g, 'mask': g, 'energy': 1}
                self.next_id += 1

        # 2. 涌动: mask碰撞 → 子卦
        children = self._surge_collide()

        # 3. 子卦 → 生态池
        self._eco_collide(children)

        # 4. 全局attractor
        self._update_attractor()

        # 5. 容量控制
        self._trim()

        return self.attractor

    def _surge_collide(self) -> list[int]:
        """涌动池碰撞: mask间XOR → 子卦 → 回流"""
        children = []
        items = list(self.surge.items())
        if len(items) < 2:
            return children

        # 采样: 随机选32对碰撞
        import random
        all_keys = list(self.surge.keys())
        n_pairs = min(32, len(all_keys) * (len(all_keys) - 1) // 2)

        for _ in range(n_pairs):
            if len(all_keys) < 2:
                break
            a_key, b_key = random.sample(all_keys, 2)
            a, b = self.surge[a_key], self.surge[b_key]

            # mask碰撞
            child = a['mask'] ^ b['mask']
            if child == 0:
                continue
            child &= MASK28
            children.append(child)

            # 流回: mask吸收
            a['mask'] ^= (child >> 4) & MASK28
            b['mask'] ^= (child >> 4) & MASK28
            a['energy'] = a.get('energy', 1) + 1
            b['energy'] = b.get('energy', 1) + 1

        # 子卦回流涌动池 (作为新卦元入驻)
        for child in children[:16]:
            if child not in [v['gua'] for v in self.surge.values()]:
                self.surge[self.next_id] = {'gua': child, 'mask': child, 'energy': 1}
                self.next_id += 1

        return children

    def _eco_collide(self, children: list[int]):
        """子卦进入生态池碰撞"""
        for child in children:
            if child == 0:
                continue
            # 四池分摊
            for i in range(4):
                self._try_eco_inject(i, child)

    def _try_eco_inject(self, pool_idx: int, gua: int):
        """尝试注入生态池: 碰撞双方都加hits"""
        pool = self.eco[pool_idx]
        thresholds = [8, 10, 12, 14]
        th = thresholds[pool_idx]

        if gua in pool:
            pool[gua]['hits'] += 1
            if pool[gua]['hits'] >= 3:
                pool[gua]['solid'] = True
            return

        # 直接入驻
        pool[gua] = {'hits': 1, 'solid': False}

        # 如果池满，不做碰撞 (避免全满时无空间)
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
            # 双方都hit
            pool[gua]['hits'] += 1
            pool[nearest_g]['hits'] += 1
            if pool[gua]['hits'] >= 3:
                pool[gua]['solid'] = True
            if pool[nearest_g]['hits'] >= 3:
                pool[nearest_g]['solid'] = True

            # XOR碰撞产出新卦
            collision = (gua ^ nearest_g) & MASK28
            if collision not in pool and collision != 0:
                pool[collision] = {'hits': 0, 'solid': False}

    def _update_attractor(self):
        """全局attractor = 涌动池XOR ⊕ 四池XOR"""
        surge_sum = xor_reduce([v['gua'] for v in self.surge.values()])
        eco_sum = 0
        for pool in self.eco:
            eco_sum ^= xor_reduce(list(pool.keys()))
        self.attractor = (surge_sum ^ eco_sum) & MASK28

    def _trim(self):
        """容量控制"""
        # 涌动池: 淘汰低能量
        if len(self.surge) > self.surge_cap:
            items = sorted(self.surge.items(), key=lambda x: x[1].get('energy', 0))
            remove = items[:len(self.surge) - self.surge_cap]
            for k, _ in remove:
                del self.surge[k]

        # 生态池: 淘汰未固化
        for i in range(4):
            if len(self.eco[i]) > self.eco_cap:
                unsolid = [(g, d) for g, d in self.eco[i].items() if not d['solid']]
                remove = unsolid[:len(self.eco[i]) - self.eco_cap]
                for g, _ in remove:
                    del self.eco[i][g]

    # ── 状态 ──
    def report(self) -> str:
        surge_g = xor_reduce([v['gua'] for v in self.surge.values()])
        eco_counts = [len(p) for p in self.eco]
        solid_counts = [sum(1 for d in p.values() if d['solid']) for p in self.eco]
        return (f"童: surge={len(self.surge)}卦 eco={eco_counts} "
                f"固={solid_counts} attr=0x{self.attractor:07X}")


if __name__ == '__main__':
    tz = TongziPool(surge_cap=512, eco_cap=32)
    text = "天地玄黄宇宙洪荒"
    chain = tz.encode(text)
    print(f"编码 '{text}' → {len(chain)}卦元")

    for _ in range(10):
        attr = tz.tick_once(inject_guas=chain if _ == 0 else None)
        print(f"  t{_+1}: {tz.report()}")
