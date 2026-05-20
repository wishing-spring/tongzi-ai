# Copyright (c) 2026 Tongzi Project (wishing-spring)
# Licensed under the MIT License. See LICENSE file for details.
"""
童子 · 极简群域架构 · 内核
===============================
F₂ⁿ 空间 + φ 母体卦群 + 八条核心群运算。

组成:
  Gua    — F₂ 空间中带出生身份的位向量
  Space  — 卦群容器，驱动内生节律

不包含: 浮点、矩阵、梯度、词嵌入、注意力、自回归、外部时钟、神经网络任何形式。

使用方法:
  >>> space = Space()
  >>> g = space.ingest("hello")
  >>> g2 = space.ingest("world")
  >>> diff, common = g.collide(g2)
  >>> space.tick()               # 推进节律
  >>> space.save()               # 持久化
"""
from __future__ import annotations
from typing import List, Tuple, Optional, Dict
import json
import os

from tongzi_constants import VEC_DIM, FULL_MASK, PHI_BITS, PHI_LEN


# ═══════════════════════════════════════════════════════════
# 纯函数 — 位运算 (无副作用，不含 n)
# ═══════════════════════════════════════════════════════════

def bit_count(v: int) -> int:
    """popcount: 汉明权重。公理 3 基础。"""
    return v.bit_count()


def hamming(a: int, b: int) -> int:
    """汉明距离 d(a,b) = popcount(a⊕b)。公理 3。"""
    return bit_count(a ^ b)


def rotate_left(v: int, k: int) -> int:
    """位循环左旋 Rk(v)。公理 4 基础。
    参数:
      v: 位向量 (FULL_MASK 内)
      k: 旋转步数 (自动对 VEC_DIM 取模)
    返回: 旋转后的位向量
    """
    k %= VEC_DIM
    return ((v << k) | (v >> (VEC_DIM - k))) & FULL_MASK


def rotate_right(v: int, k: int) -> int:
    """位循环右旋，对称于 rotate_left。"""
    k %= VEC_DIM
    return ((v >> k) | (v << (VEC_DIM - k))) & FULL_MASK


def gray_encode(n: int) -> int:
    """格雷编码: n → n⊕(n>>1)。生成格雷巡检环。"""
    return n ^ (n >> 1)


def gray_ring(v: int) -> int:
    """格雷环上的下一站。相邻卦汉明距离恒为 1。"""
    n = gray_encode(v)
    n = (n + 1) & FULL_MASK
    # 反格雷解码
    mask = n
    while mask:
        mask >>= 1
        n ^= mask
    return n & FULL_MASK


# ═══════════════════════════════════════════════════════════
# Gua — F₂ 空间中的卦元
# ═══════════════════════════════════════════════════════════

