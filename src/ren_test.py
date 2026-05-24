# -*- coding: utf-8 -*-
"""
Ren 态微循环 · 最小闭环测试

三才时态:
  天(TIAN) — 锚, 已固化的历史
  人(REN)  — 挂, 黄灯期, 碰撞发生的空隙
  地(DI)   — 坍缩结果, 成为下一轮天

测试: 10字 A轴(笔画) · 验证激发→咬合→坍缩微循环
"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi_kernel import Gua, _fit
from tools.tri_encode import tri_encode
from tools.strokes import get_strokes
import time

# ============================================================
# 收紧咬合: 至少 min_match 位匹配才咬
# ============================================================
FIT_MIN = 1  # 原始门槛

def _fit_strict(a: Gua, b: Gua, min_match: int = FIT_MIN) -> bool:
    """a 凸 ∧ b 凹 → 至少 min_match 位匹配才咬合。"""
    pa = a.value & 0xFF
    pb = b.value & 0xFF
    match = pa & ~pb & 0xFF
    return match.bit_count() >= min_match


def _fit_rate(chars):
    """统计这组字中任意两卦的咬合概率。"""
    n = len(chars)
    guas = [(ch, Gua(tri_encode(ch)[0].value)) for ch in chars]
    hits = 0
    total = 0
    for i in range(n):
        for j in range(n):
            total += 1
            if _fit_strict(guas[i][1], guas[j][1]):
                hits += 1
    return hits, total

# ============================================================
# Ren 态
# ============================================================

class Ren:
    """挂态 — 系统的空隙。生命有限, 咬合或湮灭。

    owner: 谁开的这道口子
    tau:   最大存活时间(碰撞次数)
    core:  当前卦值
    """

    def __init__(self, owner: str, g: Gua, tau: int = 5):
        self.owner = owner
        self.tau = tau          # 还能碰几次
        self.core = g           # 当前值
        self.history = []       # [(碰谁, XOR结果, 咬合否)]
        self.alive = True

    def try_bite(self, target: Gua, label: str) -> bool:
        """尝试咬合。咬上→坍缩, 没咬上→耗τ。"""
        if not self.alive:
            return False

        self.tau -= 1
        fit_a = _fit_strict(self.core, target)
        fit_b = _fit_strict(target, self.core)

        if fit_a or fit_b:
            # 咬合成功 → XOR 产生新值
            new_val = self.core.value ^ target.value
            self.core = Gua(new_val)
            self.history.append((label, new_val, '咬'))
            self.alive = False  # 坍缩
            return True
        else:
            # 没咬上 → 计数
            self.history.append((label, None, '空'))
            if self.tau <= 0:
                self.alive = False  # τ耗尽 → 湮灭
            return False

    def outcome(self) -> str:
        if not self.alive and self.history and self.history[-1][2] == '咬':
            return f"坍缩→{self.core.value:04X}"
        elif not self.alive:
            return "湮灭"
        return f"悬挂中(τ={self.tau})"


# ============================================================
# 单轴微循环测试
# ============================================================

def test_ren_lifecycle():
    """10字 A轴单轴 Ren 态微循环。

    流程:
      1. 选锚(天): 同笔画数的一组字
      2. 发 Ren 态: 给定一个字, 开挂
      3. 循环碰撞: 跟锚中字逐个碰
      4. 坍缩或湮灭: 看结果
    """
    chars = "水河火木天地日月山河"
    print("「Ren 微循环」10字 · A轴 · 门槛≥3位\n")

    # 先测咬合率
    hits, total = _fit_rate(chars)
    print(f"咬合率: {hits}/{total} = {hits/total:.1%}\n")

    # 分组: 同笔画数的锚
    by_strokes = {}
    for ch in chars:
        sc = get_strokes(ch)
        by_strokes.setdefault(sc, []).append(ch)

    print("天(锚):")
    for sc, group in sorted(by_strokes.items()):
        print(f"  {sc}画: {group}")

    # 测试1: 水(4画) 挂, 跟 4画组碰
    print("\n" + "=" * 50)
    print("测试1: 「水」挂, 跟4画组碰")
    a, _, _ = tri_encode('水')
    ren = Ren('水', Gua(a.value), tau=5)

    for target_ch in by_strokes.get(4, []):
        if target_ch == '水':
            continue
        ta, _, _ = tri_encode(target_ch)
        bitten = ren.try_bite(Gua(ta.value), target_ch)
        print(f"  碰{target_ch} → {'咬!' if bitten else '空'} (τ={ren.tau})")
        if not ren.alive:
            break

    print(f"  结果: {ren.outcome()}")
    print(f"  历史: {[(h[0], h[2]) for h in ren.history]}")

    # 测试2: 河(8画) 挂, 跟 8画组碰
    print("\n" + "=" * 50)
    print("测试2: 「河」挂, 跟8画组碰")
    a, _, _ = tri_encode('河')
    ren = Ren('河', Gua(a.value), tau=5)

    for target_ch in by_strokes.get(8, []) + ['海', '湖', '江']:
        if target_ch == '河':
            continue
        ta, _, _ = tri_encode(target_ch)
        bitten = ren.try_bite(Gua(ta.value), target_ch)
        print(f"  碰{target_ch} → {'咬!' if bitten else '空'} (τ={ren.tau})")
        if not ren.alive:
            break

    print(f"  结果: {ren.outcome()}")

    # 测试3: τ耗尽 → 湮灭
    print("\n" + "=" * 50)
    print("测试3: 「木」挂 tau=2, 故意碰不咬合的")
    a, _, _ = tri_encode('木')
    ren = Ren('木', Gua(a.value), tau=2)

    for target_ch in ['金', '刀', '剑']:
        ta, _, _ = tri_encode(target_ch)
        bitten = ren.try_bite(Gua(ta.value), target_ch)
        print(f"  碰{target_ch} → {'咬!' if bitten else '空'} (τ={ren.tau})")
        if not ren.alive:
            break

    print(f"  结果: {ren.outcome()}")

    # 测试4: 同字群内碰撞
    print("\n" + "=" * 50)
    print("测试4: 同画群批量碰撞统计")
    results = []
    for ch in chars:
        sc = get_strokes(ch)
        group = [c for c in chars if get_strokes(c) == sc and c != ch]
        if not group:
            continue

        a, _, _ = tri_encode(ch)
        ren = Ren(ch, Gua(a.value), tau=5)
        for target_ch in group:
            ta, _, _ = tri_encode(target_ch)
            ren.try_bite(Gua(ta.value), target_ch)
            if not ren.alive:
                break
        results.append((ch, sc, ren.outcome()))

    print(f"  {'字':<4} {'画':<4} {'结果'}")
    for ch, sc, out in results:
        print(f"  {ch:<4} {sc:<4} {out}")

    # 分析
    collapsed = [r for r in results if '坍缩' in r[2]]
    died = [r for r in results if '湮灭' in r[2]]
    print(f"\n  坍缩: {len(collapsed)}/{len(results)}")
    print(f"  湮灭: {len(died)}/{len(results)}")


if __name__ == '__main__':
    test_ren_lifecycle()
