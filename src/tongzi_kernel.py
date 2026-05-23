# Copyright (c) 2026 Tongzi Project (wishing-spring)
# Licensed under the MIT License. See LICENSE file for details.
"""
童子 · 第3组 · 金字塔
=======================
卦爻是砖。金字塔是结构。

  Gua      — 16位 F₂ 值, 仅此而已
  Pyramid  — 7层分辨率梯度
  Layer    — 一层砖 (2^W 块)

操作: ascend(升)/descend(降)/resolve(解析)/put(放砖)
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

    def __init__(self, value: int):
        self.value = value & FULL_MASK

    def __repr__(self):
        return f"Gua({self.value:04X})"


def yao(g: Gua) -> list:
    """拆卦为爻。"""
    return [(g.value >> (15 - i)) & 1 for i in range(16)]


def bits(g: Gua) -> str:
    """卦的二进制串。"""
    return f"{g.value:016b}"


# ============================================================
# 层
# ============================================================

class Layer:
    """一层砖。宽度 W → 2^W 块。

    ┌─┬─┬─┬─┐
    ├─┼─┼─┼─┤  ← 4爻层, 16块
    └─┴─┴─┴─┘
    """

    def __init__(self, width: int):
        if width < 2 or width > 16:
            raise ValueError(f"层宽需 2~16, 不是 {width}")
        self.width = width
        self.size = 1 << width
        self.bricks: list[Gua] = [Gua(i) for i in range(self.size)]

    def __len__(self):
        return self.size

    def __getitem__(self, i: int) -> Gua:
        return self.bricks[i]

    def __repr__(self):
        return f"Layer({self.width}爻, {self.size}块)"


# ============================================================
# 金字塔
# ============================================================

class Pyramid:
    """7 层分辨率梯度。

          2爻 (4)
         3爻 (8)
        4爻 (16)
       5爻 (32)
      6爻 (64)
     7爻 (128)
    8爻 (256)

    尖 = 粗判, 底 = 精辨。
    """

    def __init__(self, min_width: int = 2, max_width: int = 8):
        self.layers: dict[int, Layer] = {}
        for w in range(min_width, max_width + 1):
            self.layers[w] = Layer(w)
        self.min = min_width
        self.max = max_width

    # ----- 升降 -----

    def ascend(self, g: Gua, from_layer: int) -> tuple[Gua, int]:
        """上一层: 砍掉最低位 → 分辨率减半。"""
        if from_layer <= self.min:
            return g, from_layer
        parent = Gua(g.value >> 1)
        return parent, from_layer - 1

    def descend(self, g: Gua, from_layer: int) -> list[Gua]:
        """下一层: 补一个位 → 分成两个子卦。"""
        if from_layer >= self.max:
            return [g]
        base = g.value << 1
        return [Gua(base), Gua(base | 1)]

    # ----- 解析 -----

    def resolve(self, target: Gua):
        """从尖往下走, 哪层停了就返回哪层。

        走法: target 跟每层的每个卦比, 全碰就停, 有锁就继续往下。
        """
        g = target
        for w in range(self.min, self.max + 1):
            trimmed = Gua(g.value & ((1 << w) - 1))
            # 看这一层有咬合吗 (用前后面 凸凹接触)
            has_lock = False
            for brick in self.layers[w].bricks:
                if _fit(brick, trimmed):
                    has_lock = True
                    break
            if not has_lock:
                return w - 1, g  # 停在上一层
        return self.max, g  # 走到底了

    # ----- 两步半流程 -----

    def flow(self, input_gua: Gua):
        """两步半: 路由 → 碰撞 → 归类。

        第1步: resolve(输入) → 定位到目标层
        第2步: 层内榫卯碰撞 → 找到所有咬合的砖
        半步:  resolve(结果) → 递归归类

        返回: (入层, 入值, 咬合数, 出层, 出值)
        """
        # 第1步: 路由——输入停在金字塔的哪层
        in_layer, trimmed = self.resolve(input_gua)

        # 第2步: 碰撞——在这一层跟所有砖怼, 看谁咬合
        if in_layer >= self.min:
            matches = [b for b in self.layers[in_layer].bricks
                       if _fit(trimmed, b)]
        else:
            matches = []

        # 半步: 归类——如果有匹配, 取中间的砖重新 resolve
        if matches:
            mid = matches[len(matches) // 2]
            out_layer, out_gua = self.resolve(mid)
        else:
            out_layer, out_gua = in_layer, trimmed

        return {
            '入层': in_layer,
            '入值': trimmed,
            '咬合': len(matches),
            '出层': out_layer,
            '出值': out_gua,
        }

    def put(self, g: Gua, layer: int):
        """替换指定层的一块砖。其他层不动。"""
        if layer not in self.layers:
            raise ValueError(f"无第{layer}爻层")
        idx = g.value & ((1 << layer) - 1)  # 取低 layer 位做索引
        self.layers[layer].bricks[idx] = g

    def __repr__(self):
        lines = [f"Pyramid({self.min}爻→{self.max}爻)"]
        for w in range(self.max, self.min - 1, -1):
            indent = "  " * (self.max - w)
            lines.append(f"{indent}{w}爻: {self.layers[w].size}块")
        return '\n'.join(lines)


# ============================================================
# 内置咬合判断 (凸凹接触)
# ============================================================

def _fit(a: Gua, b: Gua) -> bool:
    """a 的前面凸能插进 b 的后面凹?
    a+Z 的角对 b-Z 的角: {0→7, 1→6, 2→5, 3→4}
    """
    az = [(a.value >> i) & 1 for i in range(4)]
    bz = [(b.value >> (7 - i)) & 1 for i in range(4)]
    for x, y in zip(az, bz):
        if x == 1 and y == 1:
            return False  # 凸凸碰撞→不咬合
    return any(x == 1 and y == 0 for x, y in zip(az, bz))


# ============================================================
# 内置形态 (精简)
# ============================================================

def form(g: Gua, width: int = 8) -> str:
    """卦的平面形态。1=# 0=. """
    return ''.join('#' if (g.value >> (width - 1 - i)) & 1 else '.'
                   for i in range(width))


def voxel_layout(width: int) -> tuple:
    """给定位宽 → 最优 3D 布局。"""
    m = {
        2:(2,1,1), 3:(3,1,1), 4:(2,2,1), 5:(5,1,1),
        6:(3,2,1), 7:(7,1,1), 8:(2,2,2), 16:(2,2,4)
    }
    return m.get(width, (width, 1, 1))
