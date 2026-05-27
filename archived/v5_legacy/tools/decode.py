# -*- coding: utf-8 -*-
"""解码 · 卦元→文本 + 码本"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi_kernel import Gua, form
from tools.encode import encode as new_encode, decode_label
from tools.encode import batch_encode

# ============================================================
# 方式1: 值→字符 (固定码本)
# ============================================================

CODE64 = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    "+-"
)

def decode_fixed(g: Gua, width: int = 8) -> str:
    v = g.value & ((1 << width) - 1)
    out = []
    while v > 0 or not out:
        out.append(CODE64[v & 0x3F])
        v >>= 6
    return ''.join(reversed(out))


# ============================================================
# 方式2: 码本 (编码时存, 解码时查)
# ============================================================

class Codec:
    """双向编解码。"""

    def __init__(self):
        self._book: dict[int, str] = {}  # value → text

    def encode(self, text: str) -> Gua:
        """文本 → 卦元。用原生区+口岸编码器。"""
        v = new_encode(text)
        g = Gua(v)
        self._book[g.value & 0xFF] = text
        return g

    def decode(self, g: Gua) -> str:
        """卦元 → 文本。查码本, 找不到就用最近邻。"""
        v = g.value & 0xFF
        if v in self._book:
            return self._book[v]
        return self.nearest(g)

    def decode_rich(self, g: Gua, flow_info: dict = None) -> str:
        """生活化解码。

        入N爻 → 看得粗细
        锁N块 → 把握大小
        差N位 → 差距远近
        """
        v = g.value & 0xFF
        if v in self._book:
            base = self._book[v]
            marker = ""
        else:
            base, dist = self._nearest_detail(g)
            if dist == 0:
                marker = ""
            elif dist == 1:
                marker = "几乎就是"
            elif dist == 2:
                marker = "八九不离十"
            elif dist == 3:
                marker = "有点像"
            elif dist == 4:
                marker = "勉强沾边"
            else:
                marker = "没把握,大概是"

        parts = []
        if flow_info:
            info = flow_info.get('入层', 0)
            if info >= 7:
                parts.append("显微镜看")
            elif info >= 5:
                parts.append("仔细看")
            elif info >= 3:
                parts.append("正常看")
            else:
                parts.append("远远看")

            locks = flow_info['池锁'] if '池锁' in flow_info else flow_info.get('交叉咬合', 0)
            if locks >= 100:
                parts.append("非常确定")
            elif locks >= 50:
                parts.append("很确定")
            elif locks >= 10:
                parts.append("有把握")
            elif locks > 0:
                parts.append("不太确定")
            else:
                parts.append("无把握")

        if marker:
            result = f"{marker}{base}"
        else:
            result = f"就是{base}"

        if parts:
            return f"[{', '.join(parts)}] {result}"
        return result

    def _nearest_detail(self, g: Gua) -> tuple:
        """返回 (最近文本, 距离)。"""
        best_text = "?"
        best_dist = 99
        v = g.value & 0xFF
        for bv, text in self._book.items():
            d = (v ^ bv).bit_count()
            if d < best_dist:
                best_dist = d
                best_text = text
        return best_text, best_dist

    def batch_encode(self, text: str) -> list[Gua]:
        """逐字编码。存入码本。返回卦元列表。"""
        return [self.encode(ch) for ch in text]

    def batch_decode(self, guas: list[Gua]) -> str:
        """逐卦解码。拼接。"""
        return ''.join(self.decode(g) for g in guas)

    def __len__(self):
        return len(self._book)


# ============================================================
# 演示
# ============================================================
if __name__ == '__main__':
    codec = Codec()

    # 编码
    text = "道法自然"
    guas = codec.batch_encode(text)
    print(f"编码: '{text}' → {len(guas)} 卦元")
    for ch, g in zip(text, guas):
        print(f"  {ch} → {form(g)}")

    # 解码
    result = codec.batch_decode(guas)
    print(f"\n解码: {len(guas)} 卦元 → '{result}'")
    print(f"匹配: {'OK' if result == text else 'MISS'}")

    # 固定码本测试
    print(f"\n固定解码: Gua(0)={decode_fixed(Gua(0))}, Gua(42)={decode_fixed(Gua(42))}")
