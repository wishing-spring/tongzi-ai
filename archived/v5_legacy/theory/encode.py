# -*- coding: utf-8 -*-
"""编码器 · 连环咬合 · 底座入口"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from source_gua import SourceGua, Gua

F0 = 28  # 展开体28爻，与v3 ct 28bit对齐


class Encoder:
    """连环咬合编码器。每字符hash分散索引，咬合XOR锁语序。"""

    def __init__(self, source: SourceGua = None, layer: int = F0):
        self.source = source or SourceGua(id_bits=4, source_id=0)
        self.layer = layer
        self._prev = None
        self._map = {}

    def encode(self, text: str) -> list[Gua]:
        out = []
        for ch in text:
            g = self._draw(ch)
            if self._prev is not None:
                g = Gua(tuple(self._prev.bits[i] ^ g.bits[i]
                              for i in range(len(g.bits))))
            out.append(g)
            self._prev = g
            self._map.setdefault(ch, []).append(g)
        return out

    def _draw(self, ch: str) -> Gua:
        """字符hash → 0~(2^layer-1) → 二进制展开。每字不同卦。"""
        h = hash(ch) & 0xFFFFFFFF
        idx = h % (1 << self.layer)
        expansion = tuple((idx >> (self.layer - 1 - j)) & 1 for j in range(self.layer))
        full = self.source._id_prefix + expansion
        return Gua(full)

    def reset(self):
        self._prev = None


if __name__ == '__main__':
    enc = Encoder()
    gs = enc.encode("下雨了")
    for ch, g in zip("下雨了", gs):
        ct = sum((b << (27-i)) for i, b in enumerate(g.bits[-28:]))
        print(f"'{ch}' → ct=0x{ct:07X}")
    print(f"语序验证: A打B≠B打A: {enc.encode('A打B')[2].bits != Encoder().encode('B打A')[2].bits}")
