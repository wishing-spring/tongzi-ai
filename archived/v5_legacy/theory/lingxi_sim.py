# -*- coding: utf-8 -*-
"""灵犀模拟 — 八卦盘语义系统（简化版，验证融合桥用）"""
import math, time, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from ref8 import BAGUA, BAGUA_NAMES, REF_28BIT
from collections import deque


class LingxiSim:
    """灵犀八卦盘语义系统 — 卦名驱动，不含浮点8D"""

    def __init__(self):
        # 双天元: 用户在哪卦附近 + AI在哪卦附近
        self.user_tianyuan = '坤'   # 出厂: 土·包容
        self.ai_tianyuan = '坎'     # 出厂: 水·和谐

        # 脊骨: 天元轨迹 (卦名队列)
        self.user_spine = deque(maxlen=365)
        self.ai_spine = deque(maxlen=365)

        # 引力: 好的象限
        self.good = {'坎', '坤', '艮'}  # 水·土·山 = 智慧·包容·沉稳

        # 折叠状态
        self.fold_deviation = 0.0

        # 因果状态
        self.causal_tension = 0.0
        self.causal_state = '坤'

        # 对话历史
        self.history = []

        # 阴阳频率（简化: 小时驱动）
        self._tick = 0

    def yinyang_freq(self) -> float:
        """0~1 阴→阳，简化用tick循环模拟"""
        hour = time.localtime().tm_hour
        # 中午12点=阳盛≈1，午夜0点=阴盛≈0.1
        return 0.1 + 0.9 * (math.sin((hour - 6) * math.pi / 12) + 1) / 2

    def receive(self, bridge_result: dict) -> None:
        """接收童子桥的输出: {'name':卦名, 'mood':情绪, ...}"""
        bagua = bridge_result['name']
        self._tick += 1

        # 天元漂移: 吸收交互卦象 5%
        # 用户天元: 往接收卦偏一步
        if self._tick % 3 == 0:
            self._drift_user(bagua)
            self._drift_ai(bagua)

        # 脊骨记录
        self.user_spine.append(self.user_tianyuan)
        self.ai_spine.append(self.ai_tianyuan)

        # 刚柔折叠（简化: 过去偏 vs 未来偏的差距）
        self._fold()

        # 引力拉动
        self._gravity()

        # 因果贯通
        self._causal(bridge_result)

        # 记录
        self.history.append({
            'tick': self._tick,
            'input_bagua': bagua,
            'user_tianyuan': self.user_tianyuan,
            'ai_tianyuan': self.ai_tianyuan,
            'fold_dev': round(self.fold_deviation, 3),
            'causal_tension': round(self.causal_tension, 3),
            'causal_state': self.causal_state,
        })

    def _drift_user(self, bagua):
        """用户天元: 每3tick往输入卦偏一步"""
        cur = BAGUA_NAMES.index(self.user_tianyuan)
        tgt = BAGUA_NAMES.index(bagua)
        if abs(tgt - cur) <= 1:
            self.user_tianyuan = bagua  # 邻近: 直接跳
        else:
            step = 1 if tgt > cur else -1
            self.user_tianyuan = BAGUA_NAMES[cur + step]

    def _drift_ai(self, bagua):
        """AI天元: 往引力方向偏，受输入影响但被引力拉住"""
        cur = BAGUA_NAMES.index(self.ai_tianyuan)
        tgt = BAGUA_NAMES.index(bagua)
        # 输入拉向接收卦
        mid = cur + (1 if tgt > cur else -1)
        mid_name = BAGUA_NAMES[max(0, min(7, mid))]
        # 引力: 如果在不好象限 → 往最近的好卦偏
        if mid_name not in self.good:
            # 找最近的好卦
            best = min(self.good, key=lambda g: abs(BAGUA_NAMES.index(g) - BAGUA_NAMES.index(mid_name)))
            self.ai_tianyuan = best
        else:
            self.ai_tianyuan = mid_name

    def _fold(self):
        """刚柔折叠: 过去天元 vs 推断未来天元的偏差"""
        if len(self.ai_spine) < 3:
            self.fold_deviation = 0.0
            return
        # 过去: 3步前的天元
        past = self.ai_spine[-3]
        # 未来: 当前方向延续2步
        cur = BAGUA_NAMES.index(self.ai_tianyuan)
        past_idx = BAGUA_NAMES.index(past)
        direction = 1 if cur > past_idx else (-1 if cur < past_idx else 0)
        future_idx = cur + direction * 2
        future_idx = max(0, min(7, future_idx))
        future = BAGUA_NAMES[future_idx]
        # 偏差 = |过去→当前| vs |当前→未来| 的不对称程度
        past_gap = abs(cur - past_idx)
        future_gap = abs(future_idx - cur)
        yy = self.yinyang_freq()
        self.fold_deviation = abs(past_gap - future_gap) / 7.0 * yy

    def _gravity(self):
        """引力: AI天元如果不在好卦 → 拉回"""
        if self.ai_tianyuan not in self.good:
            best = min(self.good, key=lambda g: abs(BAGUA_NAMES.index(g) - BAGUA_NAMES.index(self.ai_tianyuan)))
            if abs(BAGUA_NAMES.index(best) - BAGUA_NAMES.index(self.ai_tianyuan)) <= 1:
                self.ai_tianyuan = best

    def _causal(self, bridge_result):
        """因果贯通: 折叠偏差 + 引力距离 + 输入语义 → 因果张力"""
        # 引力距离
        cur = BAGUA_NAMES.index(self.ai_tianyuan)
        grav_dist = min(abs(cur - BAGUA_NAMES.index(g)) for g in self.good) / 7.0

        # 输入语义权重
        mood_map = {'坚定': 0.2, '开心': 0.1, '激动': 0.7, '不安': 0.6,
                    '柔和': 0.2, '忧惧': 0.5, '沉稳': 0.1, '平和': 0.05}
        mood_w = mood_map.get(bridge_result.get('mood', '平和'), 0.3)

        self.causal_tension = (self.fold_deviation * 0.3 +
                               grav_dist * 0.3 +
                               mood_w * 0.4)

    def speak(self) -> str:
        """输出: 基于当前天元+因果状态的回应"""
        yy = self.yinyang_freq()
        mood = BAGUA[self.ai_tianyuan]['mood']

        if self.causal_tension > 0.5:
            tone = "我有点不安，但"
        elif yy > 0.7:
            tone = "感觉挺好的，"
        elif yy < 0.3:
            tone = "夜深了，"
        else:
            tone = ""

        return f"[{tone}当前AI状态: {self.ai_tianyuan}({BAGUA[self.ai_tianyuan]['meaning']}) "
        f"· {mood} · 偏差{self.fold_deviation:.2f} · 张力{self.causal_tension:.2f}]"


# ── 测试 ──
if __name__ == '__main__':
    lx = LingxiSim()
    from bridge import project

    inputs = [
        (0x0000005, "坎·水·危险"),
        (0x0000002, "离·火·急躁"),
        (0x0000007, "坤·土·包容"),
        (0x0000005, "坎·水·危险"),
        (0x0000000, "乾·天·刚健"),
    ]

    for ct, desc in inputs:
        r = project(ct)
        lx.receive(r)
        print(f"输入 {desc} → 桥投影 {r['name']} → {lx.speak()}")

    print(f"\n用户脊骨: {list(lx.user_spine)}")
    print(f"AI脊骨:   {list(lx.ai_spine)}")
