# -*- coding: utf-8 -*-
"""Gua — An F₂ point with suit identity + pinball content.

A Gua is the fundamental unit of Tongzi. It is an immutable 32-bit value:
   bits 28-31: suit ID (♥♦♣♠)
   bits 0-27:  28-bit content (F₂ vector)
"""

from dataclasses import dataclass
from .encode import suit_of, content
from .surge import surge


@dataclass
class Gua:
    """F₂ space gua. Value is immutable; pool-local state is managed externally."""
    value: int
    source: str = ''         # original Chinese character (for express())
    is_native: bool = True   # True = direct encoding, False = collision-born
    born_tick: int = 0

    @property
    def suit(self) -> str:
        """Suit symbol (♥♦♣♠) derived from high 4 bits."""
        return suit_of(self.value)

    @property
    def ct(self) -> int:
        """28-bit F₂ content (suit bits stripped)."""
        return content(self.value)

    def effective(self, tick: int) -> int:
        """Effective value at a given tick, with surge window applied."""
        return surge(self.value, tick)
