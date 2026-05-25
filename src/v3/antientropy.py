# -*- coding: utf-8 -*-
"""反熵 — 检测僵化 + φ引导微偏移打破封闭群"""

from .constants import phi_slice, CT_MASK


class AntiEntropy:
    """僵化检测 + φ注入扰动。

    灵犀第九卦: 打破纯碰撞的死亡秩序。
    童子: 检测连续无新生 → φ切片引导翻转 → 新碰撞链。
    """

    def __init__(self, stagnation_window: int = 5, jitter_bits: int = 3):
        self.stagnation_window = stagnation_window
        self.jitter_bits = jitter_bits
        self.stagnation_ticks = 0
        self.total_jitters = 0
        self.last_births = 0

    def check(self, total_births: int) -> bool:
        """返回 True 表示需要注熵。"""
        if total_births == self.last_births:
            self.stagnation_ticks += 1
        else:
            self.stagnation_ticks = 0
            self.last_births = total_births
        return self.stagnation_ticks >= self.stagnation_window

    def jitter(self, ct: int, tick: int) -> int:
        """φ引导微偏移。"""
        self.total_jitters += 1
        self.stagnation_ticks = 0

        seed = phi_slice((tick * 17 + self.total_jitters * 31) % 256, 28)
        
        jitter_positions = []
        for i in range(self.jitter_bits):
            pos = ((seed >> (i * 9)) & 0x1FF) % 28
            if pos not in jitter_positions:
                jitter_positions.append(pos)

        result = ct
        for pos in jitter_positions:
            result ^= (1 << pos)

        return result & CT_MASK

    def stats(self) -> str:
        return f"反熵: {self.total_jitters}次注入"
