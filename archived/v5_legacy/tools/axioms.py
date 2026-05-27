# Copyright (c) 2026 Tongzi Project (wishing-spring)
# Licensed under the MIT License. See LICENSE file for details.
"""
工具 · 公理与群运算
=====================
四条公理 + 八条核心群运算。

使用:
  from tools.axioms import hamming, rotate_left, collide
  diff, comm = collide(gua_a, gua_b)

所有函数是纯函数, 无副作用, 不依赖 Gua 类。
"""

from tongzi_constants import VEC_DIM, FULL_MASK

# ============================================================
# 四条公理
# ============================================================

def hamming(a: int, b: int) -> int:
    """公理3: d(a,b) = popcount(a⊕b)。汉明距离。"""
    return (a ^ b).bit_count()


def rotate_left(v: int, k: int) -> int:
    """公理4: 位循环左旋 Rk(v)。旋转保距。"""
    k %= VEC_DIM
    return ((v << k) | (v >> (VEC_DIM - k))) & FULL_MASK


def rotate_right(v: int, k: int) -> int:
    """对称右旋。"""
    k %= VEC_DIM
    return ((v >> k) | (v << (VEC_DIM - k))) & FULL_MASK


def gray_encode(n: int) -> int:
    """格雷编码: n → n⊕(n>>1)。"""
    return n ^ (n >> 1)


def gray_decode(n: int) -> int:
    """反格雷解码。"""
    mask = n
    while mask:
        mask >>= 1
        n ^= mask
    return n & FULL_MASK


def gray_ring(v: int) -> int:
    """格雷环上的下一站。相邻卦汉明距离恒为 1。"""
    n = gray_encode(v)
    n = (n + 1) & FULL_MASK
    return gray_decode(n)


# ============================================================
# 八运算群
# ============================================================

def collide(a: int, b: int) -> tuple:
    """碰撞: (差异位, 共同位)。
    diff = a⊕b, comm = ~(a⊕b)
    """
    diff = a ^ b
    comm = (~diff) & FULL_MASK
    return diff, comm


def orbit(a: int, center: int, step: int = 1) -> int:
    """绕 center 旋转 step 步。
    a' = Rₛₜₑₚ(a ⊕ center) ⊕ center
    """
    delta = a ^ center
    rotated = rotate_left(delta, step)
    return (rotated ^ center) & FULL_MASK


def stretch(a: int, toward: int, lam: int) -> int:
    """向 toward 伸缩 lam 步。
    λ ∈ [0, VEC_DIM]
    """
    lam = max(0, min(lam, VEC_DIM))
    diff = a ^ toward
    mask = ((1 << lam) - 1) << (VEC_DIM - lam)
    move = diff & mask
    return (a ^ move) & FULL_MASK


def ball(value: int, radius: int) -> list:
    """汉明球: 所有距离 ≤ radius 的值。"""
    result = []
    for v in range(FULL_MASK + 1):
        if hamming(value, v) <= radius:
            result.append(v)
    return result


def centrality(value: int, others: list) -> float:
    """中心度: 1 / (1 + 平均汉明距离)。
    注意: 唯一使用浮点的地方, 仅用于度量。
    """
    if not others:
        return 1.0
    avg_d = sum(hamming(value, v) for v in others) / len(others)
    return 1.0 / (1.0 + avg_d)
