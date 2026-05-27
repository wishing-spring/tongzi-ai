# -*- coding: utf-8 -*-
"""灵犀折叠·引力·因果 — 刚柔折叠 + 引力拉动 + 五流贯通"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from ref8 import BAGUA, BAGUA_NAMES
from lingxi_tianyuan import TianYuan, Spine


class RigidFlexFold:
    """刚柔折叠: past ⊕ future → generated_now → 偏差"""

    def __init__(self):
        self.past_rigid = '坤'      # 刚性过去虚影
        self.future_flex = '坤'     # 柔性未来虚影(主分支)
        self.generated_now = '坤'   # 折叠产物
        self.deviation = 0.0        # 生成现在 vs 本体的偏差

    def fold(self, ai_ty: TianYuan, ai_spine: Spine, yinyang_freq: float):
        """执行折叠。阴阳频率控制刚柔权重。"""
        # 刚性: 过去=脊骨10步前
        lookback = ai_spine.lookback(10)
        if lookback:
            self.past_rigid = lookback[0][0]
        else:
            self.past_rigid = ai_ty.bagua

        # 柔性: 未来=惯性延续
        inertia = ai_spine.inertia()
        cur_idx = BAGUA_NAMES.index(ai_ty.bagua)
        if inertia > 0.1:
            future_idx = (cur_idx + 1) % 8
        elif inertia < -0.1:
            future_idx = (cur_idx - 1) % 8
        else:
            future_idx = cur_idx
        self.future_flex = BAGUA_NAMES[future_idx]

        self._compute_generated(yinyang_freq, ai_ty)

    def fold_mixed(self, ai_ty: TianYuan, user_spine: Spine,
                   ai_spine: Spine, yinyang_freq: float):
        """双脊混合折叠: 刚性取用户轨迹(多样)，柔性取AI惯性"""
        # 刚性: 用户脊骨10步前
        lookback = user_spine.lookback(10)
        if lookback:
            self.past_rigid = lookback[0][0]
        else:
            self.past_rigid = '坤'

        # 柔性: AI惯性
        inertia = ai_spine.inertia()
        cur_idx = BAGUA_NAMES.index(ai_ty.bagua)
        if inertia > 0.1:
            future_idx = (cur_idx + 1) % 8
        elif inertia < -0.1:
            future_idx = (cur_idx - 1) % 8
        else:
            future_idx = cur_idx
        self.future_flex = BAGUA_NAMES[future_idx]

        self._compute_generated(yinyang_freq, ai_ty)

    def _compute_generated(self, yinyang_freq: float, ai_ty: TianYuan):
        """公用: 折叠加权 → generated_now + deviation"""
        rigid_w = 1.0 - yinyang_freq
        flex_w = yinyang_freq
        past_idx = BAGUA_NAMES.index(self.past_rigid)
        flex_idx = BAGUA_NAMES.index(self.future_flex)
        gen_idx = round(past_idx * rigid_w + flex_idx * flex_w) % 8
        self.generated_now = BAGUA_NAMES[gen_idx]

        actual_idx = BAGUA_NAMES.index(ai_ty.bagua)
        dist = min(abs(gen_idx - actual_idx), 8 - abs(gen_idx - actual_idx))
        self.deviation = dist / 4.0


class Gravity:
    """引力: 向"好"的卦拉。不强制。"""

    GOOD_BAGUA = {'坎', '坤', '艮', '巽', '兑'}  # 水·土·山·风·泽

    def __init__(self, strength: float = 0.5):
        self.strength = strength

    def pull(self, ai_ty: TianYuan) -> str:
        """引力: 好区内自由；离开→70%概率拉回(柔化)"""
        if ai_ty.bagua in self.GOOD_BAGUA:
            return ai_ty.bagua
        cur_idx = BAGUA_NAMES.index(ai_ty.bagua)
        best, best_dist = None, 9
        for g in self.GOOD_BAGUA:
            gi = BAGUA_NAMES.index(g)
            d = min(abs(cur_idx - gi), 8 - abs(cur_idx - gi))
            if d < best_dist:
                best_dist, best = d, g
        # 柔化: 70%拉回，30%允许短暂探访
        import random
        return best if random.random() < self.strength else ai_ty.bagua

    def distance_to_good(self, bagua: str) -> float:
        """到好区的距离 0~1"""
        if bagua in self.GOOD_BAGUA:
            return 0.0
        cur_idx = BAGUA_NAMES.index(bagua)
        dists = []
        for g in self.GOOD_BAGUA:
            gi = BAGUA_NAMES.index(g)
            d = abs(cur_idx - gi)
            dists.append(min(d, 8 - d))
        return min(dists) / 4.0


class CausalChain:
    """因果贯通: 五流汇合 → 因果状态"""

    def __init__(self):
        self.causal_state = '坤'     # 虚拟因果位置
        self.causal_tension = 0.0    # 因果张力 0(和谐)~1(冲突)
        self._history_tension = []   # 张力历史

    def merge(self,
              rule_bagua: str,          # 童子桥过来的卦(规则匹配)
              char_bagua: str,          # 字符卦象(当前输入语义)
              experience_bagua: str,    # 经验权重(脊骨主导卦)
              fold_bagua: str,          # 刚柔折叠产物
              gravity_bagua: str,       # 引力拉动方向
              ) -> None:
        """五流加权汇合 → 因果状态 + 因果张力"""

        # 五流索引
        idxs = [BAGUA_NAMES.index(b) for b in
                [rule_bagua, char_bagua, experience_bagua, fold_bagua, gravity_bagua]]

        # 权重
        weights = [0.25, 0.20, 0.20, 0.20, 0.15]

        # 加权平均索引
        avg_idx = sum(i * w for i, w in zip(idxs, weights)) % 8
        self.causal_state = BAGUA_NAMES[round(avg_idx) % 8]

        # 因果张力 = 五流不一致程度(环形距离方差)
        mean = sum(idxs) / 5.0
        variance = sum(abs(i - mean) for i in idxs) / 5.0
        self.causal_tension = min(1.0, variance / 4.0)

        self._history_tension.append(self.causal_tension)
        if len(self._history_tension) > 20:
            self._history_tension.pop(0)

    def is_tense(self, threshold: float = 0.35) -> bool:
        """是否紧张(需要第九卦介入)"""
        # 连续3次高张力
        if len(self._history_tension) < 3:
            return False
        return all(t > threshold for t in self._history_tension[-3:])


if __name__ == '__main__':
    # 测试折叠
    ty = TianYuan('坤')
    sp = Spine()
    for t in ['离', '坎', '离', '坤', '乾']:
        ty.attract(t, 0.05)
        sp.record(ty, 0)

    fold = RigidFlexFold()
    fold.fold(ty, sp, 0.5)
    print(f"折叠: past={fold.past_rigid} future={fold.future_flex} "
          f"generated={fold.generated_now} 偏差={fold.deviation:.3f}")

    # 测试引力
    g = Gravity(0.15)
    for bagua in ['离', '坎', '震', '坤']:
        pulled = g.pull(TianYuan(bagua))
        print(f"引力: {bagua} → {pulled} (距好={g.distance_to_good(bagua):.0%})")

    # 测试因果
    cc = CausalChain()
    cc.merge('离', '坎', '坤', '艮', '巽')
    print(f"\n因果: 状态={cc.causal_state} 张力={cc.causal_tension:.3f}")
    for _ in range(3):
        cc.merge('离', '离', '离', '离', '离')
    print(f"连续紧张: {cc.is_tense()}")
