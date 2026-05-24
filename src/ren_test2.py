# -*- coding: utf-8 -*-
"""
Ren 态 · 第二批实验 · 收紧咬合 + 三轴联合
==========================================
目标: 湮灭率 30-50%, 让 τ 机制真正生效
策略: 16位满空间 + 门槛扫描 + 三轴联合咬合
"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi_kernel import Gua
from tools.tri_encode import tri_encode
from tools.strokes import get_strokes, STROKE_COUNT

# ============================================================
# 咬合函数 — 16位满空间
# ============================================================
def _fit_16(a: Gua, b: Gua, min_match: int) -> bool:
    """a凸∧b凹，至少 min_match 位匹配(共16位)。"""
    pa = a.value & 0xFFFF
    pb = b.value & 0xFFFF
    match = pa & ~pb & 0xFFFF
    return match.bit_count() >= min_match


def _tri_fit(ch_a: str, ch_b: str, min_match: int) -> tuple:
    """三轴联合咬合。返回 (A咬?, B咬?, C咬?, 全咬?)。"""
    aA, aB, aC = tri_encode(ch_a)
    bA, bB, bC = tri_encode(ch_b)
    ok_a = _fit_16(Gua(aA.value), Gua(bA.value), min_match) or \
           _fit_16(Gua(bA.value), Gua(aA.value), min_match)
    ok_b = _fit_16(Gua(aB.value), Gua(bB.value), min_match) or \
           _fit_16(Gua(bB.value), Gua(aB.value), min_match)
    ok_c = _fit_16(Gua(aC.value), Gua(bC.value), min_match) or \
           _fit_16(Gua(bC.value), Gua(aC.value), min_match)
    return ok_a, ok_b, ok_c, (ok_a and ok_b and ok_c)


# ============================================================
# 门槛扫描
# ============================================================
def scan_thresholds(chars: list, group_fn, group_label: str):
    """对一组字扫描门槛1-8。"""
    print(f"\n{'='*60}")
    print(f"门槛扫描: {group_label} ({len(chars)}字)")
    print(f"{'门槛':<6} {'总对数':<8} {'咬合':<8} {'比率':<8} {'三轴全咬':<10}")

    n = len(chars)
    for t in range(1, 9):
        hits = 0
        tri_hits = 0
        total = 0
        for i in range(n):
            for j in range(n):
                total += 1
                ok_a, ok_b, ok_c, all_ok = _tri_fit(chars[i], chars[j], t)
                if ok_a or ok_b or ok_c:
                    hits += 1
                if all_ok:
                    tri_hits += 1

        bar = '█' * max(1, hits * 30 // max(total, 1))
        print(f"  {t:<4}  {total:<8} {hits:<8} {hits/total:<7.1%} {tri_hits:<10} {bar}")

    return


# ============================================================
# Ren 三轴联合碰撞
# ============================================================
class TriRen:
    """三轴联合 Ren 态。

    τ 耗尽或三轴全咬 → 坍缩。
    只有单轴/双轴咬 → 继续漂。
    """

    def __init__(self, owner: str, tau: int = 5):
        self.owner = owner
        self.tau = tau
        self.alive = True
        self.history = []
        self.min_match = 3  # 默认门槛

    def try_bite(self, target_ch: str) -> dict:
        """尝试三轴咬合。"""
        if not self.alive or target_ch == self.owner:
            return {'bitten': False, 'detail': 'self'}

        self.tau -= 1
        ok_a, ok_b, ok_c, all_ok = _tri_fit(
            self.owner, target_ch, self.min_match
        )

        detail = f"A:{int(ok_a)}B:{int(ok_b)}C:{int(ok_c)}"
        ax = sum([ok_a, ok_b, ok_c])

        if all_ok:
            # 三轴全咬 → 坍缩
            self.alive = False
            self.history.append((target_ch, '坍缩', ax, detail))
            return {'bitten': True, 'axes': 3, 'detail': detail}

        elif ax >= 1:
            # 部分咬合 → 留下痕迹但继续
            self.history.append((target_ch, '半咬', ax, detail))
            if self.tau <= 0:
                self.alive = False
                return {'bitten': False, 'dead': True, 'detail': detail}
            return {'bitten': False, 'partial': True, 'axes': ax, 'detail': detail}
        else:
            # 全空
            self.history.append((target_ch, '空', 0, detail))
            if self.tau <= 0:
                self.alive = False
                return {'bitten': False, 'dead': True, 'detail': detail}
            return {'bitten': False, 'detail': detail}

    def outcome(self) -> str:
        if not self.alive:
            last = self.history[-1] if self.history else None
            if last and last[1] == '坍缩':
                return f"坍缩({last[2]}轴)"
            else:
                return "湮灭"
        return f"悬挂(τ={self.tau})"


def run_tri_ren_batch(chars: list, min_match: int, tau: int = 5):
    """批量三轴Ren碰撞。"""
    print(f"\n{'='*60}")
    print(f"三轴Ren: {len(chars)}字 · 门槛≥{min_match}位 · τ={tau}")

    results = []
    for ch in chars:
        ren = TriRen(ch, tau=tau)
        ren.min_match = min_match

        # 跟其他所有人碰
        for target in chars:
            if target == ch:
                continue
            ren.try_bite(target)
            if not ren.alive:
                break

        out = ren.outcome()
        history = ' → '.join(
            f"{h[0]}{'!' if h[1]=='坍缩' else '~' if h[1]=='半咬' else '·'}"
            for h in ren.history[:6]
        )
        print(f"  {ch:<4} {out:<12} {history}")
        results.append((ch, out))

    collapsed = [r for r in results if '坍缩' in r[1]]
    died = [r for r in results if '湮灭' in r[1]]
    print(f"\n  坍缩: {len(collapsed)}/{len(results)}  湮灭: {len(died)}/{len(results)}")
    return results


# ============================================================
# 主测试
# ============================================================
if __name__ == '__main__':
    all_chars = list(STROKE_COUNT.keys())[:30]  # 30字

    # 1. 门槛扫描
    scan_thresholds(all_chars, None, "30字全库")

    # 2. 选一个门槛做实际碰撞
    for t in [2, 3, 4]:
        run_tri_ren_batch(all_chars[:15], min_match=t, tau=5)

    # 3. 语义组测试
    print(f"\n{'='*60}")
    print("语义组: 4画字群")
    g4 = [ch for ch in all_chars if get_strokes(ch) == 4]
    for t in [2, 3]:
        run_tri_ren_batch(g4, min_match=t, tau=5)
