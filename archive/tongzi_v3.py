# -*- coding: utf-8 -*-
"""
童子 v3.0 · 涌动池 + 生态池 · 完整实现
=========================================
灵犀涌动 → F₂等效：分组位旋转 + φ切片天气
生态池 → 碰撞生子固化剪枝，不同区域不同规则

架构:
  涌动池(永动·不生) ←→ 生态池A(快生) / 生态池B(慢生) / 生态池C(不生)
"""

import sys
sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi_constants import PHI_BITS, PHI_LEN
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from collections import Counter


# ═══════════════════════════════════════════════════
# φ 工具
# ═══════════════════════════════════════════════════

def phi_slice(start: int, n: int) -> int:
    v = 0
    for i in range(n):
        if PHI_BITS[(start + i) % PHI_LEN] == '1':
            v |= (1 << i)
    return v


# ═══════════════════════════════════════════════════
# 位旋转工具
# ═══════════════════════════════════════════════════

def rotl_group(v: int, group_start: int, group_size: int, steps: int) -> int:
    """对 v 中 [group_start:group_start+group_size] 位组循环左旋 steps 步。"""
    mask = ((1 << group_size) - 1) << group_start
    group = (v & mask) >> group_start
    k = steps % group_size
    rotated = ((group << k) | (group >> (group_size - k))) & ((1 << group_size) - 1)
    return (v & ~mask) | (rotated << group_start)


# ═══════════════════════════════════════════════════
# 四芯编码
# ═══════════════════════════════════════════════════

SUITS    = ['♥', '♦', '♣', '♠']
ID_MASK  = 0xF0000000
CT_MASK  = 0x0FFFFFFF

_PINS = [phi_slice(i * 28, 28) for i in range(16)]

def encode(ch: str, sid: int) -> int:
    cp = ord(ch)
    v = cp
    for i in range(16):
        if cp & (1 << i):
            v ^= _PINS[i]
    return (sid << 28) | (v & CT_MASK)

def suit_of(v: int) -> str:
    return SUITS[(v >> 28) & 0xF] if ((v >> 28) & 0xF) < 4 else '?'

def content(v: int) -> int:
    return v & CT_MASK


# ═══════════════════════════════════════════════════
# 涌動变换 (F₂等效灵犀八卦盘旋转)
# ═══════════════════════════════════════════════════

# 四组位旋转速率 (素数, 24h一圈映射为不同周期)
# 位[0:7]    每tick左旋1步  → LCM周期 8 tick
# 位[8:15]   每tick左旋2步  → LCM周期 4 tick
# 位[16:23]  每tick左旋3步  → LCM周期 8 tick
# 位[24:27]  每tick左旋5步  → LCM周期 4 tick
# 位[28:31]  身份位不旋转
_SURGE_GROUPS = [
    (0, 8, 1),     # 低8位, 速率1
    (8, 8, 2),     # 中低8位, 速率2
    (16, 8, 3),    # 中高8位, 速率3
    (24, 4, 5),    # 高位内容(4位身份以下), 速率5
    # 高4位(28-31) = 身份 → 不旋转
]

# 四组位旋转 — 不同花色不同速率，实现跨花色涌動
# ♥:(1,2,3,5)  ♦:(2,3,5,7)  ♣:(3,5,7,11)  ♠:(5,7,11,13)
_SURGE_RATES = {
    0: [1, 2, 3, 5],      # ♥
    1: [2, 3, 5, 7],      # ♦
    2: [3, 5, 7, 11],     # ♣
    3: [5, 7, 11, 13],    # ♠
}
_SURGE_GROUPS = [
    (0, 8),     # 低8位
    (8, 8),     # 中低8位
    (16, 8),    # 中高8位
    (24, 4),    # 高位内容(4位,身份以下)
]

def surge(v: int, tick: int) -> int:
    """涌動: 按花色分化速率。
    
    同花色 → 同速率 → ROTL保距 → 稳定匹配
    跨花色 → 不同速率 → 相对距离永动 → 持续新碰撞
    
    灵犀等效: 八卦盘24h一圈旋转。童子: 四花色不同周期错动。
    """
    phase = tick // SURGE_CYCLE
    sid = (v >> 28) & 0xF
    rates = _SURGE_RATES.get(sid, [1, 2, 3, 5])

    result = v
    for (gs, gz), rate in zip(_SURGE_GROUPS, rates):
        result = rotl_group(result, gs, gz, phase * rate)

    # φ天气 — 也按花色取不同切片
    weather = phi_slice((phase * 7 + sid * 37) % PHI_LEN, 28)
    result = (result & ID_MASK) | ((result & CT_MASK) ^ weather)

    return result


# ═══════════════════════════════════════════════════
# 卦元
# ═══════════════════════════════════════════════════

@dataclass
class Gua:
    value: int          # 32位原生卦值 (不动)
    source: str = ''    # 原始字
    is_native: bool = True
    hit_count: int = 0
    is_solid: bool = False
    energy: int = 0
    born_tick: int = 0  # 出生时刻

    @property
    def suit(self) -> str:
        return suit_of(self.value)

    @property
    def ct(self) -> int:
        return content(self.value)

    def effective(self, tick: int) -> int:
        """涌動后的有效值。"""
        return surge(self.value, tick)


