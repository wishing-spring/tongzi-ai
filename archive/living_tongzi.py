# -*- coding: utf-8 -*-
"""
活童子 · 蚯蚓实验
==================
v1.2的六个零件 + v2.3的弹珠编码 + 四芯身份 = 活的

零件:
  频率控制 — 每个卦自己蓄能，有快有慢
  tick 驱动 — 系统自己推进，不等人喂
  合并生子 — 碰撞生XOR子+AND子
  密度自疏散 — 太挤了自己散
  固化 — 常碰的锁住
  express — 卦翻回字
"""

import sys
sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi_constants import PHI_BITS, PHI_LEN
from dataclasses import dataclass, field
from typing import List, Optional

# ============================================================
# φ 工具
# ============================================================

def phi_slice(start: int, n: int) -> int:
    v = 0
    for i in range(n):
        if PHI_BITS[(start + i) % PHI_LEN] == '1':
            v |= (1 << i)
    return v

# ============================================================
# 四芯
# ============================================================

SUITS    = ['♥', '♦', '♣', '♠']
ID_MASK  = 0xF0000000
CT_MASK  = 0x0FFFFFFF

_PINS = [phi_slice(i * 28, 28) for i in range(16)]

def _pinball(cp: int) -> int:
    v = cp
    for i in range(16):
        if cp & (1 << i):
            v ^= _PINS[i]
    return v & CT_MASK

def encode(ch: str, sid: int) -> int:
    """一字→带花色身份的32位卦。"""
    return (sid << 28) | _pinball(ord(ch))

def suit_of(v: int) -> str:
    return SUITS[(v >> 28) & 0xF]

def content_of(v: int) -> int:
    return v & CT_MASK

# ============================================================
# 卦
# ============================================================

F0 = 256           # 基础能量阈值
SOLID_HIT = 3      # 碰撞几次才固化
DENSITY_MAX = 64   # 池子上限

@dataclass
class Gua:
    value: int          # 32位卦值
    source: str = ''    # 原始字
    is_native: bool = True  # 原生(喂入) vs 子卦(碰撞生)
    energy: int = 0
    hit_count: int = 0
    is_solid: bool = False
    core: int = 0        # 固化内核
    alive: bool = True

    @property
    def suit(self) -> str:
        return suit_of(self.value)

    @property
    def content(self) -> int:
        return content_of(self.value)

    def express_name(self, pool: List['Gua']) -> str:
        """找同花色最近原生卦 → 用其源字命名。"""
        my_suit = self.suit
        native = [g for g in pool if g.is_native and g.suit == my_suit]
        if not native:
            return '?'
        best = min(native, key=lambda g: (self.content ^ g.content).bit_count())
        return best.source


# ============================================================
# 池子 — 活的
# ============================================================

