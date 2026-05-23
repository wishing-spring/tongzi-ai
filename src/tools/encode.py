# Copyright (c) 2026 Tongzi Project (wishing-spring)
# Licensed under the MIT License. See LICENSE file for details.
"""
工具 · 编解码
===============
文本 ↔ 卦 的所有路径。

使用:
  from tools.encode import encode, batch_encode, text_to_seed
  g1, g2 = encode("天地"), encode("玄黄")
  blocks = batch_encode(["天地","玄黄","宇宙"])  # 同锚点, d=2
"""

from tongzi_constants import VEC_DIM, FULL_MASK, PHI_BITS, PHI_LEN
from tongzi_kernel import Gua, generate_gua


def text_to_seed(text: str) -> int:
    """文本 → φ 起始位置。确定性, 零依赖。"""
    seed = len(text)
    for i, c in enumerate(text):
        seed ^= ord(c) << (i % 8)
    return seed % PHI_LEN


def encode(text: str) -> Gua:
    """文本 → 卦 (哈希式, 幂等但无语义邻近性)。"""
    pos = text_to_seed(text)
    return generate_gua(pos)


def batch_encode(texts: list, anchor: int = 0) -> list:
    """批量编码: 同锚点 XOR 微扰。
    
    批内汉明距离 = 2 (精确可控)。
    """
    base = generate_gua(anchor)
    results = []
    for i, text in enumerate(texts):
        mask = 1 << (i % VEC_DIM)
        value = (base.value ^ mask) & FULL_MASK
        g = Gua(value)
        results.append(g)
    return results


def phi_slice(pos: int, length: int = VEC_DIM) -> int:
    """直接从 φ 取位, 不生成 Gua。"""
    bits = PHI_BITS[pos:pos + length]
    if len(bits) < length:
        bits += PHI_BITS[:length - len(bits)]
    return int(bits, 2) & ((1 << length) - 1)
