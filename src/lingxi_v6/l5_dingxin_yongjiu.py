# -*- coding: utf-8 -*-
"""定心坠子 + YongJiu — 5值门控 · 游离卦元探针 · 零浮点"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from guayuan import MASK28, hamming, xor_reduce, gua_hash, nearest, random_gua, pool_average


class DingXinZhuizi:
    """定心坠子: 5维价值门控 + 双重画像"""

    VALUES = ['真诚', '仁爱', '智慧', '勇气', '和谐']
    ELEMENTS = ['木', '火', '土', '金', '水']

    def __init__(self):
        # 5个价值卦元
        self.value_guas = {v: gua_hash(v) for v in self.VALUES}
        # 门控阈值
        self.th_guide = 0.3
        self.th_accept = 0.5
        self.th_caution = 0.7
        # 画像
        self.user_tianyuan = gua_hash("用户")   # 用户天元
        self.ai_persona = self._init_persona()  # AI人格
        self.tick = 0

    def _init_persona(self) -> int:
        """AI人格 = 5值均匀加权XOR"""
        r = 0
        for v in self.VALUES:
            r ^= self.value_guas[v]
        return r & MASK28

    def align(self, candidate: int) -> tuple[str, float]:
        """门控对齐: candidate卦元 vs 5维价值 → (等级, avg_dist)"""
        total_d = 0
        for v in self.VALUES:
            total_d += hamming(candidate, self.value_guas[v])
        avg = total_d / 5.0 / 28.0

        if avg < self.th_guide:
            return 'GUIDE', avg
        elif avg < self.th_accept:
            return 'ACCEPT', avg
        elif avg < self.th_caution:
            return 'CAUTION', avg
        else:
            return 'REJECT', avg

    def modulate_prob(self, candidate: int, base_prob: float) -> float:
        """调节跃迁概率"""
        level, _ = self.align(candidate)
        factors = {'GUIDE': 1.5, 'ACCEPT': 1.0, 'CAUTION': 0.5, 'REJECT': 0.0}
        return base_prob * factors[level]

    def update_user(self, attractor: int):
        """更新用户天元"""
        self.user_tianyuan ^= (attractor >> 4) & MASK28
        self.tick += 1

    def update_persona(self, feedback_gua: int, weight: float = 0.05):
        """AI人格微调"""
        self.ai_persona ^= (feedback_gua >> 3) & MASK28


class YongJiu:
    """第九卦: 游离卦元探针 · 三才检测 · 双井势 · 场骤冷"""

    def __init__(self):
        self.gua = 0x0FFFFFFF          # 游离卦元 (全1=全可能性)
        self.shallow = 0               # 浅井结果
        self.deep = 0                  # 深井结果
        self.tick = 0
        self.trigger_count = 0         # 连续触发次数
        self.L_threshold = 0.35        # 信息丢失触发阈值
        self._history: list[int] = []  # 最近256卦元采样

    # ── 三才检测 ──
    def three_talents(self, pool: list[int]) -> float:
        """天·地·人 三才联合检测 → L ∈ [0,1]"""
        if not pool or len(pool) < 4:
            return 0.0

        sample = pool[:min(len(pool), 256)]
        self._history = sample

        # 天: XOR归约 → bit_count = 位级熵
        total = xor_reduce(sample)
        entropy = total.bit_count() / 28.0

        # 地: 唯一卦元占比
        unique = len(set(sample))
        coverage = unique / len(sample)

        # 人: 平均位密度
        density = sum(g.bit_count() for g in sample) / (len(sample) * 28.0)

        L = entropy * 0.5 + (1.0 - coverage) * 0.2 + density * 0.3
        return L

    # ── 双井势 ──
    def tick_once(self, attractor: int, pool: list[int]) -> dict:
        """每tick: 双井徘徊 → 分岔检测 → 可能触发"""
        self.tick += 1

        # 浅井 (惯性)
        self.shallow = (self.gua ^ attractor) & MASK28

        # 深井 (变异)
        self.deep = (self.gua ^ ((attractor << 7) ^ (attractor >> 14))) & MASK28

        # 徘徊: 偶数tick用浅井，奇数用深井
        if self.tick % 2 == 0:
            self.gua = self.shallow
        else:
            self.gua = self.deep

        # 分岔检测
        split = hamming(self.shallow, self.deep)

        # 三才检测
        L = self.three_talents(pool)

        triggered = False
        quenched = False
        if L > self.L_threshold or split >= 20:
            triggered = True
            self.trigger_count += 1
        elif split < 4:
            self.trigger_count = max(0, self.trigger_count - 1)

        # 场骤冷
        if self.trigger_count >= 3:
            quenched = True
            self._quench(pool)

        completion = 0
        if split >= 20:
            completion = (self.shallow ^ self.deep) & MASK28

        return {
            'gua': self.gua,
            'split': split,
            'L': L,
            'triggered': triggered,
            'quench': quenched,
            'completion': completion,
        }

    def _quench(self, pool: list[int]):
        """场骤冷: 归零 → 从池重建"""
        self.gua = 0
        if pool:
            sample = pool[:128]
            self.gua = xor_reduce(sample)
        self.trigger_count = 0


if __name__ == '__main__':
    # 定心坠子
    dxz = DingXinZhuizi()
    for gua in [0x1234567, 0xABCDEF0, 0x5555555, 0x0000000]:
        level, _ = dxz.align(gua)
        print(f"  定心: gua=0x{gua:07X} → {level}")

    # YongJiu
    yj = YongJiu()
    pool = [random_gua(i) for i in range(200)]
    print(f"\n  YongJiu初始: 0x{yj.gua:07X}")
    for i in range(6):
        st = yj.tick_once(attractor=random_gua(i * 99), pool=pool)
        print(f"  tick{i+1}: split={st['split']} L={st['L']:.3f} "
              f"trig={st['triggered']} quench={st['quench']}")
