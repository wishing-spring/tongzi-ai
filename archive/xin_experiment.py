# Copyright (c) 2026 Tongzi Project (wishing-spring)
# Licensed under the MIT License. See LICENSE file for details.
"""
四芯身份系统 · 扑克花色
===========================
♥ ♦ ♣ ♠ — 四副花色。同字同内容，不同花色。

每卦 32 位:
  高 4 位 = 芯身份 (0-3 → ♥♦♣♠)
  低 28 位 = 弹珠内容 (所有芯共享同一套 φ 柱阵)

扑克牌类比:
  7♥ 和 7♦ 不同张牌，但都是"7"
  跨花色比内容(不看花色)，同花色比全卦
  
用法:
  >>> factory = CardFactory()
  >>> cards = factory.deal("水 火 天 地")  # 每字发四张
"""

import sys
sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi_kernel import Gua, FULL_MASK
from tongzi_constants import PHI_BITS, PHI_LEN
from dataclasses import dataclass, field
from typing import List, Optional, Dict


# ============================================================
# φ 切片 → 弹珠柱阵
# ============================================================

def phi_slice(start: int, n_bits: int) -> int:
    result = 0
    for i in range(n_bits):
        if PHI_BITS[(start + i) % PHI_LEN] == '1':
            result |= (1 << i)
    return result


def phi_pins(start: int, n_pins: int = 16) -> List[int]:
    """16根弹珠柱，每根28位（给身份留4位）。"""
    return [phi_slice(start + i * 28, 28) for i in range(n_pins)]


# ============================================================
# 芯定义
# ============================================================

SUITS    = ['♥', '♦', '♣', '♠']
ID_MASK  = 0xF << 28       # 高4位 = 芯身份
CONT_MASK = 0x0FFFFFFF      # 低28位 = 内容

# ──── 共用的弹珠柱阵（从 φ[0] 切）────
_SHARED_PINS = phi_pins(0, 16)


def _pinball_28(cp: int) -> int:
    """弹珠编码 → 28位内容。"""
    v = cp
    for i in range(16):
        if cp & (1 << i):
            v ^= _SHARED_PINS[i]
    # 28位镜像填充
    return (v & CONT_MASK)


def encode(ch: str, suit_id: int) -> Gua:
    """一字 + 花色 → 带身份的卦元。

    身份高4位，内容低28位。同字不同花色 → 内容同，卦不同。
    """
    content = _pinball_28(ord(ch))
    value = (suit_id << 28) | content
    return Gua(value)


def suit_of(g: Gua) -> str:
    """从卦读花色。"""
    sid = (g.value >> 28) & 0xF
    return SUITS[sid] if sid < 4 else '?'


def content_of(g: Gua) -> int:
    """剥身份取内容。"""
    return g.value & CONT_MASK


# ============================================================
# 牌
# ============================================================

@dataclass
class Card:
    """桌上一张牌。"""
    ch: str          # 字
    suit: str        # ♥♦♣♠
    sid: int         # 0-3
    gua: Gua         # 带身份的卦

    @property
    def name(self) -> str:
        return f"{self.ch}{self.suit}"

    @property
    def content(self) -> int:
        return self.gua.value & CONT_MASK


# ============================================================
# 发牌器
# ============================================================

class CardFactory:
    """一字→四花色→四张牌。"""

    def deal(self, text: str) -> List[Card]:
        cards = []
        words = [w.strip() for w in text.split() if w.strip()]
        for ch in words:
            for sid, suit in enumerate(SUITS):
                g = encode(ch, sid)
                cards.append(Card(ch, suit, sid, g))
        return cards


# ============================================================
# 碰撞分析
# ============================================================

@dataclass
class Hit:
    a: Card; b: Card
    fit: int          # 榫卯接触位数
    locked: bool      # 是否达阈值
    same_ch: bool     # 同字？
    same_suit: bool   # 同花色？
    match_type: str   # 'same_word'|'cross_suit'|'different'

FIT_MIN = 6  # 28位空间阈值

