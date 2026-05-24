# Copyright (c) 2026 Tongzi Project (wishing-spring)
# Licensed under the MIT License. See LICENSE file for details.
"""
童子 v2.0 · 统一离散推理系统
=============================
三个金字塔(A/B/C轴) → 池子碰撞 → 三轴交汇归约
零外部依赖 · 纯F₂运算 · 单入口
"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi_kernel import Gua, Pyramid, LayerPool
from tools.tri_encode import tri_encode
from tools.strokes import get_strokes, STROKE_COUNT, get_structure, get_component, script_tag
from dataclasses import dataclass, field
from collections import Counter

FIT_MIN = 4     # 位锁定阈值 (16位中>=4位匹配)
TAU = 5         # 活性窗口: 每个卦元有几次匹配机会


# ============================================================
# 编码器
# ============================================================

def _encode_A(ch: str) -> Gua:
    """A轴: 笔画(高位6b) + 码点(低位10b)。同笔画字自然接近。"""
    cp = ord(ch)
    sc = min(get_strokes(ch), 63)
    cp10 = cp & 0x3FF
    return Gua((sc << 10) | cp10)

def _tri_encode(ch: str) -> tuple:
    """一字→(G_A, G_B, G_C)。A轴用笔画加权, B/C用标准编码。"""
    tag = script_tag(ch)
    if tag != 0:
        cp = ord(ch)
        v = (tag << 14) | (cp & 0x3FFF)
        g = Gua(v)
        return (g, g, g)
    gA = _encode_A(ch)
    _, gB, gC = tri_encode(ch)
    return (gA, gB, gC)


# ============================================================
# 节点: 一个字符在三轴空间中的状态
# ============================================================

@dataclass
class Node:
    ch: str
    gA: Gua; gB: Gua; gC: Gua
    tau: int = TAU
    alive: bool = True
    state: str = 'active'     # active | result | pruned
    scars: list = field(default_factory=list)

    def hamming_to(self, other: 'Node') -> int:
        """三轴汉明距离和。"""
        return ((self.gA.value ^ other.gA.value).bit_count() +
                (self.gB.value ^ other.gB.value).bit_count() +
                (self.gC.value ^ other.gC.value).bit_count())

    def axes_match(self, other: 'Node', m=FIT_MIN) -> tuple:
        """三轴位锁定判定。返回(ok_a, ok_b, ok_c, sum)。"""
        ok_a = _fit_16(self.gA, other.gA, m) or _fit_16(other.gA, self.gA, m)
        ok_b = _fit_16(self.gB, other.gB, m) or _fit_16(other.gB, self.gB, m)
        ok_c = _fit_16(self.gC, other.gC, m) or _fit_16(other.gC, self.gC, m)
        return ok_a, ok_b, ok_c, sum([ok_a, ok_b, ok_c])


def _fit_16(a: Gua, b: Gua, m=FIT_MIN) -> bool:
    """a凸∧b凹, >=m位即锁定。"""
    return ((a.value & 0xFFFF) & (~b.value & 0xFFFF)).bit_count() >= m


# ============================================================
# 统一系统
# ============================================================

class Tongzi:
    """童子统一离散推理系统。

    架构:
      feed(text) → 编码 → 三金字塔并行 → 池子碰撞 → 三轴归约 → 归档
      ask(ch) → 查询归档 → 返回邻居+路径
    """

    def __init__(self, tau=TAU, fit_min=FIT_MIN):
        self.tau = tau
        self.fit_min = fit_min
        self.pyr_A = Pyramid()
        self.pyr_B = Pyramid()
        self.pyr_C = Pyramid()
        self.archives: dict[str, Node] = {}
        self._order: list[str] = []   # 喂入顺序

    # ========================================================
    # 核心: 喂入
    # ========================================================

    def feed(self, text: str):
        """喂入文本。全流程: 编码→入塔→池碰→三轴判定→归档。"""
        nodes = []
        for ch in text:
            if ch not in STROKE_COUNT:
                continue
            if ch in self.archives:
                nodes.append(self.archives[ch])
                continue
            gA, gB, gC = _tri_encode(ch)
            node = Node(ch, gA, gB, gC, tau=self.tau)
            nodes.append(node)
            self._order.append(ch)

        # === 碰撞轮: 三池并行 + 三轴交汇判定 ===
        for i, ni in enumerate(nodes):
            if not ni.alive:
                continue

            candidates = [nj for j, nj in enumerate(nodes) if i != j and nj.alive]
            best = None  # (axes, target_node)

            for nj in candidates:
                ok_a, ok_b, ok_c, axes = ni.axes_match(nj, self.fit_min)
                tri = (axes == 3)

                ni.scars.append({
                    'target': nj.ch, 'axes': axes, 'tri': tri,
                    'A': ok_a, 'B': ok_b, 'C': ok_c
                })
                ni.tau -= 1

                if tri and (best is None or axes > best[0]):
                    best = (axes, nj)

                # 在三个金字塔各自碰撞
                self.pyr_A.flow(Gua(ni.gA.value))
                self.pyr_B.flow(Gua(ni.gB.value))
                self.pyr_C.flow(Gua(ni.gC.value))

                if ni.tau <= 0:
                    break

            # 判定
            if best is not None and best[0] == 3:
                # 归约: XOR融合三轴
                for s in ni.scars:
                    if s.get('result') is None:
                        s['result'] = 'part' if s['axes'] > 0 else 'null'
                for s in ni.scars:
                    if s['target'] == best[1].ch and s['tri']:
                        s['result'] = 'lock'
                        break
                ni.gA = Gua(ni.gA.value ^ best[1].gA.value)
                ni.gB = Gua(ni.gB.value ^ best[1].gB.value)
                ni.gC = Gua(ni.gC.value ^ best[1].gC.value)
                ni.alive = False
                ni.state = 'result'
            elif ni.tau <= 0:
                for s in ni.scars:
                    if s.get('result') is None:
                        s['result'] = 'prune'
                ni.alive = False
                ni.state = 'pruned'
            else:
                for s in ni.scars:
                    if s.get('result') is None:
                        s['result'] = 'part' if s['axes'] > 0 else 'null'
                ni.state = 'active'

        # === 归档 ===
        for node in nodes:
            self.archives[node.ch] = node

    # ========================================================
    # 查询
    # ========================================================

    def ask(self, ch: str) -> dict | None:
        """查询一个字的归档。返回(None, dict, or str)。"""
        if ch not in self.archives:
            return None
        n = self.archives[ch]
        return {
            'ch': ch,
            'state': n.state,
            'tau': n.tau,
            'scars': [(s['target'], s['result'], s['axes']) for s in n.scars],
            'chain': self._trace(n),
        }

    def _trace(self, n: Node) -> str:
        parts = []
        for s in n.scars:
            r = s.get('result', '?')
            m = '!' if r == 'lock' else '~' if r == 'part' else '.'
            parts.append(f"{s['target']}{m}")
        return '→'.join(parts) if parts else '-'

    def neighbors(self, ch: str, k: int = 3) -> list:
        """找k个最近邻居(三轴汉明距离和)。"""
        if ch not in self.archives:
            return []
        n = self.archives[ch]
        dists = []
        for c2, n2 in self.archives.items():
            if c2 == ch:
                continue
            d = n.hamming_to(n2)
            dists.append((d, c2))
        dists.sort()
        return [(c, d) for d, c in dists[:k]]

    # ========================================================
    # 统计
    # ========================================================

    def status(self) -> dict:
        """系统状态。"""
        r = sum(1 for n in self.archives.values() if n.state == 'result')
        p = sum(1 for n in self.archives.values() if n.state == 'pruned')
        h = sum(1 for n in self.archives.values() if n.state == 'active')
        total = len(self.archives)
        return {
            'total': total,
            'result': r, 'pruned': p, 'active': h,
            'result_rate': f'{r/total:.1%}' if total else '0%',
            'prune_rate': f'{p/max(1,r+p):.1%}',
            'pool_sizes': {
                'A': {w: len(self.pyr_A.layers[w].pool) for w in range(2,9)},
                'B': {w: len(self.pyr_B.layers[w].pool) for w in range(2,9)},
                'C': {w: len(self.pyr_C.layers[w].pool) for w in range(2,9)},
            },
        }

    def report(self):
        """打印完整报告。"""
        s = self.status()
        print(f"童子 v2.0 · 统一系统 · τ={self.tau} · 阈值>={self.fit_min}位")
        print(f"  归约:{s['result']}  剪枝:{s['pruned']}  悬挂:{s['active']}  总计:{s['total']}")
        print(f"  归约率:{s['result_rate']}  剪枝率:{s['prune_rate']}")
        print(f"\n  池子状态:")
        for axis in 'ABC':
            ps = s['pool_sizes'][axis]
            sizes = ' '.join(f'L{w}:{ps[w]:>3}' for w in range(2,9))
            print(f"    {axis}轴:  {sizes}")


# ============================================================
# 快速入口
# ============================================================

if __name__ == '__main__':
    tz = Tongzi(tau=5, fit_min=4)
    train = "水河火木天地日月山河金刀剑一二三四五六七八九十万千爱恨生死你我他"
    print(f"喂入 {len(train)} 字符...")
    tz.feed(train)
    tz.report()

    # 邻居展示
    print("\n--- 邻居 ---")
    for ch in "水火爱一":
        if ch in tz.archives:
            nbs = tz.neighbors(ch, 5)
            nlist = ' '.join(f'{c}({d})' for c,d in nbs)
            print(f"  {ch} → {nlist}")
