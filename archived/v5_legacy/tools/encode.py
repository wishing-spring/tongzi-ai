# -*- coding: utf-8 -*-
"""
编码器 v2 · 原生区 + 口岸

16bit 编码:
  [15:14] script 标记 (2bit) — 0=汉字区 1=拉丁区 2=其他区
  [13]    保留

汉字区 ([15:14]=00):
  [12:7]  码点低 6bit (锚定)
  [6:0]   笔画数 (0-127, 实际 1-64)

拉丁区 ([15:14]=01):
  [12:7]  码点低 6bit (锚定)
  [6:0]   码点高 7bit 折叠

其他区 ([15:14]=10):
  [12:0]  码点低 13bit
"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tools.strokes import get_strokes, script_tag


def encode(ch: str) -> int:
    """一字 → 16bit

    汉字: script=00 | 码点低6bit | 笔画数7bit
    拉丁: script=01 | 码点低6bit | 码点折叠7bit
    其他: script=10 | 码点低13bit
    """
    cp = ord(ch)
    script = script_tag(ch)

    if script == 0:
        # 汉字区 — 有笔画解剖
        cp6 = cp & 0x3F           # 码点低 6bit
        sc = min(get_strokes(ch), 127)  # 笔画数, 上限 127
        value = (0 << 14) | (cp6 << 7) | sc

    elif script == 1:
        # 拉丁区 — 码点折叠
        cp6 = cp & 0x3F           # 低 6bit
        cp7 = (cp >> 7) & 0x7F    # 高 7bit
        value = (1 << 14) | (cp6 << 7) | cp7

    else:
        # 其他区 — 纯码点
        value = (2 << 14) | (cp & 0x1FFF)

    return value & 0xFFFF


def batch_encode(text: str) -> list[int]:
    """逐字编码。"""
    return [encode(ch) for ch in text]


def decode_label(val: int) -> str:
    """可读标签。"""
    script = (val >> 14) & 0x3
    names = {0: '汉字', 1: '拉丁', 2: '其他'}
    if script == 0:
        cp = (val >> 7) & 0x3F
        sc = val & 0x7F
        return f"汉字 码{cp:02X} 画{sc}"
    elif script == 1:
        cp6 = (val >> 7) & 0x3F
        cp7 = val & 0x7F
        return f"拉丁 码{cp6:02X}:{cp7:02X}"
    else:
        cp13 = val & 0x1FFF
        return f"其他 码{cp13:04X}"


if __name__ == '__main__':
    # 测试汉字
    print("汉字区:")
    for ch in "水河火天地木":
        v = encode(ch)
        print(f"  {ch}({get_strokes(ch)}画) → {v:04X} {v:016b}  {decode_label(v)}")

    # 距离
    print(f"\n汉明距离:")
    def dist(a, b):
        return (encode(a) ^ encode(b)).bit_count()
    for a, b in [('水','河'), ('水','火'), ('水','木'), ('日','月'), ('天','地')]:
        print(f"  {a}<->{b}: {dist(a,b)} 位")

    # 口岸
    print(f"\n口岸:")
    for ch in "aAz9":
        v = encode(ch)
        print(f"  {ch} → {v:04X} {decode_label(v)}")
