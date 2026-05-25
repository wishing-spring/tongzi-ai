# -*- coding: utf-8 -*-
"""Fundamental constants — φ mother body, bit masks, suit symbols."""

# The golden ratio φ = (1+√5)/2 as a 256-bit binary fractional expansion.
# All gua values are slices of φ. The mother body is the "soil" that
# determines which attractor basins form.
PHI_BITS = [
    1,0,0,1,1,1,1,0, 0,0,1,1,0,1,1,1, 0,1,1,1,1,0,0,1, 1,0,0,1,1,1,1,0,
    0,0,1,0,1,0,1,0, 0,1,1,1,1,1,0,0, 1,1,1,0,1,0,1,1, 0,1,0,0,1,1,1,0,
    0,1,0,0,0,1,0,1, 0,1,0,1,0,1,0,1, 1,0,1,1,1,0,1,0, 0,1,0,0,1,0,0,1,
    1,1,1,0,1,1,1,0, 0,0,0,1,0,1,1,1, 1,0,0,1,0,0,1,0, 0,1,0,1,0,0,0,1,
    0,0,1,0,1,0,1,1, 1,1,0,1,1,0,0,0, 1,1,1,0,1,0,0,0, 1,0,1,1,0,0,1,0,
    0,1,1,1,0,0,0,1, 1,0,1,1,0,1,0,1, 1,0,0,1,1,1,0,0, 0,1,1,0,0,0,0,1,
    0,1,0,1,0,0,1,0, 0,1,1,1,1,1,1,0, 0,1,1,1,1,1,1,0, 0,1,1,1,0,0,1,1,
    0,1,0,1,1,0,0,1, 0,0,1,0,1,0,1,0, 0,0,1,0,1,0,1,1, 1,0,0,0,1,0,0,1,
]

# Suits — four identities, same character different tracks
SUITS = ['\u2665', '\u2666', '\u2663', '\u2660']  # ♥♦♣♠

# Bit masks
ID_MASK   = 0xF0000000   # 4-bit suit ID (bits 28-31)
CT_MASK   = 0x0FFFFFFF   # 28-bit content (bits 0-27)

# F₀ — base frequency for eco pool energy accumulation
F0 = 32


def phi_slice(start: int, nbits: int) -> int:
    """Extract nbits from PHI_BITS starting at position 'start'."""
    val = 0
    for i in range(nbits):
        idx = start + i
        if idx < len(PHI_BITS) and PHI_BITS[idx]:
            val |= (1 << (nbits - 1 - i))
    return val


def to_hex(v: int, nbits: int = 28) -> str:
    """Format an integer as hex with leading zeros for nbits."""
    return f"{v:0{(nbits + 3) // 4}x}"


def rotl_group(v: int, start: int, nbits: int, k: int) -> int:
    """Rotate an nbit-group left by k positions within a value, keeping other bits."""
    mask = ((1 << nbits) - 1) << start
    group = (v & mask) >> start
    rotated = ((group << k) | (group >> (nbits - k))) & ((1 << nbits) - 1)
    return (v & ~mask) | (rotated << start)
