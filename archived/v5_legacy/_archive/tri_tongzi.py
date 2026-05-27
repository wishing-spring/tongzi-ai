# -*- coding: utf-8 -*-
"""
三轴童子 · 正交三元组流水线

一字 → (G_A, G_B, G_C) → 三条金字塔并行 → 交汇约束解析
"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi_kernel import Gua, Pyramid, form
from tools.tri_encode import tri_encode, tri_label
from tools.strokes import get_strokes, get_structure, get_component


class TriTongzi:
    """三轴童子。

    A塔(笔画) + B塔(结构) + C塔(部件) 。
    正交运行。交汇处咬合。
    """

    def __init__(self):
        self.pyr_A = Pyramid()   # 笔画塔
        self.pyr_B = Pyramid()   # 结构塔
        self.pyr_C = Pyramid()   # 部件塔
        self._chars: dict[str, tuple] = {}  # ch → (a,b,c) 原始三元组

    # ============================================================
    # 学
    # ============================================================

    def learn(self, text: str):
        """喂入知识。每字生成三元组, 入三塔。"""
        for ch in text:
            if ch not in self._chars:
                a, b, c = tri_encode(ch)
                self._chars[ch] = (a, b, c)
            else:
                a, b, c = self._chars[ch]

            self.pyr_A.flow(a)
            self.pyr_B.flow(b)
            self.pyr_C.flow(c)

        return len(text)

    # ============================================================
    # 问
    # ============================================================

    def ask(self, text: str) -> dict:
        """查询。三元编码 → 三塔碰撞 → 交汇解析。"""
        results = []

        for ch in text:
            a, b, c = tri_encode(ch)

            # 三塔碰撞 (生态系统用)
            self.pyr_A.flow(a)
            self.pyr_B.flow(b)
            self.pyr_C.flow(c)

            # 交汇: 不查碰撞后的值, 查原始编码
            # 每个轴独立找 top-3 候选, 再取交集
            result = self._resolve_intersect(a, b, c, ch)

            results.append({
                '字': ch,
                'A': f"{get_strokes(ch)}画",
                'B': ['独','左右','上下','品','全包','半包','左中右','上中下'][get_structure(ch)],
                'C': f"部{get_component(ch)}",
                '结果': result,
            })

        return {'输入': text, '逐字': results}

    def _resolve_intersect(self, a: Gua, b: Gua, c: Gua, ch: str) -> str:
        """交汇约束解析: 三轴 top-5 取交集。"""
        av = a.value & 0xFFFF
        bv = b.value & 0xFFFF
        cv = c.value & 0xFFFF

        def top_k(val, k=5):
            ranked = []
            for known_ch, (ka, kb, kc) in self._chars.items():
                d = (val ^ (ka.value & 0xFFFF)).bit_count()
                ranked.append((d, known_ch))
            ranked.sort(key=lambda x: x[0])
            return [ch for d, ch in ranked[:k]], ranked[0]

        a_top5, a_best = top_k(av)
        b_top5, b_best = top_k(bv)
        c_top5, c_best = top_k(cv)

        a_set, b_set, c_set = set(a_top5), set(b_top5), set(c_top5)
        inter_ab = a_set & b_set
        inter_ac = a_set & c_set
        inter_bc = b_set & c_set
        all3 = inter_ab & c_set

        if all3:
            lst = sorted(all3)[:3]
            return f"[3] {'|'.join(lst)}"
        elif inter_ab:
            lst = sorted(inter_ab)[:3]
            return f"[AB] {'|'.join(lst)}"
        elif inter_ac:
            lst = sorted(inter_ac)[:3]
            return f"[AC] {'|'.join(lst)}"
        elif inter_bc:
            lst = sorted(inter_bc)[:3]
            return f"[BC] {'|'.join(lst)}"
        else:
            return f"[-] {a_best[1]}|{b_best[1]}|{c_best[1]}"

    def stats(self) -> dict:
        return {
            '库大小': len(self._chars),
            'A塔': self.pyr_A.stats(),
            'B塔': self.pyr_B.stats(),
            'C塔': self.pyr_C.stats(),
        }


# ============================================================
# 演示
# ============================================================
if __name__ == '__main__':
    t = TriTongzi()

    # 学一批字
    from tools.strokes import STROKE_COUNT
    all_chars = list(STROKE_COUNT.keys())
    t.learn(''.join(all_chars))
    print(f"学 {len(all_chars)} 字")

    # 测
    print("\n" + "=" * 60)
    tests = [
        "水河火",
        "天地人",
        "日月星",
        "爱恨",
        "红绿蓝",
        "你我他",
        "上下左右",
        "生死",
        "森林",
    ]
    for q in tests:
        r = t.ask(q)
        parts = [f"{it['字']}→{it['结果']}" for it in r['逐字']]
        print(f"「{q}」: {' | '.join(parts)}")

    print(f"\n{t.stats()}")
