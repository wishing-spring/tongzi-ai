# Copyright (c) 2026 Tongzi Project (wishing-spring)
# Licensed under the MIT License. See LICENSE file for details.
"""
童子 · 第3组 · 卦爻
=====================
卦爻: 0 和 1 组成的纯粹单位。

  Gua  — 16 位 F₂ 值, 仅此而已
  yao  — 拆解: value → [0,1,0,...]

无出生位置, 无运算, 无方法。
操作见 tools.axioms, 编码见 tools.encode。
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
# 卦爻
# ============================================================

class Gua:
    """16 位 F₂ 卦爻。纯粹的值, 无负载。

        1001111000110111
        丨丨丨丨丨丨丨丨丨丨丨丨丨丨丨丨
        爻爻爻爻爻爻爻爻爻爻爻爻爻爻爻爻
    """

    __slots__ = ('value',)

    def __init__(self, value: int):
        self.value = value & FULL_MASK

    def __repr__(self):
        return f"Gua({self.value:04X})"


def yao(g: Gua) -> list:
    """拆卦为爻: Gua → 16 条 [0,1,0,1,...]"""
    return [(g.value >> (15 - i)) & 1 for i in range(16)]


def bits(g: Gua) -> str:
    """卦的二进制串。"""
    return f"{g.value:016b}"


def form(g: Gua, width: int = 16) -> str:
    """卦的平面形态。"""
    chars = []
    for i in range(width):
        bit = (g.value >> (width - 1 - i)) & 1
        chars.append('1' if bit else '.')
    return ''.join(chars)


def form_lines(g: Gua, width: int = 16) -> str:
    """卦的爻线形态。"""
    lines = []
    for i in range(width):
        bit = (g.value >> (width - 1 - i)) & 1
        lines.append('===' if bit else '---')
    return '\n'.join(lines)


def voxel(g: Gua, layout: tuple = None) -> tuple:
    """卦 → 立体体素。

    低位优先: g.value 的低 N 位映射到体素。
    N = X*Y*Z
    """
    if layout is None:
        layout = (2, 2, 4)
    X, Y, Z = layout
    total = X * Y * Z

    grid = [[[False]*X for _ in range(Y)] for __ in range(Z)]
    for i in range(total):
        bit = (g.value >> (total - 1 - i)) & 1
        z = i // (X * Y)
        remainder = i % (X * Y)
        y = remainder // X
        x = remainder % X
        grid[z][y][x] = bool(bit)
    return grid


def voxel_layout(width: int) -> tuple:
    """给定位宽 → 最优 3D 布局。

    2→(2,1,1)   3→(3,1,1)   4→(2,2,1)   5→(5,1,1)
    6→(3,2,1)   7→(7,1,1)   8→(2,2,2)   9→(3,3,1)
    10→(5,2,1)  11→(11,1,1) 12→(3,2,2)  13→(13,1,1)
    14→(7,2,1)  15→(5,3,1)  16→(2,2,4)
    """
    layouts = {
        2:  (2, 1, 1),   3:  (3, 1, 1),
        4:  (2, 2, 1),   5:  (5, 1, 1),
        6:  (3, 2, 1),   7:  (7, 1, 1),
        8:  (2, 2, 2),   9:  (3, 3, 1),
        10: (5, 2, 1),   11: (11, 1, 1),
        12: (3, 2, 2),   13: (13, 1, 1),
        14: (7, 2, 1),   15: (5, 3, 1),
        16: (2, 2, 4),
    }
    return layouts.get(width, (width, 1, 1))


def voxel_view(g: Gua, layout: tuple = None) -> str:
    """立体卦爻的三视图 + 逐层。"""
    if layout is None:
        layout = voxel_layout(16)
    X, Y, Z = layout
    total = X * Y * Z
    g3 = voxel(g, layout)

    # 俯视 (top-down)
    top = []
    for y in range(Y):
        row = ''
        for x in range(X):
            filled = any(g3[z][y][x] for z in range(Z))
            row += '#' if filled else '.'
        top.append(row)

    # 前视 (front)
    front = []
    for z in range(Z-1, -1, -1):
        row = ''
        for x in range(X):
            filled = any(g3[z][y][x] for y in range(Y))
            row += '#' if filled else '.'
        front.append(row)

    # 右视 (right)
    right = []
    for z in range(Z-1, -1, -1):
        row = ''
        for y in range(Y):
            filled = any(g3[z][y][x] for x in range(X))
            row += '#' if filled else '.'
        right.append(row)

    # 逐层
    layers = []
    for z in range(Z-1, -1, -1):
        lr = []
        for y in range(Y):
            row = ''
            for x in range(X):
                row += '#' if g3[z][y][x] else '.'
            lr.append(row)
        layers.append('\n'.join(lr))

    lines = [f"体素 {X}x{Y}x{Z}  ({total}爻)"]
    lines.append("俯视   前视   右视")
    for i in range(max(len(top), len(front))):
        t = top[i] if i < len(top) else '  '
        f = front[i] if i < len(front) else '  '
        r = right[i] if i < len(right) else '  '
        lines.append(f"{t}     {f}     {r}")
    lines.append("")
    for z in range(Z):
        lines.append(f"--层{z}--")
        lines.append(layers[Z-1-z])

    return '\n'.join(lines)


def fit(a: Gua, b: Gua, width: int = 16) -> str:
    """榫卯测试: 两个同宽卦爻是否互锁。"""
    mask = (1 << width) - 1
    va = a.value & mask
    vb = b.value & mask
    overlap = va & vb

    # 简化: 无重叠 = 可互锁 (实际需要邻接检测, 这里先做基础判断)
    if overlap == 0 and va != 0 and vb != 0:
        return "互锁"
    elif overlap != 0:
        return f"碰撞 ({overlap.bit_count()} 位)"
    else:
        return "无接触"


# ============================================================
# 生成
# ============================================================

def generate_gua(pos: int) -> Gua:
    """φ 母体 → 一个卦爻。位置只用于取位, 不绑定卦上。"""
    return Gua(phi_slice(pos))


# ============================================================
# 空间
# ============================================================

class Space:
    """卦元仓库。

    纯粹容器。不管理、不登记、不计数。
    卦放进去就在。拿出来就离开。
    """

    def __init__(self, name: str = ""):
        self.name = name
        self._guas: list[Gua] = []

    def put(self, g: Gua):
        """放入一个卦元。"""
        self._guas.append(g)

    def take(self, idx: int = -1) -> Gua:
        """取出最末卦元 (默认) 或指定索引。取出即离开仓库。"""
        return self._guas.pop(idx)

    def peek(self) -> list[Gua]:
        """看一下仓库里有什么。不取出。"""
        return list(self._guas)

    def __len__(self):
        return len(self._guas)

    def __repr__(self):
        return f"Space('{self.name}', {len(self._guas)} 卦)"
