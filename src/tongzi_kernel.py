# Copyright (c) 2026 Tongzi Project (wishing-spring)
# Licensed under the MIT License. See LICENSE file for details.
"""
童子 · 第3组 · 金字塔 + 层内池
================================
卦爻是砖。金字塔是结构。每层都有自己的池。

  Gua      — 16位 F₂ 值, 仅此而已
  Layer    — 一层砖 + 一个碰撞池
  Pyramid  — 7层分辨率梯度, 每层内生碰撞
"""

from __future__ import annotations
from tongzi_constants import VEC_DIM, FULL_MASK, PHI_BITS, PHI_LEN


# ============================================================
# φ 母体取位
# ============================================================

def phi_slice(pos: int, length: int = VEC_DIM) -> int:
    """从 φ 母体截取位段。返回原始整数值。"""
    bits = PHI_BITS[pos:pos + length]
    if len(bits) < length:
        bits += PHI_BITS[:length - len(bits)]
    return int(bits, 2) & ((1 << length) - 1)


# ============================================================
# 卦爻 — 砖
# ============================================================

class Gua:
    """16 位 F₂ 卦爻。纯粹的值, 无负载。"""

    __slots__ = ('value',)

    def __init__(self, value: int = 0):
        self.value = value & FULL_MASK

    def __repr__(self):
        return f"Gua({self.value:04X})"


def yao(g: Gua) -> list:
    """拆卦为爻。"""
    return [(g.value >> (15 - i)) & 1 for i in range(16)]


def form(g: Gua, w: int = 8) -> str:
    """可视化卦元 (w 位宽)。"""
    mask = (1 << w) - 1
    v = g.value & mask
    chars = []
    for i in range(w - 1, -1, -1):
        chars.append('#' if (v >> i) & 1 else '.')
    return ''.join(chars)


# ============================================================
# 榫卯: 面型判定
# ============================================================

# 每卦 16 位中取 8 个棱角 = 高 8 位作为 "前面"
# 8 棱角: 每棱角 1 位 → 8 位面
# 凸: 对应位 >= 4; 凹: 对应位 < 4

from dataclasses import dataclass

@dataclass
class Facet:
    """8棱角面型。"""
    pattern: int   # 8位, 1=凸 0=凹

    @classmethod
    def from_gua(cls, g: Gua) -> Facet:
        v = g.value & 0xFF  # 低8位
        # 每棱角含多位, 求和 ≥ 某个值判为凸
        # 简化: 每 2 位一组, 8 组 = 16 位
        pattern = 0
        for i in range(8):
            bits = (g.value >> (i * 2)) & 0x3
            if bits >= 2:
                pattern |= (1 << i)
        return cls(pattern)

    @property
    def convex(self) -> int:
        """凸棱数。"""
        return self.pattern.bit_count()

    @property
    def concave(self) -> int:
        """凹棱数。"""
        return 8 - self.convex


def _fit(a: Gua, b: Gua) -> bool:
    """a 凸 ∧ b 凹 → 咬合。

    a 的前面碰到 b 的后面。
    至少一个棱角 a 凸且对应 b 凹则咬合。
    """
    pa = a.value & 0xFF
    pb = b.value & 0xFF
    # a 凸位 & b 凹位 → 非零即咬合
    return (pa & ~pb & 0xFF) != 0


# ============================================================
# 层 — 砖块群 + 碰撞池
# ============================================================

class LayerPool:
    """层内微型池。存储+碰撞+生子。支持标记追踪。"""
    def __init__(self, width: int):
        self.width = width
        self._guas: list[Gua] = []
        self._tags: dict[int, str] = {}  # id(gua) → tag

    def add(self, g: Gua, tag: str = None):
        self._guas.append(g)
        if tag:
            self._tags[id(g)] = tag

    def find(self, target: Gua) -> list[Gua]:
        return [g for g in self._guas if _fit(target, g)]

    def find_tagged(self, target: Gua) -> list[str]:
        """找匹配的卦，返回它们的tag列表。"""
        tags = []
        for g in self._guas:
            if _fit(target, g):
                t = self._tags.get(id(g))
                if t:
                    tags.append(t)
        return tags

    def all(self) -> list[Gua]:
        return list(self._guas)

    def tag_of(self, g: Gua) -> str:
        return self._tags.get(id(g), '')

    def __len__(self):
        return len(self._guas)


class Layer:
    """一层。宽度 W → 2^W 块砖 + 一个碰撞池。"""

    def __init__(self, width: int):
        if width < 2 or width > 16:
            raise ValueError(f"层宽需 2~16, 不是 {width}")
        self.width = width
        self.size = 1 << width
        self.bricks: list[Gua] = [Gua(i) for i in range(self.size)]
        self.pool = LayerPool(width)

    def __len__(self):
        return self.size

    def __getitem__(self, i: int) -> Gua:
        return self.bricks[i]

    def __repr__(self):
        return f"Layer({self.width}爻, {self.size}块, 池{len(self.pool)}卦)"


# ============================================================
# 金字塔 — 7 层
# ============================================================

