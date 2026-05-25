# -*- coding: utf-8 -*-
"""F₂ gravity anchor: pulls output toward "good". Not force, just bias."""

from dataclasses import dataclass
from v3.constants import CT_MASK, phi_slice, PHI_BITS


def _make_good_target() -> int:
    ct = 0
    for i in range(28):
        phase = (i * 17 + i // 7 * 31) % len(PHI_BITS)
        if PHI_BITS[phase] == '1':
            ct |= (1 << i)
    return ct & CT_MASK

GOOD_TARGET = _make_good_target()


@dataclass
class Gravity:
    target_ct: int = GOOD_TARGET
    strength: float = 0.15

    def pull(self, ct: int, tick: int) -> int:
        n_bits = max(1, int(28 * self.strength))
        diff = ct ^ self.target_ct
        if diff == 0:
            return ct
        seed = phi_slice((tick * 53) % 256, 28)
        pull_mask = 0
        used = set()
        diff_positions = [i for i in range(28) if (diff >> i) & 1]
        for i in range(min(n_bits, len(diff_positions))):
            idx = ((seed >> (i * 9)) & 0x1FF) % len(diff_positions)
            pos = diff_positions[idx]
            if pos not in used:
                pull_mask |= (1 << pos)
                used.add(pos)
        return (ct ^ pull_mask) & CT_MASK

    def distance_to_good(self, ct: int) -> int:
        return (ct ^ self.target_ct).bit_count()


FORBIDDEN_PATTERNS = [
    0x0A5A5A5, 0x05A5A5A, 0x0FF0000,
]


def is_forbidden(ct: int, threshold: int = 3) -> bool:
    for pattern in FORBIDDEN_PATTERNS:
        if ((ct ^ pattern) & CT_MASK).bit_count() <= threshold:
            return True
    return False
