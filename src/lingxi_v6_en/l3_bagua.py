# -*- coding: utf-8 -*-
"""L3 Bagua Layer — 64 GuaYuan ring · Hamming transitions · Lightning chain · zero-float"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from guayuan import MASK28, hamming, xor_reduce, nearest, gua_hash, get_bits

BAGUA = ['Qian', 'Dui', 'Li', 'Zhen', 'Xun', 'Kan', 'Gen', 'Kun']

def hex_name(upper: int, lower: int) -> str:
    return f"{BAGUA[upper]}{BAGUA[lower]}"


class BaguaRing:
    """64 GuaYuan ring"""

    def __init__(self):
        self.refs: list[int] = []
        self.active_idx = 0
        self.active_gua = 0
        self.tick = 0
        self.lightning_path: list[int] = []
        self._build_refs()

    def _build_refs(self):
        """Generate 64 reference codes"""
        for upper in range(8):
            for lower in range(8):
                ref = (upper << 25) | (lower << 22)
                fill = upper ^ lower
                for i in range(8):
                    fill = ((fill << 3) ^ (fill * 7)) & 0x3FFFFF
                ref |= fill & 0x3FFFFF
                self.refs.append(ref & MASK28)

    def current_hex_name(self) -> str:
        upper = get_bits(self.active_gua, 28, 25)
        lower = get_bits(self.active_gua, 25, 22)
        return hex_name(upper % 8, lower % 8)

    def current_trigram(self) -> str:
        upper = get_bits(self.active_gua, 28, 25)
        return BAGUA[upper % 8]

    def set_from_attractor(self, attractor: int):
        self.active_gua = attractor & MASK28
        self.active_idx = self._nearest_idx(self.active_gua)

    def tick_once(self, phi_ctx: int = 0, attractor: int = 0) -> dict:
        """One frame: time-sync → Hamming transition → Lightning"""
        self.tick += 1
        time_idx = self.tick % 64

        candidates = []
        for idx, ref in enumerate(self.refs):
            d = hamming(self.active_gua, ref)
            candidates.append((idx, d))
        candidates.sort(key=lambda x: x[1])

        top4 = candidates[:4]
        weights = [1.0 / (d + 1) for _, d in top4]
        total_w = sum(weights)
        r = (attractor ^ (self.tick * 7)) % max(1, int(total_w * 100))
        cum = 0
        chosen = top4[0]
        for (idx, d), w in zip(top4, weights):
            cum += w * 100
            if r <= cum:
                chosen = (idx, d)
                break

        new_idx = chosen[0]
        new_ref = self.refs[new_idx]
        self.active_gua = (self.active_gua ^ new_ref ^ phi_ctx ^ (attractor >> 4)) & MASK28
        self.active_idx = new_idx

        self.lightning_path.append(self.active_gua)
        if len(self.lightning_path) > 4:
            self.lightning_path.pop(0)

        lightning_gua = 0
        if len(self.lightning_path) >= 3:
            lightning_gua = xor_reduce(self.lightning_path[-3:])

        return {
            'idx': self.active_idx,
            'name': self.current_hex_name(),
            'trigram': self.current_trigram(),
            'lightning': lightning_gua,
            'time_sync': (self.active_idx == time_idx),
        }

    def _nearest_idx(self, gua: int) -> int:
        best_idx, best_d = 0, 999
        for idx, ref in enumerate(self.refs):
            d = hamming(gua, ref)
            if d < best_d:
                best_d, best_idx = d, idx
        return best_idx

    def force_jump(self, gua: int):
        """YongJiu-forced jump"""
        self.active_gua = gua & MASK28
        self.active_idx = self._nearest_idx(gua)


if __name__ == '__main__':
    ring = BaguaRing()
    ring.set_from_attractor(0x1234567)
    print(f"Initial: {ring.current_hex_name()} idx={ring.active_idx}")
    for i in range(8):
        st = ring.tick_once(phi_ctx=i * 0x111111, attractor=0xABCDEF0 + i)
        print(f"  tick{i+1}: {st['name']} trgm={st['trigram']} L={st['lightning']:08X} sync={st['time_sync']}")
