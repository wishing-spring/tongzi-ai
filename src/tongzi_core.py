"""
童子 · 极简群域架构 · 内核
===============================
F₂ⁿ 空间 + φ 母体卦群 + 群运算内生法则。

组成:
  Gua    — F₂ 空间中的一个卦（位向量 + 出生身份）
  Space  — 卦群容器 + 节律驱动

不包含: 浮点、矩阵、梯度、词嵌入、注意力、自回归、外部时钟。
"""
from tongzi_constants import VEC_DIM, FULL_MASK, PHI_BITS, PHI_LEN
from typing import Optional, List, Tuple
import json
import os

# ============================================================
# 纯函数 — 位运算（四条公理衍出）
# ============================================================

def bit_count(v: int) -> int:
    """汉明权重"""
    return v.bit_count()

def hamming(a: int, b: int) -> int:
    """汉明距离 (公理 3)"""
    return bit_count(a ^ b)

def rotate_left(v: int, k: int) -> int:
    """位循环左旋 (公理 4 基础)"""
    k = k % VEC_DIM
    return ((v << k) | (v >> (VEC_DIM - k))) & FULL_MASK

def rotate_right(v: int, k: int) -> int:
    """位循环右旋"""
    k = k % VEC_DIM
    return ((v >> k) | (v << (VEC_DIM - k))) & FULL_MASK

# ============================================================
# Gua — F₂ 空间中的一个卦
# ============================================================

class Gua:
    """F₂ 空间中的卦元。自带出生身份，不依赖外部数据库。"""

    __slots__ = ('value', 'pos', 'length', 'id_t', 'id_l',
                 'mask', 'is_solid', 'core', 'hit_count',
                 'energy', 'lambda_base')

    def __init__(self, value: int, pos: int, length: int):
        self.value = value & ((1 << length) - 1)
        self.pos = pos           # φ 中的出生位置
        self.length = length     # 取位长度 (= 爻数)

        # 身份证 — 从 φ 位置推导，不存数据库
        self.id_t = pos          # 出生序号
        self.id_l = length       # 层编码

        # 固化
        self.is_solid = False    # 是否已固化
        self.core = 0            # 固化内核（锁定后 = value & mask）
        self.mask = self._derive_mask()

        # 运行时
        self.hit_count = 0       # 累计碰撞次数
        self.energy = 0          # 能量累积（用于频控）
        self.lambda_base = 0     # 伸缩基数（运行时从 id_l 推导）

    def _derive_mask(self) -> int:
        """从 id_l 推导固化掩码。内核段 = 高 id_l 位。"""
        if self.id_l <= 0:
            return 0
        core_bits = self.id_l
        if core_bits > VEC_DIM:
            core_bits = VEC_DIM
        return ((1 << core_bits) - 1) << (VEC_DIM - core_bits)

    @property
    def moving_bits(self) -> int:
        """参与运算的游动位（固化后内核不参与）"""
        if self.is_solid:
            return self.value & ~self.mask
        return self.value & FULL_MASK

    # ===== 核心运算 =====

    def collide(self, other: 'Gua') -> Tuple[int, int]:
        """碰撞：产出差异向量和共识向量 (⊕, ∧)"""
        a = self.moving_bits
        b = other.moving_bits
        return (a ^ b, a & b)

    def orbit(self, center: int, k: int) -> int:
        """绕心盘旋：绕 center 在等距球面上旋转 k 步"""
        diff = (self.moving_bits ^ center) & FULL_MASK
        rotated = rotate_left(diff, k)
        return (rotated ^ center) & FULL_MASK

    def stretch(self, center: int, lam: int) -> int:
        """径向伸缩：λ∈{0,1} 控制伸缩"""
        delta = (self.moving_bits ^ center) & FULL_MASK
        if lam == 0:
            return self.moving_bits
        return (self.moving_bits ^ delta) & FULL_MASK

    def solidify(self):
        """固化：锁定内核段，永不再变"""
        if not self.is_solid:
            self.core = self.value & self.mask
            self.is_solid = True

    def weakly_unlock(self, bit: int):
        """同源弱解禁：仅前驱/后继可微调单个固化位"""
        if self.is_solid:
            self.value ^= (1 << bit)

    def __repr__(self):
        solid = 'S' if self.is_solid else '-'
        return f"Gua({self.value:016b}|t={self.id_t},l={self.id_l}{solid})"