class Analyzer:
    """桌面碰撞分析。"""

    def __init__(self, fit_min=FIT_MIN):
        self.fit_min = fit_min
        self.hits: List[Hit] = []

    def analyze(self, cards: List[Card]) -> str:
        self.hits.clear()
        n = len(cards)

        for i in range(n):
            for j in range(i+1, n):
                a, b = cards[i], cards[j]
                # 榫卯：a的凸插入b的凹
                f1 = (a.gua.value & ~b.gua.value).bit_count()
                f2 = (b.gua.value & ~a.gua.value).bit_count()
                fit = max(f1, f2)

                same_ch = (a.ch == b.ch)
                same_suit = (a.suit == b.suit)

                if same_ch and not same_suit:
                    mtype = 'same_word'     # 同字跨花色
                elif same_suit:
                    mtype = 'same_suit'     # 同花色异字
                else:
                    mtype = 'cross'         # 异字异花色

                self.hits.append(Hit(
                    a=a, b=b, fit=fit,
                    locked=fit >= self.fit_min,
                    same_ch=same_ch,
                    same_suit=same_suit,
                    match_type=mtype
                ))

        return self._report(cards)

    def _report(self, cards: List[Card]) -> str:
        lines = []
        lines.append("═" * 56)
        lines.append("四芯身份 · 扑克花色系统 · 分析报告")
        lines.append("═" * 56)

        # ── 身份唯一性 ──
        words = sorted(set(c.ch for c in cards))
        lines.append("\n[身份唯一性] 同字四花色 → 四张牌，身份全不同:")
        for w in words:
            cc = [c for c in cards if c.ch == w]
            gua_vals = sorted(set(hex(c.gua.value) for c in cc))
            suits = ''.join(c.suit for c in sorted(cc, key=lambda c: c.sid))
            all_diff = len(gua_vals) == 4
            tag = "OK" if all_diff else "FAIL"
            lines.append(f"  [{tag}] {w} → {suits}  卦值: {' / '.join(gua_vals)}")

        # ── 内容一致性 ──
        lines.append("\n[内容一致性] 同字跨花色，低28位内容应该相同:")
        for w in words:
            cc = [c for c in cards if c.ch == w]
            contents = set(c.content for c in cc)
            same = len(contents) == 1
            tag = "OK" if same else f"{len(contents)}种"
            lines.append(f"  [{tag}] {w}")

        # ── 同字跨花色碰撞 ──
        same_word = [h for h in self.hits if h.match_type == 'same_word']
        lines.append(f"\n[同字跨花色] {len(same_word)}对，应全部锁定:")
        for h in same_word[:8]:
            ok = "YES" if h.locked else "NO"
            lines.append(f"  [{ok}] {h.a.name}↔{h.b.name}  {h.fit}位")

        # ── 同花色异字 ──
        for suit in SUITS:
            ss = [h for h in self.hits 
                  if h.match_type == 'same_suit' and h.a.suit == suit]
            if ss:
                lines.append(f"\n[芯{suit}] {len(ss)}对同花色碰撞:")
                for h in sorted(ss, key=lambda x: -x.fit)[:6]:
                    ok = "锁" if h.locked else "  "
                    lines.append(f"  [{ok}] {h.a.ch}↔{h.b.ch}  {h.fit}位")

        # ── 汇总 ──
        total = len(self.hits)
        locked = sum(1 for h in self.hits if h.locked)
        lines.append(f"\n[汇总] {len(cards)}牌 {total}对碰撞 {locked}锁定 "
                     f"(阈值{self.fit_min}位)")

        # ── 语义验证 ──
        lines.append("\n[语义对验证]")
        pairs = [('水','河'), ('爱','恨'), ('火','水'), ('一','二'), ('天','地')]
        for a, b in pairs:
            # 找同花色碰撞
            for suit in SUITS:
                hits_ab = [h for h in self.hits 
                          if h.a.ch == a and h.b.ch == b 
                          and h.a.suit == suit and h.b.suit == suit]
                if hits_ab:
                    h = hits_ab[0]
                    lines.append(f"  {a}{suit}↔{b}{suit}  {h.fit}位  {'锁' if h.locked else '未锁'}")

        return '\n'.join(lines)


# ============================================================
# 测试
# ============================================================

if __name__ == '__main__':
    factory = CardFactory()
    analyzer = Analyzer()

    # 小测试
    cards = factory.deal("水 火 天 地 爱 恨 一 二 河")
    print(analyzer.analyze(cards))
