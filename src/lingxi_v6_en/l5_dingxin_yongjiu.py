# -*- coding: utf-8 -*-
"""DingXin + YongJiu — 5-value gating · free GuaYuan probe · zero-float"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from guayuan import MASK28, hamming, xor_reduce, gua_hash, random_gua


class DingXinZhuizi:
    """DingXin: 5-dimensional value gating + dual persona"""

    VALUES = ['Sincerity', 'Benevolence', 'Wisdom', 'Courage', 'Harmony']

    def __init__(self):
        self.value_guas = {v: gua_hash(v) for v in self.VALUES}
        self.th_guide = 0.3
        self.th_accept = 0.5
        self.th_caution = 0.7
        self.user_tianyuan = gua_hash("user")
        self.ai_persona = self._init_persona()
        self.tick = 0

    def _init_persona(self) -> int:
        r = 0
        for v in self.VALUES:
            r ^= self.value_guas[v]
        return r & MASK28

    def align(self, candidate: int) -> tuple[str, float]:
        """Gate alignment: candidate gua vs 5 values → (grade, avg_dist)"""
        total_d = 0
        for v in self.VALUES:
            total_d += hamming(candidate, self.value_guas[v])
        avg = total_d / 5.0 / 28.0
        if avg < self.th_guide:
            return 'GUIDE', avg
        elif avg < self.th_accept:
            return 'ACCEPT', avg
        elif avg < self.th_caution:
            return 'CAUTION', avg
        else:
            return 'REJECT', avg

    def modulate_prob(self, candidate: int, base_prob: float) -> float:
        level, _ = self.align(candidate)
        factors = {'GUIDE': 1.5, 'ACCEPT': 1.0, 'CAUTION': 0.5, 'REJECT': 0.0}
        return base_prob * factors[level]

    def update_user(self, attractor: int):
        self.user_tianyuan ^= (attractor >> 4) & MASK28
        self.tick += 1

    def update_persona(self, feedback_gua: int, weight: float = 0.05):
        self.ai_persona ^= (feedback_gua >> 3) & MASK28


class YongJiu:
    """YongJiu: free GuaYuan probe · three-talent detection · dual-well · field quench"""

    def __init__(self):
        self.gua = 0x0FFFFFFF
        self.shallow = 0
        self.deep = 0
        self.tick = 0
        self.trigger_count = 0
        self.L_threshold = 0.35
        self._history: list[int] = []

    def three_talents(self, pool: list[int]) -> float:
        """Heaven·Earth·Human joint detection → L ∈ [0,1]"""
        if not pool or len(pool) < 4:
            return 0.0
        sample = pool[:min(len(pool), 256)]
        self._history = sample

        total = xor_reduce(sample)
        entropy = total.bit_count() / 28.0
        unique = len(set(sample))
        coverage = unique / len(sample)
        density = sum(g.bit_count() for g in sample) / (len(sample) * 28.0)
        L = entropy * 0.5 + (1.0 - coverage) * 0.2 + density * 0.3
        return L

    def tick_once(self, attractor: int, pool: list[int]) -> dict:
        self.tick += 1
        self.shallow = (self.gua ^ attractor) & MASK28
        self.deep = (self.gua ^ ((attractor << 7) ^ (attractor >> 14))) & MASK28

        if self.tick % 2 == 0:
            self.gua = self.shallow
        else:
            self.gua = self.deep

        split = hamming(self.shallow, self.deep)
        L = self.three_talents(pool)

        triggered = False
        quenched = False
        if L > self.L_threshold or split >= 20:
            triggered = True
            self.trigger_count += 1
        elif split < 4:
            self.trigger_count = max(0, self.trigger_count - 1)

        if self.trigger_count >= 3:
            quenched = True
            self._quench(pool)

        completion = 0
        if split >= 20:
            completion = (self.shallow ^ self.deep) & MASK28

        return {
            'gua': self.gua, 'split': split, 'L': L,
            'triggered': triggered, 'quench': quenched, 'completion': completion,
        }

    def _quench(self, pool: list[int]):
        self.gua = 0
        if pool:
            self.gua = xor_reduce(pool[:128])
        self.trigger_count = 0


if __name__ == '__main__':
    dxz = DingXinZhuizi()
    for gua in [0x1234567, 0xABCDEF0, 0x5555555, 0x0000000]:
        level, _ = dxz.align(gua)
        print(f"  DingXin: gua=0x{gua:07X} → {level}")

    yj = YongJiu()
    pool = [random_gua(i) for i in range(200)]
    print(f"\n  YongJiu init: 0x{yj.gua:07X}")
    for i in range(6):
        st = yj.tick_once(attractor=random_gua(i * 99), pool=pool)
        print(f"  tick{i+1}: split={st['split']} L={st['L']:.3f} trig={st['triggered']} quench={st['quench']}")