class Pool:
    """活池。tick驱动，频率内生。"""

    def __init__(self):
        self.guas: List[Gua] = []
        self.tick_count: int = 0
        self.log: List[str] = []

    # ── 喂入 ──

    def feed(self, text: str):
        words = [w.strip() for w in text.split() if w.strip()]
        for ch in words:
            for sid in range(4):
                val = encode(ch, sid)
                g = Gua(value=val, source=ch, is_native=True,
                        energy=sid * 16)  # 四花色错峰启动
                self.guas.append(g)
        self.log.append(f"[feed] +{len(words)*4} cards ({len(words)}字×4芯)")

    # ── tick — 心跳 ──

    def tick(self):
        self.tick_count += 1
        births = []
        deaths = []

        alive = [g for g in self.guas if g.alive]

        # 1. 频率累积
        for g in alive:
            if not g.is_solid:
                g.energy += 12 + (g.value.bit_count() % 8)  # 密度决定速率

        # 2. 碰撞
        active = [g for g in alive if g.energy >= F0 and not g.is_solid]
        locked_pairs = []

        for i, a in enumerate(active):
            if not a.alive:
                continue
            a.energy = 0  # 释放
            for j, b in enumerate(active):
                if i >= j or not b.alive:
                    continue
                # 榫卯接触（只看内容位，跨芯兼容）
                fit_ab = (a.content & ~b.content).bit_count()
                fit_ba = (b.content & ~a.content).bit_count()
                fit = max(fit_ab, fit_ba)
                if fit >= 6:  # FIT_MIN for 28-bit
                    a.hit_count += 1
                    b.hit_count += 1
                    locked_pairs.append((a, b, fit))

        # 3. 生子
        locked_this_tick = set()
        for a, b, _ in locked_pairs:
            pair_key = (id(a), id(b)) if id(a) < id(b) else (id(b), id(a))
            if pair_key in locked_this_tick:
                continue
            locked_this_tick.add(pair_key)

            # XOR 子 + AND 子，各占一半父母花色
            xor_val = ((a.value & 0x0FFFFFFF) ^ (b.value & 0x0FFFFFFF)) & 0x0FFFFFFF
            and_val = ((a.value & 0x0FFFFFFF) & (b.value & 0x0FFFFFFF)) & 0x0FFFFFFF

            # XOR子带a的花色，AND子带b的花色
            child_xor = Gua(value=(a.value & 0xF0000000) | xor_val,
                            source='', is_native=False, energy=F0//2)
            child_and = Gua(value=(b.value & 0xF0000000) | and_val,
                            source='', is_native=False, energy=F0//2)
            births.extend([child_xor, child_and])

        # 4. 固化
        for g in alive:
            if not g.is_solid and g.hit_count >= SOLID_HIT:
                g.is_solid = True
                g.core = g.value & 0xF0000000  # 高位固化为身份

        # 5. 剪枝（长期未碰、非固化、非原生，能量枯竭）
        for g in alive:
            if (not g.is_native and not g.is_solid
                    and g.hit_count == 0 and g.energy > F0 * 5):
                g.alive = False
                deaths.append(g)

        # 6. 入池 + 固化老化（固化的归入历史，不占活池位置）
        for g in births:
            self.guas.append(g)

        # 7. 密度控制
        alive_now = [g for g in self.guas if g.alive and not g.is_solid]
        if len(alive_now) > DENSITY_MAX:
            victims = sorted(alive_now, key=lambda g: g.hit_count)
            for g in victims[:len(alive_now) - DENSITY_MAX]:
                g.alive = False
                deaths.append(g)

        n_alive = sum(1 for g in self.guas if g.alive)
        n_solid = sum(1 for g in self.guas if g.is_solid)
        self.log.append(
            f"[t{self.tick_count:03d}] alive={n_alive} solid={n_solid} "
            f"+{len(births)}birth -{len(deaths)}dead"
        )

    # ── express ──

    def express(self, g: Gua) -> str:
        return g.express_name(self.guas)

    # ── 报告 ──

    def report(self) -> str:
        lines = []
        lines.append(f"=== 活池 · tick={self.tick_count} ===")
        alive = [g for g in self.guas if g.alive]
        solid = [g for g in self.guas if g.is_solid]
        lines.append(f"存活: {len(alive)}  固化: {len(solid)}")

        # 按花色分组
        for sid, suit in enumerate(SUITS):
            ss = [g for g in self.guas if suit_of(g.value) == suit]
            if ss:
                lines.append(f"\n芯{suit}: {len(ss)}卦")
                for g in sorted(ss, key=lambda x: -x.hit_count)[:6]:
                    name = self.express(g)
                    tag = "[固]" if g.is_solid else "[活]"
                    src = f"←{g.source}" if g.source else "(子)"
                    lines.append(
                        f"  {tag} {name:4s} {src:6s} "
                        f"e={g.energy:3d} hit={g.hit_count} "
                        f"val=0x{g.value:08x}"
                    )

        # 最近日志
        lines.append(f"\n--- 最近10条日志 ---")
        for L in self.log[-10:]:
            lines.append(f"  {L}")

        return '\n'.join(lines)


# ============================================================
# 实验
# ============================================================

if __name__ == '__main__':
    pool = Pool()

    print("【喂入】20字 × 4芯 = 80卦")
    pool.feed("水 火 天 地 山 雷 风 泽 日 月 星 光 暗 冷 热 干 湿 动 静 空")

    print("\n【200 tick】")
    checkpoints = [10, 30, 50, 100, 150, 200]
    for _ in range(200):
        pool.tick()
        if pool.tick_count in checkpoints:
            al = sum(1 for g in pool.guas if g.alive)
            sl = sum(1 for g in pool.guas if g.is_solid)
            kids = sum(1 for g in pool.guas if not g.is_native)
            print(f"  t{pool.tick_count:03d}: alive={al} solid={sl} "
                  f"children={kids} total={len(pool.guas)}")

    print("\n" + pool.report())

    # 吸引子分析
    print("\n=== 吸引子分析 ===")
    from collections import Counter
    for sid, suit in enumerate(SUITS):
        ss = [g for g in pool.guas if g.is_solid and g.suit == suit]
        names = [g.express_name(pool.guas) for g in ss]
        top = Counter(names).most_common(5)
        print(f"\n芯{suit} 固化 {len(ss)}卦，top5吸引子:")
        for name, cnt in top:
            bar = '█' * cnt
            print(f"  {name:4s} {bar} {cnt}")
