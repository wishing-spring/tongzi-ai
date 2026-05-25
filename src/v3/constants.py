# -*- coding: utf-8 -*-
"""童子 v3.0 · 全局常量"""

PHI_BITS = (
    "10011110001101110111100110111001"
    "01111111010010100111110000010101"
    "00011011001000100110111101111101"
    "00111001010111101110011001011010"
    "01111010011011110011110001010111"
    "00100001011001000011011111011111"
    "01110010000111011111101101001011"
    "01001110101111110011100101111011"
)
PHI_LEN = 256
VEC_DIM = 32
FULL_MASK = 0xFFFFFFFF

SUITS      = ['♥', '♦', '♣', '♠']
ID_MASK    = 0xF0000000
CT_MASK    = 0x0FFFFFFF

def phi_slice(start: int, n: int) -> int:
    v = 0
    for i in range(n):
        if PHI_BITS[(start + i) % PHI_LEN] == '1':
            v |= (1 << i)
    return v

def rotl_group(v: int, gs: int, gz: int, steps: int) -> int:
    mask = ((1 << gz) - 1) << gs
    grp = (v & mask) >> gs
    k = steps % gz
    rot = ((grp << k) | (grp >> (gz - k))) & ((1 << gz) - 1)
    return (v & ~mask) | (rot << gs)