# ═══════════════════════════════════════════════════
# 涌动永动池
# ═══════════════════════════════════════════════════

class SurgePool:
    """永动池。存续所有卦元的本源。不生不灭，纯涌動。"""

    def __init__(self):
        self.guas: Dict[int, Gua] = {}  # value → Gua (去重)
        self.order: List[Gua] = []      # 保持顺序

    def ingest(self, text: str):
        """喂字 → 四花色 → 入池。"""
        words = [w.strip() for w in text.split() if w.strip()]
        added = 0
        for ch in words:
            for sid in range(4):
                val = encode(ch, sid)
                if val in self.guas:
                    continue  # 已存在跳过
                g = Gua(value=val, source=ch, is_native=True)
                self.guas[val] = g
                self.order.append(g)
                added += 1
        return added

    def snapshot(self, tick: int) -> List[Gua]:
        """取当前涌動快照（不影响池内原生值）。"""
        return list(self.order)  # 生态池自己调 surge()

    def __len__(self):
        return len(self.order)

    def stats(self) -> str:
        suits_breakdown = Counter(g.suit for g in self.order)
        return (f"涌动池: {len(self.order)}卦 "
                f"{' | '.join(f'{s}{suits_breakdown[s]}' for s in SUITS)}")


# ═══════════════════════════════════════════════════
# 生态池
# ═══════════════════════════════════════════════════

F0 = 96            # 更快激活
FIT_MIN = 6
DENSITY_MAX = 48
SURGE_CYCLE = 5     # 涌動每5tick一相(灵犀24h→童子5tick微周期)

class EcoPool:
    """生态池。从涌动池拉卦，碰撞生子，子卦可回流或不回流。

    参数:
      name        — 池名
      tau         — 活性窗口（快慢节奏）
      fit_min     — 锁定阈值
      birth_rate  — 生子频率衰减系数
      flow_back   — 子卦是否回流涌动池
      density_max — 密度上限
    """

    def __init__(self, name: str, tau=5, fit_min=FIT_MIN,
                 birth_rate=1.0, flow_back=False, density_max=DENSITY_MAX):
        self.name = name
        self.tau = tau
        self.fit_min = fit_min
        self.birth_rate = birth_rate  # 1.0=正常, 0.5=减半
        self.flow_back = flow_back
        self.density_max = density_max

        self.guas: List[Gua] = []       # 池中卦
        self.births: List[Gua] = []     # 待回流的子卦
        self.tick_count: int = 0
        self.total_births: int = 0
        self.total_solid: int = 0

    def pull(self, surge_pool: SurgePool, tick: int):
        """从涌动池拉入新卦。"""
        for g in surge_pool.order:
            if g not in self.guas:
                g.energy = 0
                g.born_tick = tick
                self.guas.append(g)

    def tick(self, global_tick: int):
        """生态池一次心跳。
        
        碰撞用存储值(含涌動出生签名)，不用实时涌動。
        生子时，孩子注入当前涌動相位。
        """
        self.tick_count += 1
        self.births.clear()
        births_this_tick = []

        alive = [g for g in self.guas if not g.is_solid]

        # 1. 频率累积
        for g in alive:
            g.energy += 18 + (g.ct.bit_count() % 14)

        # 2. 碰撞 (用存储值，不生涌動变换)
        active = [g for g in alive if g.energy >= F0]
        locked_pairs = set()

        for i, a in enumerate(active):
            if a.is_solid:
                continue
            a.energy = 0

            for j, b in enumerate(active):
                if i >= j or b.is_solid:
                    continue
                pair_key = (id(a), id(b)) if id(a) < id(b) else (id(b), id(a))
                if pair_key in locked_pairs:
                    continue

                # 榫卯接触 — 用存储原值
                fit_ab = (a.ct & ~b.ct).bit_count()
                fit_ba = (b.ct & ~a.ct).bit_count()
                fit = max(fit_ab, fit_ba)

                if fit >= self.fit_min:
                    a.hit_count += 1
                    b.hit_count += 1
                    locked_pairs.add(pair_key)

                    # 生子 — 注入当前涌動相位
                    surge_a = a.effective(global_tick)
                    surge_b = b.effective(global_tick)
                    xor_ct = ((surge_a & CT_MASK) ^ (surge_b & CT_MASK)) & CT_MASK
                    and_ct = ((surge_a & CT_MASK) & (surge_b & CT_MASK)) & CT_MASK

                    child_xor = Gua(
                        value=(a.value & ID_MASK) | xor_ct,
                        source='', is_native=False,
                        energy=F0 // 2, born_tick=global_tick
                    )
                    child_and = Gua(
                        value=(b.value & ID_MASK) | and_ct,
                        source='', is_native=False,
                        energy=F0 // 2, born_tick=global_tick
                    )
                    births_this_tick.extend([child_xor, child_and])

        # 3. 子卦入池
        for child in births_this_tick:
            self.guas.append(child)
            self.total_births += 1
            if self.flow_back:
                self.births.append(child)

        # 4. 固化
        for g in self.guas:
            if not g.is_solid and g.hit_count >= 3:
                g.is_solid = True
                self.total_solid += 1

        # 5. 剪枝
        dead = []
        for g in self.guas:
            if (not g.is_native and not g.is_solid
                    and g.hit_count == 0
                    and global_tick - g.born_tick > self.tau * 4):
                dead.append(g)
        for g in dead:
            self.guas.remove(g)

        # 6. 密度控制
        non_solid = [g for g in self.guas if not g.is_solid]
        if len(non_solid) > self.density_max:
            victims = sorted(non_solid, key=lambda g: g.hit_count)
            for g in victims[:len(non_solid) - self.density_max]:
                self.guas.remove(g)

    def stats(self) -> str:
        alive = sum(1 for g in self.guas if not g.is_solid)
        solid = sum(1 for g in self.guas if g.is_solid)
        return (f"{self.name}: {len(self.guas)}卦 "
                f"(alive={alive} solid={solid} births={self.total_births})")


