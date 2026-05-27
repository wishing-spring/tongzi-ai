# -*- coding: utf-8 -*-
"""卦元生成器 · 爻层递进 · 每层多一爻 · 可稳定复现"""

import hashlib


class Yao:
    """1 yao = 1 F₂ bit"""
    __slots__ = ('bit',)
    def __init__(self, bit: int):
        self.bit = bit & 1
    def __repr__(self):
        return '⚊' if self.bit else '⚋'
    def __xor__(self, other):
        return Yao(self.bit ^ other.bit)


class Gua:
    """N yao = N-bit F₂ vector"""
    __slots__ = ('yaos', '_hash')
    def __init__(self, yaos):
        self.yaos = tuple(yaos)
        self._hash = None
    @property
    def n(self): return len(self.yaos)
    @property
    def bits(self): return tuple(y.bit for y in self.yaos)
    @property
    def bits_int(self):
        v = 0
        for y in self.yaos:
            v = (v << 1) | y.bit
        return v
    def __repr__(self):
        return ''.join(str(y) for y in self.yaos)
    def __hash__(self):
        if self._hash is None:
            self._hash = hash(self.bits)
        return self._hash
    def __eq__(self, other):
        return self.bits == other.bits
    def xor_with(self, other):
        return Gua([Yao(a.bit ^ b.bit) for a, b in zip(self.yaos, other.yaos)])


class GuaGenerator:
    """Layer-based gua generation.

    Layer k has gua with k yao each.
    Each gua derived from a parent in layer k-1 by appending one yao.
    φ-perturbation ensures every gua within a layer is unique.

    When a gua is drawn (consumed), an identical twin is cloned back,
    maintaining the pool size and structural continuity.
    """

    def __init__(self, max_layers=28):
        self.max_layers = max_layers
        self._pools = {}          # layer -> set of Gua
        self._parent = {}         # child_gua -> parent_gua
        self._twins = {}          # consumed_gua -> replacement_gua

    def generate_layer(self, k: int):
        """Generate layer k (gua with k yao). k=1 is root layer."""
        if k in self._pools:
            return
        if k == 1:
            self._pools[1] = {Gua([Yao(0)]), Gua([Yao(1)])}
            return
        if k - 1 not in self._pools:
            self.generate_layer(k - 1)

        pool = []
        for parent in self._pools[k - 1]:
            g0 = Gua(parent.yaos + (Yao(0),))
            g1 = Gua(parent.yaos + (Yao(1),))
            pool.append(g0)
            pool.append(g1)
            self._parent[g0] = parent
            self._parent[g1] = parent
        self._pools[k] = pool

    def _perturb(self, gua: Gua, layer: int, idx: int) -> Gua:
        """Deterministic subtle variation. Every 7th gua gets a yao flipped
        at position idx%layer, preserving overall structure."""
        if idx % 7 == 0:
            pos = idx % len(gua.yaos)
            bits = list(gua.yaos)
            bits[pos] = Yao(bits[pos].bit ^ 1)
            return Gua(tuple(bits))
        return gua

    def draw(self, layer: int) -> Gua:
        """Draw a gua from layer. Auto-clones twin replacement."""
        if layer not in self._pools:
            self.generate_layer(layer)
        g = self._pools[layer].pop(0)
        twin = Gua(g.yaos)
        self._twins[g] = twin
        self._pools[layer].append(twin)
        return g

    def lineage(self, gua: Gua) -> list:
        """Trace from gua back to root layer."""
        line = [gua]
        while gua in self._parent:
            gua = self._parent[gua]
            line.append(gua)
        return line[::-1]

    def pool_size(self, layer: int) -> int:
        if layer in self._pools:
            return len(self._pools[layer])
        return 0


if __name__ == '__main__':
    gen = GuaGenerator(max_layers=28)
    for L in [1, 2, 3]:
        gen.generate_layer(L)
        guas = sorted(gen._pools[L], key=lambda g: g.bits_int)
        print(f"Layer {L} ({len(guas)} gua, {L} yao):")
        for g in guas:
            p = gen._parent.get(g, None)
            ps = f" <- {p}" if p else " <- root"
            print(f"  {g}{ps}")
        print()

    g = gen.draw(2)
    print(f"draw: {g}")
    print(f"pool layer 2 after draw: {gen.pool_size(2)}")
    print(f"lineage: {' -> '.join(str(x) for x in gen.lineage(g))}")
