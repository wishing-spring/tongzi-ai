# Copyright (c) 2026 Tongzi Project (wishing-spring)
# Licensed under the MIT License. See LICENSE file for details.
"""
童子 · 第3组 · 工坊
=====================
积木装配台。卦爻只管存在, 不被管理。

快捷入口:
  block(text)        造一块积木
  batch(texts)       批量造积木
  map(blocks)        看积木图

底层:
  tongzi_kernel.py      — 卦爻 (0 和 1)
  tools/axioms.py        — 公理 + 八运算
  tools/encode.py        — 编解码
  tools/blocks.py        — 拼装 (Block/chain/ring/mesh...)
"""

from __future__ import annotations
from typing import List
from tongzi_kernel import Gua, generate_gua
from tongzi_constants import VEC_DIM
from tools.encode import encode as _encode, batch_encode as _batch_encode
from tools.blocks import (
    Block, link, unlink, chain, ring, mesh,
    cluster, orbit_from, stretch_to, view, graph
)


# ============================================================
# 入口
# ============================================================

def block(text: str) -> Block:
    """文本 → 卦 → 积木。"""
    g = _encode(text)
    return Block(g, text)


def batch(texts: List[str], anchor: int = 0) -> List[Block]:
    """批量造积木: 同锚点 XOR 微扰, 批内汉明=2。"""
    guas = _batch_encode(texts, anchor)
    return [Block(g, t) for g, t in zip(guas, texts)]


def map(blocks: List[Block]) -> str:
    """看积木图。"""
    return graph(blocks)