# ============================================================
# Space — 卦群容器 + 内生节律
# ============================================================

STATE_FILE = os.path.join(os.path.dirname(__file__), '.tongzi_state.json')

class Space:
    """F₂ⁿ 离散群域空间。所有卦在此共存、碰撞、演化。"""

    F0 = 256  # 基础频次（能量阈值，越大越慢）

    def __init__(self):
        self.guas: List[Gua] = []     # 卦群
        self.tick_count: int = 0      # 节律计数
        self._max_id_l: int = 0       # 当前最大层编码（运行时更新）

    # ===== φ 编码 =====

    @staticmethod
    def encode(text: str) -> Tuple[int, int]:
        """
        φ-卦编码：文本→φ 二进制流位置→取 VEC_DIM 位。
        返回 (value, pos)。pos 即 id_t。
        """
        seed = 0
        for i, c in enumerate(text):
            seed ^= ord(c) << (i * 7 % 32)
        seed = seed & 0x7FFFFFFF

        pos = seed % PHI_LEN
        bits = []
        for i in range(VEC_DIM):
            idx = (pos + i) % PHI_LEN
            bits.append(PHI_BITS[idx])
        value = int(''.join(bits), 2)
        return value, pos

    # ===== 卦管理 =====

    def ingest(self, text: str) -> Gua:
        """摄入文本，生成新卦"""
        value, pos = self.encode(text)
        g = Gua(value, pos, VEC_DIM)

        if g.id_l > self._max_id_l:
            self._max_id_l = g.id_l

        g.lambda_base = self._derive_lambda_base(g.id_l)
        self.guas.append(g)
        return g

    def _derive_lambda_base(self, id_l: int) -> int:
        """λ 基数从层编码推导。深层卦 λ 大（更散）。"""
        if self._max_id_l <= 0:
            return 0
        ratio = id_l / self._max_id_l
        return int(ratio * (VEC_DIM // 2))

    # ===== 内生频控（能量累积制）=====

    def f1(self, gua: Gua) -> int:
        """顺位频控：f₁ = F0/(1+id_t)。早生高频率"""
        return self.F0 // (1 + gua.id_t)

    def f2(self, gua: Gua) -> int:
        """层差频控：f₂ = F0/(1+id_l)。低层密交互"""
        return self.F0 // (1 + gua.id_l)

    def _rate(self, gua: Gua) -> int:
        """组合速率 = min(f₁, f₂)。取两频控的较慢者"""
        return min(self.f1(gua), self.f2(gua))

    def should_participate(self, gua: Gua) -> bool:
        """
        能量累积制：每 tick 累积速率，满 F0 触发放电。
        早生卦速率高 → 频繁触发；晚生卦速率低 → 稀疏触发。
        """
        if gua.is_solid:
            return False  # 固化卦不参与碰撞
        gua.energy += self._rate(gua)
        if gua.energy >= self.F0:
            gua.energy -= self.F0
            return True
        return False

    # ===== 空间自感知 =====

    def local_density(self, gua: Gua, radius: int = 3) -> float:
        """局部疏密感知 S(x) = N / (d̄_H + 1)"""
        neighbors = []
        for other in self.guas:
            if other is gua:
                continue
            if other.id_l != gua.id_l:
                continue
            d = hamming(gua.value, other.value)
            if d <= radius:
                neighbors.append((other, d))

        N = len(neighbors)
        if N == 0:
            return 0.0
        d_avg = sum(d for _, d in neighbors) / N
        return N / (d_avg + 1.0)

    def max_density(self) -> float:
        """当前空间最大疏密感知值"""
        if not self.guas:
            return 0.0
        return max(self.local_density(g) for g in self.guas)

    # ===== 自适应 λ 调节 =====

    def mu(self, id_l: int) -> float:
        """μ 敏感度——纯 id_l 推导"""
        if self._max_id_l <= 0:
            return 0.0
        return id_l / self._max_id_l

    def adjust_lambda(self, gua: Gua, S: float, S_max: float):
        """λ_new = λ_base × (1 - μ × S/S_max)  拥挤 → λ↑ → 散开"""
        if S_max <= 0:
            return
        mu_val = self.mu(gua.id_l)
        factor = 1.0 - mu_val * (S / S_max)
        gua.lambda_base = max(0, int(gua.lambda_base * max(0, factor)))

    # ===== 固化判据 =====

    def should_solidify(self, gua: Gua) -> bool:
        """亲缘碰撞达标 + 层深自判"""
        if gua.is_solid:
            return False
        threshold = max(3, VEC_DIM - gua.id_l)
        return gua.hit_count >= threshold

    # ===== 密度自清 =====

    def density_cleanup(self):
        """极度过载：合并最近同层卦对"""
        limit = max(5, VEC_DIM * 2)
        if len(self.guas) <= limit:
            return

        best_dist = VEC_DIM + 1
        best_pair = None
        for i in range(len(self.guas)):
            for j in range(i + 1, len(self.guas)):
                a, b = self.guas[i], self.guas[j]
                if a.id_l != b.id_l:
                    continue
                d = hamming(a.value, b.value)
                if d < best_dist:
                    best_dist = d
                    best_pair = (i, j)

        if best_pair:
            i, j = best_pair
            a, b = self.guas[i], self.guas[j]
            merged_val = (a.moving_bits ^ b.moving_bits) & FULL_MASK
            new_g = Gua(merged_val, min(a.pos, b.pos), a.length)
            if a.is_solid:
                new_g.core = a.core
                new_g.is_solid = True
            elif b.is_solid:
                new_g.core = b.core
                new_g.is_solid = True
            self.guas.pop(max(i, j))
            self.guas.pop(min(i, j))
            self.guas.append(new_g)

    # ===== 节律 =====

    def tick(self):
        """一个节律周期"""
        self.tick_count += 1

        # 1. 全局密度
        S_max = self.max_density()

        # 2. 感知 + 自调节
        for g in self.guas:
            S = self.local_density(g)
            self.adjust_lambda(g, S, S_max)

        # 3. 碰撞交互（能量累积触发的卦两两配对）
        active = [g for g in self.guas if self.should_participate(g)]
        for i in range(0, len(active) - 1, 2):
            a, b = active[i], active[i + 1]
            diff, common = a.collide(b)
            a.hit_count += 1
            b.hit_count += 1
            if not a.is_solid:
                a.value = (a.value & a.mask) | (diff & ~a.mask)
            if not b.is_solid:
                b.value = (b.value & b.mask) | (common & ~b.mask)

        # 4. 固化判据
        for g in self.guas:
            if self.should_solidify(g):
                g.solidify()

        # 5. 密度自清
        self.density_cleanup()

    # ===== 持久化 =====

    def save(self):
        """保存卦群状态"""
        data = {
            'tick': self.tick_count,
            'guas': [
                {
                    'v': g.value, 'p': g.pos, 'l': g.length,
                    's': g.is_solid, 'c': g.core, 'h': g.hit_count,
                    'e': g.energy,
                }
                for g in self.guas
            ]
        }
        with open(STATE_FILE, 'w') as f:
            json.dump(data, f)

    def load(self) -> bool:
        """加载卦群状态"""
        if not os.path.exists(STATE_FILE):
            return False
        with open(STATE_FILE, 'r') as f:
            data = json.load(f)
        self.tick_count = data.get('tick', 0)
        self.guas = []
        for gd in data.get('guas', []):
            g = Gua(gd['v'], gd['p'], gd['l'])
            g.is_solid = gd.get('s', False)
            g.core = gd.get('c', 0)
            g.hit_count = gd.get('h', 0)
            g.energy = gd.get('e', 0)
            self.guas.append(g)
        for g in self.guas:
            if g.id_l > self._max_id_l:
                self._max_id_l = g.id_l
        return True

    # ===== 状态 =====

    @property
    def size(self) -> int:
        return len(self.guas)

    @property
    def active_count(self) -> int:
        return sum(1 for g in self.guas if not g.is_solid)

    @property
    def solid_count(self) -> int:
        return sum(1 for g in self.guas if g.is_solid)

    @property
    def max_layer(self) -> int:
        return self._max_id_l

    def status(self) -> dict:
        return {
            'total': self.size,
            'active': self.active_count,
            'solid': self.solid_count,
            'tick': self.tick_count,
            'max_layer': self.max_layer,
        }
