# -*- coding: utf-8 -*-
"""
童子 · 三态因果全系统 v1.8
===========================
锚定态(Anchor) → 活性态(Active) → 结果态(Result)
三轴联合位锁定 · 全候选最优匹配 · A轴笔画高位 · 阈值>=4位
"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi_kernel import Gua, Pyramid, LayerPool
from tools.tri_encode import tri_encode
from tools.strokes import get_strokes, STROKE_COUNT, get_structure, get_component, script_tag

FIT_MIN = 4  # 16位>=4位匹配 — 真拐点，全咬率20.8%

# ============================================================
def _fit_16(a: Gua, b: Gua, m=FIT_MIN) -> bool:
    match = (a.value & 0xFFFF) & (~b.value & 0xFFFF)
    return match.bit_count() >= m


def _encode_A_weighted(ch: str) -> Gua:
    """A轴编码v2: 笔画占高位(6b)，码点占低位(10b)。

    [15:10]=笔画数(0-63) [9:0]=码点低10位
    同笔画字高位一致→汉明距离≤10→位锁定概率大幅提升。
    """
    cp = ord(ch)
    sc = min(get_strokes(ch), 63)
    cp10 = cp & 0x3FF
    return Gua(((sc << 10) | cp10) & 0xFFFF)


def _tri_encode_v2(ch: str) -> tuple:
    """一字→(G_A_v2, G_B, G_C)。仅A轴改变，B/C不动。"""
    tag = script_tag(ch)
    if tag != 0:
        cp = ord(ch)
        v = (tag << 14) | (cp & 0x3FFF)
        g = Gua(v)
        return (g, g, g)

    gA = _encode_A_weighted(ch)
    _, gB, gC = tri_encode(ch)
    return (gA, gB, gC)

# ============================================================
class RenNode:
    """Ren态节点 — 挂在金字塔层上。

    τ: 生命机会
    scars: 咬合疤痕 (持久)
    state: 天/人/地
    """

    def __init__(self, ch: str, gA: Gua, gB: Gua, gC: Gua, tau: int = 5):
        self.ch = ch                # 所属字
        self.gA, self.gB, self.gC = gA, gB, gC
        self.tau = tau
        self.alive = True
        self.scars: list[dict] = []  # [{target, axes, result}]
        self.state = 'active'           # anchor→active→result

    def bite(self, other: 'RenNode') -> bool:
        """三轴联合位锁定。"""
        ok_a = _fit_16(self.gA, other.gA) or _fit_16(other.gA, self.gA)
        ok_b = _fit_16(self.gB, other.gB) or _fit_16(other.gB, self.gB)
        ok_c = _fit_16(self.gC, other.gC) or _fit_16(other.gC, self.gC)
        axes = sum([ok_a, ok_b, ok_c])
        all3 = axes == 3

        scar = {'target': other.ch, 'axes': axes, 'tri': all3, 'A': ok_a, 'B': ok_b, 'C': ok_c}
        self.scars.append(scar)
        self.tau -= 1

        if all3:
            # 归约: XOR融合三轴
            self.gA = Gua(self.gA.value ^ other.gA.value)
            self.gB = Gua(self.gB.value ^ other.gB.value)
            self.gC = Gua(self.gC.value ^ other.gC.value)
            scar['result'] = '归约'
            self.alive = False
            self.state = 'result'
            return True

        if self.tau <= 0:
            scar['result'] = '剪枝'
            self.alive = False
            self.state = 'pruned'
            return False

        scar['result'] = '零' if axes == 0 else '部分'
        return False

    def trace(self) -> str:
        """路径追溯。"""
        parts = []
        for s in self.scars:
            mark = '!' if s['result'] == '归约' else '~' if s['result'] == '部分' else '.'
            parts.append(f"{s['target']}{mark}")
        return '→'.join(parts) if parts else '-'

    def verdict(self) -> str:
        """判决。"""
        if self.state == 'result':
            return f"归约({len(self.scars)}碰)"
        elif self.state == 'pruned':
            return f"剪枝({len(self.scars)}碰)"
        return f"悬挂(τ={self.tau})"


# ============================================================
class RenTongzi:
    """三态因果童子。

    学习: 编码→入金字塔→发活性态→碰撞→归约/剪枝→归档
    提问: 编码→在归档中找→输出路径
    """

    def __init__(self, tau: int = 5):
        self.tau = tau
        self.pyr_A = Pyramid()
        self.pyr_B = Pyramid()
        self.pyr_C = Pyramid()
        self.archives: dict[str, RenNode] = {}  # ch → 最终节点
        self._chars = []

    def learn(self, text: str):
        """喂入文本。锚定→活性→全候选最优匹配→归约/剪枝→归档。"""
        nodes = []
        for ch in text:
            if ch not in STROKE_COUNT:
                continue
            if ch in self.archives:
                nodes.append(self.archives[ch])
                continue

            gA, gB, gC = _tri_encode_v2(ch)
            node = RenNode(ch, Gua(gA.value), Gua(gB.value), Gua(gC.value), tau=self.tau)
            nodes.append(node)
            self._chars.append(ch)

        # 全候选最优: 每个节点检查所有候选，取最佳位锁定
        for i, ni in enumerate(nodes):
            if not ni.alive:
                continue

            best = None  # (axes, target_node)
            candidates = [nj for j, nj in enumerate(nodes) if i != j and nj.alive]

            for nj in candidates:
                ok_a = _fit_16(ni.gA, nj.gA) or _fit_16(nj.gA, ni.gA)
                ok_b = _fit_16(ni.gB, nj.gB) or _fit_16(nj.gB, ni.gB)
                ok_c = _fit_16(ni.gC, nj.gC) or _fit_16(nj.gC, ni.gC)
                axes = sum([ok_a, ok_b, ok_c])

                scar = {'target': nj.ch, 'axes': axes, 'tri': axes == 3,
                        'A': ok_a, 'B': ok_b, 'C': ok_c}
                ni.scars.append(scar)
                ni.tau -= 1

                if axes == 3 and (best is None or axes > best[0]):
                    best = (axes, nj)

                if ni.tau <= 0:
                    break

            # 归约到最优（如有三轴全锁），否则剪枝/悬挂
            if best is not None and best[0] == 3:
                # 记录位锁定——最优疤痕标归约，其余标零/部分
                for s in ni.scars:
                    if s.get('result') is None:
                        s['result'] = '零' if s['axes'] == 0 else '部分'
                for s in ni.scars:
                    if s['target'] == best[1].ch and s['tri']:
                        s['result'] = '归约'
                        break
                ni.gA = Gua(ni.gA.value ^ best[1].gA.value)
                ni.gB = Gua(ni.gB.value ^ best[1].gB.value)
                ni.gC = Gua(ni.gC.value ^ best[1].gC.value)
                ni.alive = False
                ni.state = 'result'
            elif ni.tau <= 0:
                for s in ni.scars:
                    s['result'] = '剪枝' if s.get('result') is None else s['result']
                ni.alive = False
                ni.state = 'pruned'
            else:
                for s in ni.scars:
                    if s.get('result') is None:
                        s['result'] = '零' if s['axes'] == 0 else '部分'
                ni.state = 'active'

        # 入金字塔
        for node in nodes:
            self.pyr_A.flow(node.gA)
            self.pyr_B.flow(node.gB)
            self.pyr_C.flow(node.gC)

        # 归档
        for node in nodes:
            if node.ch not in self.archives:
                self.archives[node.ch] = node

    def ask(self, text: str) -> list[dict]:
        """提问。返回每字的判决+路径+邻居。"""
        results = []
        for ch in text:
            if ch not in STROKE_COUNT:
                results.append({'字': ch, '判决': '无编码', '路径': '-', '邻居': []})
                continue

            if ch in self.archives:
                node = self.archives[ch]
                # 找咬合邻居
                neighbors = []
                for scar in node.scars[:5]:
                    neighbors.append(f"{scar['target']}({scar['axes']}轴){scar['result']}")
                results.append({
                    '字': ch,
                    '判决': node.verdict(),
                    '路径': node.trace(),
                    '状态': node.state,
                    '邻居': neighbors,
                })
            else:
                # 未知字: 编码后入塔找最近
                gA, gB, gC = tri_encode(ch)
                node = RenNode(ch, Gua(gA.value), Gua(gB.value), Gua(gC.value), tau=self.tau)
                # 跟归档中所有节点碰
                for arch_ch, arch_node in self.archives.items():
                    node.bite(arch_node)
                    if not node.alive:
                        break

                # 入塔
                self.pyr_A.flow(node.gA)
                self.pyr_B.flow(node.gB)
                self.pyr_C.flow(node.gC)
                self.archives[ch] = node

                results.append({
                    '字': ch,
                    '判决': node.verdict(),
                    '路径': node.trace(),
                    '状态': node.state,
                    '邻居': [f"{s['target']}({s['axes']}轴){s['result']}" for s in node.scars[:5]],
                })

        return results

    def stats(self) -> dict:
        collapsed = sum(1 for n in self.archives.values() if n.state == '地')
        annihilated = sum(1 for n in self.archives.values() if n.state == '湮')
        hanging = sum(1 for n in self.archives.values() if n.state == '人')
        return {
            '库': len(self.archives),
            '坍缩': collapsed,
            '湮灭': annihilated,
            '悬挂': hanging,
            'A塔': self.pyr_A.stats(),
            'B塔': self.pyr_B.stats(),
            'C塔': self.pyr_C.stats(),
        }


# ============================================================
if __name__ == '__main__':
    print("「Ren态三轴童子」v1.8-r3\n")

    rt = RenTongzi(tau=5)

    # 学习
    train = "水河火木天地日月山河金刀剑一二三四五六七八九十万千"
    rt.learn(train)

    # 提问
    tests = ["水河火", "天地人", "爱恨", "生死", "你我他"]
    for q in tests:
        print(f"「{q}」")
        for r in rt.ask(q):
            print(f"  {r['字']} {r['判决']:<12} {r['路径']}")
        print()

    print(rt.stats())
