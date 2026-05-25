# -*- coding: utf-8 -*-
"""Express — 卦翻回字"""

from typing import List
from .gua import Gua


def express(g: Gua, natives: List[Gua]) -> str:
    """卦 → 最近原生字(同花色)。"""
    suit = g.suit
    nats = [gg for gg in natives if gg.is_native and gg.suit == suit]
    if not nats:
        return '?'
    best = min(nats, key=lambda gg: (g.ct ^ gg.ct).bit_count())
    return best.source