class Gua:
    """F₂ 空间中的卦元。

    每个卦天生携带:
      {id_t, id_l} = 身份证 — 从 φ 位置推导，不需存储
      pos, length    — 出生位置与长度

    固化: 内核段锁死不可改写，游动段继续自由演化。
    """

    __slots__ = (
        'value',      # int : 位向量值
        'pos',        # int : φ 出生位置
        'length',     # int : 爻数 (id_l)
        'id_t',       # int : 出生序号 (= pos)
        'id_l',       # int : 层编码 (= length)
        'mask',       # int : 固化掩码 (高 id_l 位为 1)
        'is_solid',   # bool: 是否已固化
        'core',       # int : 固化内核 (= value & mask)
        'hit_count',  # int : 累计碰撞次数
        'energy',     # int : 能量累积值 (频控用)
        'lambda_base',# int : 伸缩基数 (λ)
        'source',     # str : 创建时的原始文本 (内丹反向译出用)
    )

    def __init__(self, value: int, pos: int, length: int):
        # 输入校验
        if length <= 0 or length > VEC_DIM:
            raise ValueError(f"length 必须在 (0, {VEC_DIM}] 内，得到 {length}")
        if pos < 0:
            raise ValueError(f"pos 必须 ≥ 0，得到 {pos}")

        self.value  = value & ((1 << length) - 1)
        self.pos    = pos
        self.length = length

        # 身份证 — 从 φ 推导
        self.id_t   = pos          # 出生序号
        self.id_l   = length       # 层编码 (爻数)

        # 固化
        self.is_solid = False
        self.core     = 0
        self.mask     = self._derive_mask()

        # 运行时统计
        self.hit_count   = 0
        self.energy      = 0
        self.lambda_base = 0
        self.source      = ""     # 创建时的原始文本

    # ---- 内部 ----

    def _derive_mask(self) -> int:
        """从 id_l 推导固化掩码。

        内核段 = 高 id_l 位。id_l=0 → 无内核。
        """
        if self.id_l <= 0:
            return 0
        core_bits = min(self.id_l, VEC_DIM)
        return ((1 << core_bits) - 1) << (VEC_DIM - core_bits)

    # ---- 只读属性 ----

    @property
    def moving_bits(self) -> int:
        """游动段: 参与运算的自由位。

        固化后内核段从所有运算中排除。
        """
        if self.is_solid:
            return self.value & ~self.mask
        return self.value & FULL_MASK

    @property
    def core_bits(self) -> int:
        """内核段: 已锁死的根基位。"""
        return self.value & self.mask if self.is_solid else 0

    # ---- 工厂 ----

    @classmethod
    def spawn(cls, value: int, pos: int, id_l: int) -> Gua:
        """生成合体子卦。id_l 下沉但位宽保持 VEC_DIM。"""
        g = cls(value & FULL_MASK, pos, VEC_DIM)
        g.id_l = max(2, id_l)
        g.mask = g._derive_mask()
        return g

    # ---- 八条核心运算 ----

    def collide(self, other: Gua) -> Tuple[int, int]:
        """碰撞: 双入双出，信息不丢失。

        返回: (diff ⊕, common ∧)
          diff   = 差异向量 (a⊕b)
          common = 共识向量 (a∧b)

        只读取游动段。固化段永不参与。
        """
        a = self.moving_bits
        b = other.moving_bits
        return (a ^ b, a & b)

    def orbit(self, center: int, k: int) -> int:
        """绕心盘旋: 绕 center 在等距球面旋转 k 步。

        保持 d(v, center) 不变。Rk(v⊕c) ⊕ c。
        """
        diff = (self.moving_bits ^ center) & FULL_MASK
        return (rotate_left(diff, k) ^ center) & FULL_MASK

    def stretch(self, center: int, lam: int) -> int:
        """径向伸缩: λ∈{0,1}。

        λ=0: 原位不动。
        λ=1: 推至对面 v⊕(v⊕c) = c。中间值实现渐进伸缩。
        """
        if lam == 0:
            return self.moving_bits
        delta = (self.moving_bits ^ center) & FULL_MASK
        return (self.moving_bits ^ delta) & FULL_MASK

    def hamming_ball(self, center: int, r: int) -> bool:
        """判定: self 是否在以 center 为心、半径 r 的汉明球内。"""
        return hamming(self.value, center) <= r

    def centrality(self, center: int) -> int:
        """核心度: 距离 center 越近越高。返回 −d(self, center)。"""
        return -hamming(self.value, center)

    # ---- 固化操作 ----

    def solidify(self) -> None:
        """固化: 锁定内核段。此后内核位永不改写。"""
        if not self.is_solid:
            self.core     = self.value & self.mask
            self.is_solid = True

    def weakly_unlock(self, bit_index: int) -> bool:
        """同源弱解禁: 仅前驱/后继可微调单个固化位。

        参数:
          bit_index: 0..VEC_DIM-1 内的位索引
        返回: True 表示确实翻转了该位
        """
        if not self.is_solid:
            return False
        if bit_index < 0 or bit_index >= VEC_DIM:
            raise ValueError(f"bit_index 必须在 [0, {VEC_DIM}) 内")
        self.value ^= (1 << bit_index)
        self.core  ^= (1 << bit_index)
        return True

    # ---- 显示 ----

    def __repr__(self) -> str:
        fmt = f'0{VEC_DIM}b'
        state = 'S' if self.is_solid else '-'
        return f"Gua({self.value:{fmt}}|t={self.id_t},l={self.id_l}{state})"

    def __hash__(self) -> int:
        return hash((self.value, self.pos, self.length, self.is_solid))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Gua):
            return NotImplemented
        return (self.value == other.value and
                self.pos == other.pos and
                self.length == other.length and
                self.is_solid == other.is_solid)


# ═══════════════════════════════════════════════════════════
# Space — F₂ⁿ 群域空间
# ═══════════════════════════════════════════════════════════

STATE_FILE = os.path.join(os.path.dirname(__file__), '.tongzi_state.json')