# ═══════════════════════════════════════════════════
# 统一系统
# ═══════════════════════════════════════════════════

class TongziV3:
    """涌动池 + 多生态池。

    surge_pool: 涌动永动池 (不生)
    eco_pools:  生态池列表 (不同规则)
    """

    def __init__(self):
        self.surge = SurgePool()
        self.eco_pools: List[EcoPool] = []
        self.global_tick: int = 0

    def add_eco(self, pool: EcoPool):
        self.eco_pools.append(pool)

    def feed(self, text: str):
        n = self.surge.ingest(text)
        return n

    def tick(self, n=1):
        for _ in range(n):
            self.global_tick += 1
            for ep in self.eco_pools:
                ep.pull(self.surge, self.global_tick)
                ep.tick(self.global_tick)

            # 子卦回流
            for ep in self.eco_pools:
                for child in ep.births:
                    if child.value not in self.surge.guas:
                        self.surge.guas[child.value] = child
                        self.surge.order.append(child)
                ep.births.clear()

    def express(self, g: Gua) -> str:
        """卦翻回字。找涌动池中同花色最近原生卦。"""
        suit = g.suit
        natives = [gg for gg in self.surge.order
                   if gg.is_native and gg.suit == suit]
        if not natives:
            return '?'
        best = min(natives, key=lambda gg: (g.ct ^ gg.ct).bit_count())
        return best.source

    def report(self) -> str:
        lines = [f"═══ 童子 v3.0 · tick={self.global_tick} ═══"]
        lines.append(self.surge.stats())
        for ep in self.eco_pools:
            lines.append(ep.stats())

        # 湧动演示
        if self.surge.order:
            g0 = self.surge.order[0]
            lines.append(f"\n涌動演示 ({g0.source}{g0.suit}):")
            for t in range(0, min(self.global_tick + 1, 6)):
                ev = surge(g0.value, t)
                lines.append(f"  t{t}: 0x{ev:08x}")

        # 吸引子
        for ep in self.eco_pools:
            solid = [g for g in ep.guas if g.is_solid]
            if solid:
                names = Counter(self.express(g) for g in solid)
                top = names.most_common(5)
                lines.append(f"\n{ep.name} 吸引子:")
                for name, cnt in top:
                    lines.append(f"  {name:4s} {'█'*cnt} {cnt}")

        return '\n'.join(lines)


# ═══════════════════════════════════════════════════
# 实验
# ═══════════════════════════════════════════════════

if __name__ == '__main__':
    tz = TongziV3()

    # 三个生态池: 快生 / 慢生 / 不生
    tz.add_eco(EcoPool("生态A·快生", tau=5, birth_rate=1.0,
                        flow_back=True, density_max=48))
    tz.add_eco(EcoPool("生态B·慢生", tau=10, birth_rate=0.6,
                        flow_back=False, density_max=32))
    tz.add_eco(EcoPool("生态C·不生", tau=999, birth_rate=0,
                        flow_back=False, density_max=16))

    # 喂入
    print("【喂入】20字")
    tz.feed("水 火 天 地 山 雷 风 泽 日 月")
    tz.feed("星 光 暗 冷 热 干 湿 动 静 空")

    # 先拉入
    for ep in tz.eco_pools:
        ep.pull(tz.surge, 0)

    # 跑
    print("\n【运行】")
    for _ in range(100):
        tz.tick()
        if tz.global_tick in [10, 25, 50, 75, 100]:
            al = sum(len(ep.guas) for ep in tz.eco_pools)
            sl = sum(sum(1 for g in ep.guas if g.is_solid)
                     for ep in tz.eco_pools)
            br = sum(ep.total_births for ep in tz.eco_pools)
            print(f"  t{tz.global_tick:03d}: total={al} solid={sl} "
                  f"births={br} surge={len(tz.surge.order)}")

    print("\n" + tz.report())
