# -*- coding: utf-8 -*-
"""四芯编码 · 弹珠机 + 花色身份"""

from .constants import phi_slice, SUITS, ID_MASK, CT_MASK

_PINS = [phi_slice(i * 28, 28) for i in range(16)]

def encode(ch: str, sid: int) -> int:
    """一字 + 花色ID → 32位卦。高4位=花色，低28位=弹珠内容。"""
    cp = ord(ch)
    v = cp
    for i in range(16):
        if cp & (1 << i):
            v ^= _PINS[i]
    return (sid << 28) | (v & CT_MASK)

def suit_of(v: int) -> str:
    sid = (v >> 28) & 0xF
    return SUITS[sid] if sid < 4 else '?'

def content(v: int) -> int:
    return v & CT_MASK
