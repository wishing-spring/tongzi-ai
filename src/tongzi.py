# -*- coding: utf-8 -*-
"""
童子 v1.6 · 完整流水线
========================
编码 → 金字塔路由 → 层内池碰撞 → 归类 → 解码
"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi_kernel import Gua, Pyramid, form
from tools.decode import Codec


class Tongzi:
    """童子完整流水线。

    金字塔包含一切 —— 层内池 + 碰撞 + 路由 + 归类。
    """

    def __init__(self):
        self.pyramid = Pyramid()
        self.codec = Codec()

    # ============================================================
    # 学: 编码 → 投入金字塔 → 层内碰撞
    # ============================================================

    def learn(self, text: str):
        """喂入知识。逐字编码 → 金字塔 flow (含碰撞)。"""
        for ch in text:
            g = self.codec.encode(ch)
            self.pyramid.flow(g)
        return len(text)

    # ============================================================
    # 问: 编码 → 金字塔 flow → 解码
    # ============================================================

    def ask(self, text: str) -> dict:
        """问一个问题。完整流水线。"""
        results = []

        for ch in text:
            g = self.codec.encode(ch)
            route = self.pyramid.flow(g)
            out_g = route['出值']
            label = self.codec.decode_rich(out_g, route)

            results.append({
                '字': ch,
                '入卦': form(g),
                '停层': f"{route['入层']}爻",
                '锁数': route['锁数'],
                '生子': route['生子'],
                '结果': label,
            })

        return {
            '输入': text,
            '逐字': results,
            '塔状态': self.pyramid.stats(),
        }

    def status(self):
        return {
            '码本字': len(self.codec),
            **self.pyramid.stats(),
        }


# ============================================================
# 演示
# ============================================================
if __name__ == '__main__':
    t = Tongzi()

    print("「学」")
    n = t.learn("道法自然天地玄黄乾坤阴阳太极无极上下左右前后生死动静虚实你好世界")
    print(f"  入塔 {n} 字")
    s = t.pyramid.stats()
    print(f"  总池卦 {s['总池卦']}, 碰撞 {s['总碰撞']} 次\n")

    print("=" * 50)
    for q in ["你好", "乾坤", "生死", "无极", "上善若水"]:
        r = t.ask(q)
        print(f"问: 「{q}」")
        for item in r['逐字']:
            print(f"  {item['字']} [{item['停层']} · {item['锁数']}锁] → {item['结果']}")
        print()

    print(t.status())
