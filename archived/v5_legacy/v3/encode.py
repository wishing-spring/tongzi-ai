# -*- coding: utf-8 -*-
"""Four-Suit Pinball Encoding

Each Chinese character is run through 4 pinball tracks (♥♦♣♠).
The char's Unicode codepoint selects which φ-slice pins to XOR,
producing a 28-bit F₂ content vector + 4-bit suit ID = 32-bit gua.
"""

from .constants import phi_slice, SUITS, ID_MASK, CT_MASK

# 16 pin positions, each a 28-bit slice of φ
_PINS = [phi_slice(i * 28, 28) for i in range(16)]


def encode(ch: str, sid: int) -> int:
    """Encode one char + suit ID → 32-bit gua value.

    High 4 bits = suit ID (0-3 maps to ♥♦♣♠).
    Low 28 bits = pinball content (XOR of pin positions selected by codepoint).
    """
    cp = ord(ch)
    v = cp
    for i in range(16):
        if cp & (1 << i):
            v ^= _PINS[i]
    return (sid << 28) | (v & CT_MASK)


def suit_of(v: int) -> str:
    """Extract suit symbol from a gua value."""
    sid = (v >> 28) & 0xF
    return SUITS[sid] if sid < 4 else '?'


def content(v: int) -> int:
    """Extract the 28-bit F₂ content from a gua value (strip suit bits)."""
    return v & CT_MASK
