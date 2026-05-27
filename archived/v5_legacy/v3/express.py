# -*- coding: utf-8 -*-
"""Express — map a gua back to its nearest native character.

Finds the native gua (same suit) with minimum Hamming distance
and returns its source character. This is how the system "speaks":
it expresses the current attractor by naming the closest remembered word.
"""

from typing import List
from .gua import Gua


def express(g: Gua, natives: List[Gua]) -> str:
    """Map a gua to the nearest native gua's source character (same suit)."""
    suit = g.suit
    nats = [gg for gg in natives if gg.is_native and gg.suit == suit]
    if not nats:
        return '?'
    best = min(nats, key=lambda gg: (g.ct ^ gg.ct).bit_count())
    return best.source
