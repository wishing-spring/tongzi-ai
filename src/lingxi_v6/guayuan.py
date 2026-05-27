# -*- coding: utf-8 -*-
"""卦元基础设施 — 28位通用载体 · 零浮点"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

MASK28 = 0x0FFFFFFF  # 28位掩码
WIDTH = 28


def gua_hash(s: str) -> int:
    """字符串→28位卦元"""
    h = 0
    for ch in s:
        h = ((h << 5) ^ ord(ch)) & MASK28
    return h


def hamming(a: int, b: int) -> int:
    """Hamming距离 (Python 3.8+ bit_count)"""
    return ((a ^ b) & MASK28).bit_count()


def xor_reduce(vals: list) -> int:
    """XOR归约"""
    r = 0
    for v in vals:
        r ^= v
    return r & MASK28


def pool_average(vals: list) -> int:
    """池平均卦元: XOR所有值后右移log2(N)"""
    if not vals:
        return 0
    total = xor_reduce(vals)
    shift = (len(vals).bit_length() - 1)
    if shift > 0:
        total >>= shift
    return total & MASK28


def nearest(vals: list, target: int, exclude: set = None) -> int:
    """找Hamming距离最近的卦元"""
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
    """生成一个卦元 (确定性，基于seed XOR)"""
    import time
    t = int(time.time() * 1000) if seed == 0 else seed
    h = t & MASK28
    for _ in range(4):
        h = ((h << 7) ^ (h >> 5) ^ (h << 13)) & MASK28
    return h


# ── 位段提取 ──
def get_bits(g: int, hi: int, lo: int) -> int:
    """提取 [hi:lo] 位段 (hi inclusive, lo exclusive)"""
    return (g >> lo) & ((1 << (hi - lo)) - 1)


def set_bits(g: int, hi: int, lo: int, val: int) -> int:
    """设置 [hi:lo] 位段"""
    mask = ((1 << (hi - lo)) - 1) << lo
    return (g & ~mask) | ((val & ((1 << (hi - lo)) - 1)) << lo)


print(f"[卦元] 28bit · 零浮点 · {__name__}")
