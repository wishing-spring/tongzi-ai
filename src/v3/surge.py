# -*- coding: utf-8 -*-
"""Surge — F₂ equivalent of the I Ching disc rotation.

The "surge" mechanism mimics the rotation of the 64-hexagram disc:
instead of rotating the hexagrams themselves, a 16-bit matching window
slides across the 28-bit F₂ space. Same pair of gua, different window
positions → different matching bits → continuous new collisions.
"""

from .constants import phi_slice, CT_MASK, rotl_group

SURGE_CYCLE = 3   # ticks per surge phase
WINDOW_BITS = 16  # matching window size (16 of 28 bits)


# Per-suit rotation rates for birth-signature surge
_RATES = {
    0: [1, 3, 5, 7],
    1: [2, 5, 7, 11],
    2: [3, 7, 11, 13],
    3: [5, 11, 13, 17],
}

_BASE_MASK = ((1 << WINDOW_BITS) - 1) << 0


def surge_mask(tick: int) -> int:
    """Surge window mask — rotates every phase, only matching bits in-window.

    Each phase slides the 16-bit window by 3 bits (10 phases = full cycle).
    The mask is ANDed with XOR results to determine which bit positions
    contribute to the current collision match.
    """
    phase = tick // SURGE_CYCLE
    shift = (phase * 3) % 28
    mask = rotl_group(_BASE_MASK, 0, 28, shift)
    return mask & CT_MASK


def surge(v: int, tick: int) -> int:
    """Surge transform — injects a surge signature during birth.

    Each suit has different rotation rates. The phase-dependent weather
    (φ-slice XOR) ensures the same gua pair produces different children
    at different surge phases.
    """
    phase = tick // SURGE_CYCLE
    sid = (v >> 28) & 0xF
    rates = _RATES.get(sid, [1, 3, 5, 7])

    from .constants import ID_MASK
    _GROUPS = [(0, 8), (8, 8), (16, 8), (24, 4)]
    r = v
    for (gs, gz), rate in zip(_GROUPS, rates):
        r = rotl_group(r, gs, gz, phase * rate)

    weather = phi_slice((phase * 13 + sid * 37) % 256, 28)
    r = (r & ID_MASK) | ((r & CT_MASK) ^ weather)
    return r
