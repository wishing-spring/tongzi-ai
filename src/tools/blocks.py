# Copyright (c) 2026 Tongzi Project (wishing-spring)
# Licensed under the MIT License. See LICENSE file for details.
"""
工具 · 积木拼装
=================
卦与卦之间的结构操作: 链接、串链、成环、织网、聚类、变形。

使用:
  from tools.blocks import Block, chain, ring, mesh, link
  a, b = Block(gua_a), Block(gua_b)
  chain([a, b, c])
"""

from __future__ import annotations
from typing import List, Dict, Set
from tools.axioms import hamming, orbit as orbit_fn, stretch as stretch_fn
from tongzi_kernel import Gua


class Block:
    """积木: 卦元加邻接表, 不依赖 Space。"""

    __slots__ = ('gua', 'name', 'links')

    def __init__(self, gua: Gua, name: str = ""):
        self.gua   = gua
        self.name  = name
        self.links: Dict[Block, int] = {}

    def __repr__(self):
        n = len(self.links)
        return f"[{self.name}]({n})" if self.name else f"[{self.gua.value:04X}]({n})"

    def distance_to(self, other: Block) -> int:
        return hamming(self.gua.value, other.gua.value)


def link(a: Block, b: Block) -> int:
    """双向链接, 返回汉明距离。"""
    d = a.distance_to(b)
    a.links[b] = d
    b.links[a] = d
    return d


def unlink(a: Block, b: Block):
    """断开链接。"""
    a.links.pop(b, None)
    b.links.pop(a, None)


def chain(blocks: List[Block]) -> List[Block]:
    """串链: 依次两两相连。"""
    for i in range(len(blocks) - 1):
        link(blocks[i], blocks[i + 1])
    return blocks


def ring(blocks: List[Block]) -> List[Block]:
    """串环: 链 + 首尾闭合。"""
    chain(blocks)
    if len(blocks) >= 2:
        link(blocks[-1], blocks[0])
    return blocks


def mesh(blocks: List[Block], radius: int = 4) -> List[Block]:
    """织网: 汉明半径内全互连。"""
    n = len(blocks)
    for i in range(n):
        for j in range(i + 1, n):
            d = blocks[i].distance_to(blocks[j])
            if d <= radius:
                link(blocks[i], blocks[j])
    return blocks


def cluster(blocks: List[Block], radius: int = 3
            ) -> List[List[Block]]:
    """聚类: BFS 按汉明距离分簇。"""
    visited: Set[Block] = set()
    clusters: List[List[Block]] = []

    for b in blocks:
        if b in visited:
            continue
        group: List[Block] = []
        queue = [b]
        visited.add(b)
        while queue:
            cur = queue.pop(0)
            group.append(cur)
            for other in blocks:
                if other not in visited and cur.distance_to(other) <= radius:
                    visited.add(other)
                    queue.append(other)
        clusters.append(group)
    return clusters


def orbit_from(block: Block, center: Block, step: int = 1) -> Block:
    """绕 center 旋转。返回新积木 (不入册)。"""
    v = orbit_fn(block.gua.value, center.gua.value, step)
    name = f"{block.name}@{center.name}{step}"
    return Block(Gua(v), name)


def stretch_to(block: Block, target: Block, lam: int) -> Block:
    """向 target 拉伸。返回新积木 (不入册)。"""
    v = stretch_fn(block.gua.value, target.gua.value, lam)
    name = f"{block.name}>{target.name}{lam}"
    return Block(Gua(v), name)


def view(block: Block) -> str:
    """看一块积木。"""
    lines = [
        f"积木: {block.name}",
        f"卦值: {block.gua.value:016b} ({block.gua.value:04X})",
        f"邻接: {len(block.links)} 块",
    ]
    if block.links:
        for other, d in sorted(block.links.items(), key=lambda x: x[1])[:8]:
            lines.append(f"  -- d={d:2d} -- {other.name}")
    return "\n".join(lines)


def graph(blocks: List[Block]) -> str:
    """看全图统计。"""
    if not blocks:
        return "空图"
    degs = [len(b.links) for b in blocks]
    dists = [d for b in blocks for d in b.links.values()]
    lines = [
        f"积木图: {len(blocks)} 块",
        f"度数: min={min(degs)} max={max(degs)} avg={sum(degs)/len(degs):.1f}",
    ]
    if dists:
        lines.append(f"距离: min={min(dists)} max={max(dists)} avg={sum(dists)/len(dists):.1f}")
    cl = cluster(blocks, 3)
    lines.append(f"聚类(r=3): {len(cl)} 簇")
    for i, c in enumerate(cl):
        names = [b.name for b in c]
        lines.append(f"  簇{i}: {', '.join(names[:5])}{'...' if len(names)>5 else ''} ({len(c)}块)")
    return "\n".join(lines)
