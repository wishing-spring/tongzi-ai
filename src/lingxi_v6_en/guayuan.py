# -*- coding: utf-8 -*-
"""GuaYuan Infrastructure — 28-bit universal carrier · zero-float"""
import os, sys, time
sys.path.insert(0, os.path.dirname(__file__))

MASK28 = 0x0FFFFFFF  # 28-bit mask
WIDTH = 28


def gua_hash(s: str) -> int:
    """String → 28-bit GuaYuan"""
    h = 0
    for ch in s:
        h = ((h << 5) ^ ord(ch)) & MASK28
    return h


def hamming(a: int, b: int) -> int:
    """Hamming distance via bit_count"""
    return ((a ^ b) & MASK28).bit_count()


def xor_reduce(vals: list) -> int:
    """XOR reduction"""
    r = 0
    for v in vals:
        r ^= v
    return r & MASK28


def pool_average(vals: list) -> int:
    """Pool centroid: XOR all then right-shift by log₂(N)"""
    if not vals:
        return 0
    total = xor_reduce(vals)
    shift = (len(vals).bit_length() - 1)
    if shift > 0:
        total >>= shift
    return total & MASK28


def nearest(vals: list, target: int, exclude: set = None) -> int:
    """Find nearest GuaYuan by Hamming distance"""
    if exclude is None:
        exclude = set()
    best, best_d = 0, 999
    for v in vals:
        if v in exclude:
            continue
        d = hamming(v, target)
        if d < best_d:
            best_d, best = d, v
    return best


def random_gua(seed: int = 0) -> int:
    """Deterministic GuaYuan from seed via XOR chain"""
    t = int(time.time() * 1000) if seed == 0 else seed
    h = t & MASK28
    for _ in range(4):
        h = ((h << 7) ^ (h >> 5) ^ (h << 13)) & MASK28
    return h


def get_bits(g: int, hi: int, lo: int) -> int:
    """Extract bit slice [hi:lo]"""
    return (g >> lo) & ((1 << (hi - lo)) - 1)


def set_bits(g: int, hi: int, lo: int, val: int) -> int:
    """Set bit slice [hi:lo]"""
    mask = ((1 << (hi - lo)) - 1) << lo
    return (g & ~mask) | ((val & ((1 << (hi - lo)) - 1)) << lo)


print(f"[GuaYuan] 28bit · zero-float · {__name__}")
