# -*- coding: utf-8 -*-
"""卦元 — 四芯身份 + 弹珠内容"""

from dataclasses import dataclass
from .encode import suit_of, content
from .surge import surge


@dataclass
class Gua:
    """F₂ 空间卦元。共享不可变值，池本地状态外部管理。"""
    value: int
    source: str = ''
    is_native: bool = True
    born_tick: int = 0

    @property
    def suit(self) -> str:      return suit_of(self.value)
    @property
    def ct(self) -> int:        return content(self.value)

    def effective(self, tick: int) -> int:
        return surge(self.value, tick)