class Space:
    """F₂ⁿ 离散群域空间。

    所有卦在此共存、碰撞、演化。无外部时钟，节律内生。

    用法:
      space = Space()
      space.ingest("some text")     # φ 编码成卦
      space.tick()                  # 推进节律
      space.save() / space.load()   # 持久化
    """

    F0 = 256  # 基础能量阈值: 越大碰撞越稀疏

    def __init__(self):
        self.guas: List[Gua] = []
        self.tick_count: int = 0
        self._max_id_l: int = 0       # 当前最大层编码 (运行时更新)
        self._density_cache: Dict[int, float] = {}  # id(gua) → S(x)

    # ============================================================
    # φ 编码: 文本 → 卦
    # ============================================================

    @staticmethod
    def encode(text: str) -> Tuple[int, int]:
        """φ-卦编码。

        文本 → 哈希种子 → φ 二进制位置 → 取 VEC_DIM 位。
        同文本永远映射到同卦。返回 (value, pos)。
        """
        if not text:
            raise ValueError("不能编码空文本")

        # 文本 → 32-bit 种子 (XOR + 移位混合)
        seed = 0
        for i, c in enumerate(text):
            seed ^= ord(c) << (i * 7 % 32)
        seed &= 0x7FFFFFFF

        pos = seed % PHI_LEN

        # φ 二进制串中取 VEC_DIM 位
        chars = []
        for i in range(VEC_DIM):
            chars.append(PHI_BITS[(pos + i) % PHI_LEN])
        value = int(''.join(chars), 2)

        return value, pos

    # ============================================================
    # 卦管理
    # ============================================================

    def ingest(self, text: str) -> Gua:
        """摄入文本，生成新卦并加入空间。

        同文本生成同卦 (值相同，但每次创建新 Gua 对象)。
        """
        value, pos = self.encode(text)
        g = Gua(value, pos, VEC_DIM)
        g.source = text

        self._update_layer_max(g.id_l)
        g.lambda_base = self._derive_lambda_base(g.id_l)

        self.guas.append(g)
        return g

    def _update_layer_max(self, id_l: int) -> None:
        if id_l > self._max_id_l:
            self._max_id_l = id_l

    def _derive_lambda_base(self, id_l: int) -> int:
        """λ 基数: 从层编码推导。

        id_l=0 → λ=0; id_l=Lmax → λ≈VEC_DIM/2。
        """
        if self._max_id_l <= 0:
            return 0
        ratio = id_l / self._max_id_l
        return int(ratio * (VEC_DIM // 2))

    # ============================================================
    # 内生频控: 能量累积制
    # ============================================================

    def f1(self, gua: Gua) -> int:
        """顺位频控: f₁ = F0/(1+id_t)。早生高频率。

        id_t 小 → 每 tick 累积能量多 → 更快触发放电。
        """
        return self.F0 // (1 + gua.id_t)

    def f2(self, gua: Gua) -> int:
        """层差频控: f₂ = F0/(1+id_l)。低层密交互。

        id_l 小 → 累积快 → 浅层卦频繁碰撞。
        """
        return self.F0 // (1 + gua.id_l)

    def _rate(self, gua: Gua) -> int:
        """速率: f₂ = F0/(1+id_l)。层深控节律。

        id_l 小 → 速率高 → 浅层卦频繁碰撞。
        同层卦同速——不因出生顺序偏斜。
        """
        return self.f2(gua)

    def _accumulate_energy(self, gua: Gua) -> None:
        """每 tick 能量累积。仅非固化卦。"""
        if gua.is_solid:
            return
        gua.energy += self._rate(gua)

    def _try_discharge(self, gua: Gua) -> bool:
        """能量满 F0 则放电，返回 True 表示本 tick 参与碰撞。

        固化卦永不放电。
        """
        if gua.is_solid:
            return False
        if gua.energy >= self.F0:
            gua.energy -= self.F0
            return True
        return False

    # ============================================================
    # 空间自感知
    # ============================================================

    def local_density(self, gua: Gua, radius: int = 3) -> float:
        """局部疏密感知: S(x) = N / (d̄_H + 1)。

        统计同层卦在汉明半径 r 内的密度。
        S 大 = 拥挤，S 小 = 空旷。
        """
        N = 0
        d_sum = 0
        for other in self.guas:
            if other is gua:
                continue
            if other.id_l != gua.id_l:   # 只感知同层
                continue
            d = hamming(gua.value, other.value)
            if d <= radius:
                N += 1
                d_sum += d

        if N == 0:
            return 0.0
        return N / (d_sum / N + 1.0)

    def max_density(self) -> float:
        """当前空间最大疏密感知值。空间空则返回 0。"""
        if not self.guas:
            return 0.0
        return max(self.local_density(g) for g in self.guas)

    # ============================================================
    # 自适应 λ 调节
    # ============================================================

    def mu(self, id_l: int) -> float:
        """μ 敏感度: 纯 id_l 推导。μ = id_l / Lmax。"""
        if self._max_id_l <= 0:
            return 0.0
        return id_l / self._max_id_l

    def adjust_lambda(self, gua: Gua, S: float, S_max: float) -> None:
        """λ_new = λ_base × (1 − μ × S/S_max)。

        拥挤 → λ 增大 → 卦向外散开 → S 回落 (负反馈闭环)。
        """
        if S_max <= 0:
            return
        mu_val  = self.mu(gua.id_l)
        factor  = 1.0 - mu_val * (S / S_max)
        gua.lambda_base = max(0, int(gua.lambda_base * max(0, factor)))

    # ============================================================
    # 固化判据
    # ============================================================

    def should_solidify(self, gua: Gua) -> bool:
        """固化判据: 亲缘碰撞次数达标 + 层深自判。

        高层卦 (大 id_l) 阈值更低 → 更易固化。
        最小阈值 = 3 以保证不会瞬间固化。
        """
        if gua.is_solid:
            return False
        threshold = max(3, VEC_DIM - gua.id_l)
        return gua.hit_count >= threshold

    # ============================================================
    # 密度自清
    # ============================================================

    def density_cleanup(self) -> Optional[Tuple[int, int]]:
        """极度过载时合并最近同层卦对。

        触发条件: 卦数 > VEC_DIM×2。
        合并规则: 游动段 XOR 融合，固化内核延续。

        返回: 合并的 (i, j) 索引对，或 None。
        """
        limit = max(5, VEC_DIM * 2)
        if len(self.guas) <= limit:
            return None

        # 找最近同层卦对 (O(N²), N≤32 可接受)
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

        if best_pair is None:
            return None

        i, j = best_pair
        a, b = self.guas[i], self.guas[j]

        # 合并
        merged_val = (a.moving_bits ^ b.moving_bits) & FULL_MASK
        merged = Gua(merged_val, min(a.pos, b.pos), a.length)
        merged.hit_count = max(a.hit_count, b.hit_count)
        merged.energy    = max(a.energy, b.energy)

        # 固化继承 (只继承一个的固化状态)
        if a.is_solid:
            merged.core     = a.core
            merged.is_solid = True
        elif b.is_solid:
            merged.core     = b.core
            merged.is_solid = True

        # 删除旧卦，插入新卦 (从后往前删避免索引偏移)
        if i > j:
            i, j = j, i
        self.guas.pop(j)
        self.guas.pop(i)
        self.guas.append(merged)

        return best_pair

    # ============================================================
    # 节律: 一个 tick 周期
    # ============================================================

    def tick(self) -> Dict[str, int]:
        """推进一个节律周期。

        顺序:
          1. 全局密度扫描
          2. λ 自适应调节 (所有卦)
          3. 能量累积 → 放电碰撞 (参与卦两两配对)
          4. 固化判据
          5. 密度自清

        返回: 本 tick 统计 {'collisions': N, 'solidified': M, 'merges': K}
        """
        self.tick_count += 1

        # ---- 1. 全局密度 ----
        S_max = self.max_density()

        # ---- 2. λ 自适应调节 ----
        for g in self.guas:
            S = self.local_density(g)
            self.adjust_lambda(g, S, S_max)

        # ---- 3. 能量累积 + 放电碰撞 ----
        for g in self.guas:
            self._accumulate_energy(g)

        active = [g for g in self.guas if self._try_discharge(g)]
        collision_count = 0
        merge_count = 0

        for i in range(0, len(active) - 1, 2):
            a, b = active[i], active[i + 1]

            # --- 原有碰撞 (A、B 原行为不变) ---
            diff, common = a.collide(b)
            a.hit_count += 1
            b.hit_count += 1
            collision_count += 1
            if not a.is_solid:
                a.value = (a.value & a.mask) | (diff & ~a.mask)
            if not b.is_solid:
                b.value = (b.value & b.mask) | (common & ~b.mask)

            # --- 合体产子: 两条腿 ---
            h = hamming(a.moving_bits, b.moving_bits)
            if 4 < h < 12:

                # XOR 合体: 差异关联链 (跳过零值)
                xor_val = a.moving_bits ^ b.moving_bits
                if xor_val:
                    C_xor = Gua(xor_val, self.tick_count + self.size, VEC_DIM)
                    C_xor.lambda_base = self._derive_lambda_base(C_xor.id_l)
                    self.guas.append(C_xor)
                    merge_count += 1

                # AND 合体: 共识沉淀 (跳过零值)
                and_val = a.moving_bits & b.moving_bits
                if and_val:
                    C_and = Gua(and_val, self.tick_count + self.size + 1, VEC_DIM)
                    C_and.lambda_base = self._derive_lambda_base(C_and.id_l)
                    self.guas.append(C_and)
                    merge_count += 1

        # ---- 4. 固化判据 ----
        solid_count = 0
        for g in self.guas:
            if self.should_solidify(g):
                g.solidify()
                solid_count += 1

        # ---- 5. 密度自清 ----
        merged = self.density_cleanup()

        return {
            'collisions': collision_count,
            'solidified': solid_count,
            'merges':     merge_count,
            'cleanups':   1 if merged else 0,
        }

    # ============================================================
    # 反向译出 — 极简内丹
    # ============================================================

    def express(self, gua: Gua) -> str:
        """反向译出: 用最近卦的源文本近似表达当前卦态。

        遍历空间内所有卦，找与给定卦游动段汉明距离最近者，
        返回其创建时的原始文本。无匹配时返回空串。
        """
        best = ""
        best_dist = VEC_DIM + 1
        for other in self.guas:
            if other is gua:
                continue
            if not other.source:
                continue
            d = hamming(gua.moving_bits, other.value)
            if d < best_dist:
                best_dist = d
                best = other.source
        return best

    # ============================================================
    # 持久化
    # ============================================================

    def save(self) -> None:
        """保存全空间状态到 STATE_FILE。"""
        data = {
            'tick': self.tick_count,
            'guas': [
                {
                    'v': g.value,
                    'p': g.pos,
                    'l': g.length,
                    's': g.is_solid,
                    'c': g.core,
                    'h': g.hit_count,
                    'e': g.energy,
                    'lb': g.lambda_base,
                    'src': g.source,
                }
                for g in self.guas
            ]
        }
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

    def load(self) -> bool:
        """从 STATE_FILE 恢复空间状态。返回是否成功。"""
        if not os.path.exists(STATE_FILE):
            return False

        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.tick_count = data.get('tick', 0)
        self.guas = []

        for gd in data.get('guas', []):
            g = Gua(gd['v'], gd['p'], gd['l'])
            g.is_solid    = gd.get('s', False)
            g.core        = gd.get('c', 0)
            g.hit_count   = gd.get('h', 0)
            g.energy      = gd.get('e', 0)
            g.lambda_base = gd.get('lb', 0)
            g.source      = gd.get('src', '')
            self.guas.append(g)

        # 重建运行时推导量
        self._max_id_l = 0
        for g in self.guas:
            self._update_layer_max(g.id_l)
        for g in self.guas:
            if g.lambda_base == 0:  # 仅对旧存档未保存的补充
                g.lambda_base = self._derive_lambda_base(g.id_l)

        return True

    # ============================================================
    # 只读状态
    # ============================================================

    @property
    def size(self) -> int:
        """卦总数"""
        return len(self.guas)

    @property
    def active_count(self) -> int:
        """非固化卦数 (= 可参与碰撞的)"""
        return sum(1 for g in self.guas if not g.is_solid)

    @property
    def solid_count(self) -> int:
        """已固化卦数"""
        return sum(1 for g in self.guas if g.is_solid)

    @property
    def max_layer(self) -> int:
        """最大层编码"""
        return self._max_id_l

    def status(self) -> dict:
        """全状态快照。"""
        total = self.size
        active = self.active_count
        return {
            'total':     total,
            'active':    active,
            'solid':     total - active,
            'tick':      self.tick_count,
            'max_layer': self.max_layer,
        }

    def __repr__(self) -> str:
        s = self.status()
        return (f"Space(t={s['tick']} N={s['total']} "
                f"active={s['active']} solid={s['solid']})")
