# -*- coding: utf-8 -*-
"""Oscillator Layer v8.0 — oscillation-modulated world-layer activation boundary · perpetual reciprocity"""
import os, sys, time, random
from .guayuan import MASK28, hamming, xor_reduce, random_gua
from .shared_pool import SharedPool


class YinYangEngine:
    """Oscillator engine: drives world-layer via oscillating pairs, modulates activate/sleep boundaries"""

    def __init__(self, pairs: int = 32):
        self.pairs = pairs
        self.yin: list[int] = []
        self.yang: list[int] = []
        self.phases: list[float] = []
        self.tick = 0
        self.coherence = 0.5
        self._init_pairs()

    def _init_pairs(self):
        for i in range(self.pairs):
            self.yin.append(random_gua(i))
            self.yang.append(random_gua(i + 100000))
            self.phases.append(random.random() * 6.283)

    def tick_once(self) -> dict:
        """Single oscillation frame"""
        self.tick += 1
        total_swap = 0

        for i in range(self.pairs):
            self.phases[i] = (self.phases[i] + 0.15) % 6.283
            phase = self.phases[i]

            y, ng = self.yin[i], self.yang[i]
            swap_bits = min(14, max(1, int(7 + 7 * (phase - 3.141) / 3.141)))
            mask = (1 << abs(swap_bits)) - 1

            if phase < 3.141:
                y_new = (y & ~mask) ^ (ng & mask)
                ng_new = (ng & ~mask) ^ (y & mask)
            else:
                y_new = (y & ~mask) ^ (ng & mask)
                ng_new = (ng & ~mask) ^ (y & mask)

            self.yin[i] = y_new & MASK28
            self.yang[i] = ng_new & MASK28
            total_swap += swap_bits

        # coherence
        yin_xor = xor_reduce(self.yin)
        yang_xor = xor_reduce(self.yang)
        self.coherence = 1.0 - hamming(yin_xor, yang_xor) / 28.0

        # bias
        yin_bits = yin_xor.bit_count()
        yang_bits = yang_xor.bit_count()
        bias = (yin_bits - yang_bits) / 28.0

        return {
            'tick': self.tick,
            'coherence': round(self.coherence, 3),
            'bias': round(bias, 3),
            'bias_label': 'yin' if bias > 0.05 else ('yang' if bias < -0.05 else 'neutral'),
        }

    def modulate_pool(self, pool: SharedPool):
        """
        Oscillator modulates world layer:
        - yin-dominant → raise activation threshold (conservative)
        - yang-dominant → lower activation threshold (exploratory)
        """
        yin_xor = xor_reduce(self.yin)
        yang_xor = xor_reduce(self.yang)
        yin_bits = yin_xor.bit_count()
        yang_bits = yang_xor.bit_count()

        bias = (yin_bits - yang_bits) / 28.0
        pool.YIN_BIAS = max(0.0, bias * 0.2)
        pool.YANG_BIAS = max(0.0, -bias * 0.2)

    def heartbeat(self) -> int:
        """Heartbeat vector: XOR-reduce all yin-yang pairs"""
        return xor_reduce(self.yin + self.yang)

    def is_alive(self) -> bool:
        return any(y != ng for y, ng in zip(self.yin, self.yang))
