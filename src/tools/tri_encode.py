# -*- coding: utf-8 -*-
"""
三轴编码器 · 正交三元组

一个汉字 → 三个卦元 (A·B·C), 各走各的塔, 交汇处咬合。

  A轴: 笔画数+码点 → 金字塔A
  B轴: 结构类+码点 → 金字塔B  
  C轴: 部件+码点   → 金字塔C
"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi_kernel import Gua
from tools.strokes import get_strokes, get_structure, get_component, script_tag


def tri_encode(ch: str) -> tuple:
    """一字 → (G_A, G_B, G_C) 正交三元组。

    G_A [15:14]=00 [13:7]=码低7 [6:0]=笔画
    G_B [15:14]=01 [13:10]=码低4 [9:7]=结构 [6:0]=码中7
    G_C [15:14]=10 [13:8]=码低6 [7:2]=部件 [1:0]=码高2
    """
    cp = ord(ch)
    tag = script_tag(ch)

    # 非汉字: 三轴合一 (全是码点)
    if tag != 0:
        v = (tag << 14) | (cp & 0x3FFF)
        g = Gua(v)
        return (g, g, g)

    # --- A轴: 笔画 ---
    sc = min(get_strokes(ch), 127)
    cp7 = (cp >> 7) & 0x7F
    a_val = (0 << 14) | (cp7 << 7) | sc

    # --- B轴: 结构 ---
    st = get_structure(ch)
    cp4 = (cp >> 10) & 0xF
    cp7b = (cp >> 3) & 0x7F
    b_val = (1 << 14) | (cp4 << 10) | (st << 7) | cp7b

    # --- C轴: 部件 ---
    comp = get_component(ch)
    cp6 = cp & 0x3F
    cp2 = (cp >> 14) & 0x3
    c_val = (2 << 14) | (cp6 << 8) | (comp << 2) | cp2

    return (
        Gua(a_val & 0xFFFF),
        Gua(b_val & 0xFFFF),
        Gua(c_val & 0xFFFF),
    )


def tri_label(g: Gua) -> str:
    """卦元 → 轴标签。"""
    axis = (g.value >> 14) & 0x3
    if axis == 0:
        cp7 = (g.value >> 7) & 0x7F
        sc = g.value & 0x7F
        return f"A轴 码{cp7:02X} 画{sc}"
    elif axis == 1:
        cp4 = (g.value >> 10) & 0xF
        st = (g.value >> 7) & 0x7
        return f"B轴 码{cp4:01X} 结构{['独','左右','上下','品','全包','半包','左中右','上中下'][st]}"
    elif axis == 2:
        cp6 = (g.value >> 8) & 0x3F
        comp = (g.value >> 2) & 0x3F
        return f"C轴 码{cp6:02X} 部件{comp}"
    return f"? {g.value:04X}"


if __name__ == '__main__':
    for ch in "水河火木森晶道你":
        a, b, c = tri_encode(ch)
        print(f"{ch}:")
        print(f"  {tri_label(a)}")
        print(f"  {tri_label(b)}")
        print(f"  {tri_label(c)}")

    # 距离
    print(f"\n三轴汉明:")
    for ch in "水河火木":
        a,b,c = tri_encode(ch)
        print(f"  {ch}: A={a.value:04X} B={b.value:04X} C={c.value:04X}")

    # 水vs河 三轴距离
    print(f"\n水 vs 河:")
    wa,wb,wc = tri_encode('水')
    ra,rb,rc = tri_encode('河')
    print(f"  A轴: {(wa.value ^ ra.value).bit_count()} 位")
    print(f"  B轴: {(wb.value ^ rb.value).bit_count()} 位")
    print(f"  C轴: {(wc.value ^ rc.value).bit_count()} 位")
