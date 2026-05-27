# -*- coding: utf-8 -*-
"""F₂ dual tianyuan: user identity + AI identity · 28-bit positions."""

from dataclasses import dataclass
from v3.constants import CT_MASK, phi_slice, PHI_BITS


@dataclass
class TianYuan:
    ct: int = 0
    last_move: int = 0

    def evolve(self, input_ct: int, tick: int, rate: float = 0.05):
        n_bits = max(1, int(28 * rate))
        seed = phi_slice((tick * 13 + self.last_move * 7) % 256, 28)
        mask = 0
        used = set()
        for i in range(n_bits):
            pos = ((seed >> (i * 9)) & 0x1FF) % 28
            if pos not in used:
                mask |= (1 << pos)
                used.add(pos)
        self.ct = (self.ct & ~mask) | (input_ct & mask)
        self.ct &= CT_MASK
        self.last_move = tick

    def distance_to(self, other_ct: int) -> int:
        return (self.ct ^ other_ct).bit_count()

    def direction_to(self, target_ct: int) -> int:
        return self.ct ^ target_ct


def default_user_tianyuan() -> TianYuan:
    return TianYuan(ct=0)


def default_ai_tianyuan() -> TianYuan:
    ai_ct = 0
    for i in range(28):
        if PHI_BITS[(i * 17) % len(PHI_BITS)] == '1':
            ai_ct |= (1 << i)
    return TianYuan(ct=ai_ct & CT_MASK)