class Pyramid:
    """7 层分辨率梯度。每层都有池。

    尖(2爻) → 粗判
    底(8爻) → 精辨
    """

    def __init__(self, min_width: int = 2, max_width: int = 8):
        self.layers: dict[int, Layer] = {}
        for w in range(min_width, max_width + 1):
            self.layers[w] = Layer(w)
        self.min = min_width
        self.max = max_width
        self.hits: dict[int, int] = {}   # id(gua) → 碰撞次数
        self.total_collisions: int = 0

    # ============================================================
    # 升降
    # ============================================================

    def ascend(self, g: Gua, from_w: int) -> tuple[Gua, int]:
        """上一层: 砍最低位。"""
        if from_w <= self.min:
            return g, from_w
        return Gua(g.value >> 1), from_w - 1

    def descend(self, g: Gua, from_w: int) -> list[tuple[Gua, int]]:
        """下一层: 补位, 产生两个子卦。"""
        if from_w >= self.max:
            return [(g, from_w)]
        base = g.value << 1
        return [(Gua(base), from_w + 1), (Gua(base | 1), from_w + 1)]

    # ============================================================
    # 碰撞: 卦元进塔, 在对应层碰
    # ============================================================

    def collide(self, g: Gua, at_width: int, max_hits: int = 32):
        """卦元在指定层的池中碰撞。

        1. 找到池中咬合的卦
        2. 碰撞: 双方换低位
        3. 生子: 咬合 → XOR子 + AND子入池
        """
        layer = self.layers[at_width]
        hits = layer.pool.find(g)

        # 只处理前 N 个
        active = hits[:max_hits] if len(hits) > max_hits else hits
        new_children = []

        for hit in active:
            # 碰撞: 换低8位
            g_lo = g.value & 0xFF
            h_lo = hit.value & 0xFF
            g.value = (g.value & 0xFF00) | h_lo
            hit.value = (hit.value & 0xFF00) | g_lo

            # 计数
            self.hits[id(g)] = self.hits.get(id(g), 0) + 1
            self.hits[id(hit)] = self.hits.get(id(hit), 0) + 1
            self.total_collisions += 1

            # 生子
            xor_val = g.value ^ hit.value
            and_val = g.value & hit.value
            if xor_val:
                new_children.append(Gua(xor_val))
            if and_val and and_val != xor_val:
                new_children.append(Gua(and_val))

        # 子卦入该层池
        for child in new_children:
            layer.pool.add(child)

        # 池裁剪: 超 128 卦, 移除最不活跃的
        if len(layer.pool) > 128:
            ranked = [(self.hits.get(id(x), 0), x) for x in layer.pool.all()]
            ranked.sort(key=lambda p: p[0])
            layer.pool._guas = [x for _, x in ranked[-128:]]

        return {
            '入层': at_width,
            '锁数': len(hits),
            '生子': len(new_children),
            '池大小': len(layer.pool),
        }

    # ============================================================
    # flow: 路由 → 碰撞 → 归类
    # ============================================================

    def flow(self, g: Gua) -> dict:
        """完整流水:

        1. 路由: 卦元自身复杂度决定停哪层
           1的密度越高 → 越深(高分辨率)
        2. 在该层池中碰撞
        3. 归类: 碰撞后的值, 最像哪块砖
        """
        # 1. 路由: 密度 → 分辨率
        density = g.value.bit_count()
        # 密度 0-16 → 映射到 2-8爻
        at_w = self.min + (density * (self.max - self.min)) // 16
        at_w = max(self.min, min(self.max, at_w))

        cur = Gua(g.value)

        # 2. 在该层池中碰撞
        collision = self.collide(cur, at_w)

        # 3. 归类: 碰撞后的值跟该层砖块比
        trimmed = Gua(cur.value & ((1 << at_w) - 1))
        best_brick = None
        best_dist = 999
        for brick in self.layers[at_w].bricks:
            d = (trimmed.value ^ brick.value).bit_count()
            if d < best_dist:
                best_dist = d
                best_brick = brick

        # 4. 沉淀
        self.layers[at_w].pool.add(Gua(g.value))

        return {
            '入层': at_w,
            '出层': at_w,
            '出值': best_brick or Gua(0),
            '差距': best_dist,
            '锁数': collision['锁数'],
            '生子': collision['生子'],
            '池锁': collision['锁数'],
        }

    # ============================================================
    # 查询
    # ============================================================

    def potential(self, g: Gua) -> int:
        """Ψ: 卦元活跃度。"""
        c = self.hits.get(id(g), 0)
        return c.bit_length() if c else 0

    def stats(self) -> dict:
        total_pool = sum(len(l.pool) for l in self.layers.values())
        return {
            '层数': len(self.layers),
            '总池卦': total_pool,
            '总碰撞': self.total_collisions,
            '活跃卦': len(self.hits),
        }

    def __repr__(self):
        ls = [f"  {w}爻: {self.layers[w]}" for w in range(self.min, self.max + 1)]
        return "金字塔\n" + "\n".join(ls)


# ============================================================
# 演示
# ============================================================
if __name__ == '__main__':
    from tools.encode import text_to_seed

    pyr = Pyramid()

    print("「金字塔 + 层内池」")
    print(pyr)
    print()

    # 喂几个字
    for ch in "道法自然天地":
        v = phi_slice(text_to_seed(ch), 8)
        g = Gua(v)
        r = pyr.flow(g)
        print(f"{ch} {form(g)} → 停{r['入层']}爻 锁{r['锁数']} 生子{r['生子']}")

    print(f"\n{pyr.stats()}")
