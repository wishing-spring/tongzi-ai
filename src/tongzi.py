# Copyright (c) 2026 Tongzi Project (wishing-spring)
# Licensed under the MIT License. See LICENSE file for details.
"""
童子 v2.1 · 统一离散推理系统 · 32位
=====================================
三个金字塔(A/B/C轴, 2-10爻) → 池子碰撞 → 三轴交汇归约
零外部依赖 · 纯F₂运算 · 单入口
"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi_kernel import Gua, Pyramid, LayerPool, VEC_DIM, FULL_MASK
from tools.tri_encode import tri_encode
from tools.strokes import get_strokes, STROKE_COUNT, script_tag
from dataclasses import dataclass, field

FIT_MIN = 8     # 位锁定阈值 (32位中>=8位, 等同16位时代>=4的比例)
TAU = 5         # 活性窗口


# ============================================================
# 编码器 — 32位
# ============================================================

def _encode_A32(ch: str) -> Gua:
    """A轴: 保距投影——码点 XOR 移位折叠到32位。"""
    cp = ord(ch)
    # XOR错位: 高11位 ^ 低21位, 无损保距
    hi = cp >> 11
    lo = cp & 0x7FF
    folded = (hi ^ lo) & 0x7FF
    v = (cp << 11) | folded  # 码点占高21位, 折叠占低11位
    return Gua(v & FULL_MASK)

def _encode_B32(ch: str) -> Gua:
    """B轴: 旋转投影——码点循环左移5位。"""
    cp = ord(ch)
    rotated = ((cp << 5) | (cp >> 16)) & 0x1FFFFF  # 21位旋转
    # 高位重复填充到32位
    v = rotated | (rotated << 10)
    return Gua(v & FULL_MASK)

def _encode_C32(ch: str) -> Gua:
    """C轴: Gray码变换——相邻码点仅差1位, 结构保距。"""
    cp = ord(ch)
    gray = cp ^ (cp >> 1)  # 标准Gray码
    # 镜像填充到32位
    v = gray | (gray << 11)
    return Gua(v & FULL_MASK)

def _tri_encode32(ch: str) -> tuple:
    """一字→(G_A, G_B, G_C) 三个独立保距投影。"""
    tag = script_tag(ch)
    if tag != 0:
        cp = ord(ch)
        v = (tag << 14) | (cp & 0x3FFF)
        g = Gua(v)
        return (g, g, g)
    return (_encode_A32(ch), _encode_B32(ch), _encode_C32(ch))


# ============================================================
# 位锁定判定
# ============================================================

def _fit_32(a: Gua, b: Gua, m=FIT_MIN) -> bool:
    """a凸∧b凹, >=m位即锁定。32位版本。"""
    return ((a.value & FULL_MASK) & (~b.value & FULL_MASK)).bit_count() >= m


# ============================================================
# 节点
# ============================================================

@dataclass
class Node:
    ch: str
    gA: Gua; gB: Gua; gC: Gua
    tau: int = TAU
    alive: bool = True
    state: str = 'active'
    scars: list = field(default_factory=list)

    def hamming_to(self, other: 'Node') -> int:
        return ((self.gA.value ^ other.gA.value).bit_count() +
                (self.gB.value ^ other.gB.value).bit_count() +
                (self.gC.value ^ other.gC.value).bit_count())

    def axes_match(self, other: 'Node', m=FIT_MIN) -> tuple:
        ok_a = _fit_32(self.gA, other.gA, m) or _fit_32(other.gA, self.gA, m)
        ok_b = _fit_32(self.gB, other.gB, m) or _fit_32(other.gB, self.gB, m)
        ok_c = _fit_32(self.gC, other.gC, m) or _fit_32(other.gC, self.gC, m)
        return ok_a, ok_b, ok_c, sum([ok_a, ok_b, ok_c])


# ============================================================
# 统一系统
# ============================================================

class Tongzi:
    """童子统一离散推理系统 · 32位。

    feed(text) → 编码 → 三金字塔并行 → 池子碰撞 → 三轴归约 → 归档
    """

    def __init__(self, tau=TAU, fit_min=FIT_MIN):
        self.tau = tau
        self.fit_min = fit_min
        self.pyr_A = Pyramid()
        self.pyr_B = Pyramid()
        self.pyr_C = Pyramid()
        self.archives: dict[str, Node] = {}
        self._order: list[str] = []

    def feed(self, text: str):
        """喂入文本。全流程。"""
        nodes = []
        for ch in text:
            if ch not in STROKE_COUNT:
                continue
            if ch in self.archives:
                nodes.append(self.archives[ch])
                continue
            gA, gB, gC = _tri_encode32(ch)
            node = Node(ch, gA, gB, gC, tau=self.tau)
            nodes.append(node)
            self._order.append(ch)

        for i, ni in enumerate(nodes):
            if not ni.alive:
                continue
            candidates = [nj for j, nj in enumerate(nodes) if i != j and nj.alive]
            best = None

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

                # 池子碰撞
                self.pyr_A.flow(Gua(ni.gA.value))
                self.pyr_B.flow(Gua(ni.gB.value))
                self.pyr_C.flow(Gua(ni.gC.value))

                if ni.tau <= 0:
                    break

            if best is not None and best[0] == 3:
                for s in ni.scars:
                    if s.get('result') is None:
                        s['result'] = 'part' if s['axes'] > 0 else 'null'
                for s in ni.scars:
                    if s['target'] == best[1].ch and s['tri']:
                        s['result'] = 'lock'; break
                ni.gA = Gua(ni.gA.value ^ best[1].gA.value)
                ni.gB = Gua(ni.gB.value ^ best[1].gB.value)
                ni.gC = Gua(ni.gC.value ^ best[1].gC.value)
                ni.alive = False; ni.state = 'result'
            elif ni.tau <= 0:
                for s in ni.scars:
                    if s.get('result') is None:
                        s['result'] = 'prune'
                ni.alive = False; ni.state = 'pruned'
            else:
                for s in ni.scars:
                    if s.get('result') is None:
                        s['result'] = 'part' if s['axes'] > 0 else 'null'
                ni.state = 'active'

        for node in nodes:
            self.archives[node.ch] = node

    def ask(self, ch: str) -> dict | None:
        if ch not in self.archives: return None
        n = self.archives[ch]
        return {
            'ch': ch, 'state': n.state, 'tau': n.tau,
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
        if ch not in self.archives: return []
        n = self.archives[ch]
        dists = []
        for c2, n2 in self.archives.items():
            if c2 == ch: continue
            dists.append((n.hamming_to(n2), c2))
        dists.sort()
        return [(c, d) for d, c in dists[:k]]

    def status(self) -> dict:
        r = sum(1 for n in self.archives.values() if n.state == 'result')
        p = sum(1 for n in self.archives.values() if n.state == 'pruned')
        h = sum(1 for n in self.archives.values() if n.state == 'active')
        t = len(self.archives)
        return {
            'total': t, 'result': r, 'pruned': p, 'active': h,
            'result_rate': f'{r/t:.1%}' if t else '0%',
            'prune_rate': f'{p/max(1,r+p):.1%}',
            'pool_sizes': {
                ax: {w: len(getattr(self, f'pyr_{ax}').layers[w].pool)
                     for w in range(2, 11)}
                for ax in 'ABC'
            },
        }

    def report(self):
        s = self.status()
        print(f"童子 v2.1 · 32位 · τ={self.tau} · 阈值>={self.fit_min}位")
        print(f"  归约:{s['result']}  剪枝:{s['pruned']}  悬挂:{s['active']}  总计:{s['total']}")
        print(f"  归约率:{s['result_rate']}  剪枝率:{s['prune_rate']}")
        print(f"\n  池子状态:")
        for axis in 'ABC':
            ps = s['pool_sizes'][axis]
            sizes = ' '.join(f'L{w}:{ps[w]:>3}' for w in range(2, 11))
            print(f"    {axis}轴:  {sizes}")


# ============================================================
# 快速入口
# ============================================================

if __name__ == '__main__':
    tz = Tongzi(tau=5, fit_min=8)
    train = "水河火木天地日月山河金刀剑一二三四五六七八九十万千爱恨生死你我他"
    print(f"喂入 {len(train)} 字符...")
    tz.feed(train)
    tz.report()

    print("\n--- 语义对 ---")
    from tongzi import _fit_32 as fit
    for a,b,label in [
        ("水","河","近义"),("火","水","反义"),("爱","恨","反义"),
        ("生","死","反义"),("一","二","数字"),("爱","水","无关"),
    ]:
        if a not in tz.archives or b not in tz.archives: continue
        na,nb = tz.archives[a], tz.archives[b]
        ok_a = fit(na.gA, nb.gA, 8) or fit(nb.gA, na.gA, 8)
        ok_b = fit(na.gB, nb.gB, 8) or fit(nb.gB, na.gB, 8)
        ok_c = fit(na.gC, nb.gC, 8) or fit(nb.gC, na.gC, 8)
        ax = sum([ok_a, ok_b, ok_c])
        print(f"  {a}-{b} [{label}]  {ax}/3")
