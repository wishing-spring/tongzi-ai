# -*- coding: utf-8 -*-
"""F₂ 双天元 — 用户身份 + AI身份 · 28bit位空间"""

from dataclasses import dataclass
from typing import Optional
from v3.constants import CT_MASK, phi_slice, PHI_BITS


@dataclass
class TianYuan:
    """天元 = 八卦盘的中心点。28bit F₂值。

    不存8D向量。存一个28位值——在整个位空间中的位置。
    演化: φ引导的位替换——保留大部分旧位,吸收少量新位。
    """
    ct: int = 0          # 28bit位置
    last_move: int = 0   # 上次移动tick

    def evolve(self, input_ct: int, tick: int, rate: float = 0.05):
        """吸收输入，缓慢偏移。

        rate=0.05 → 约20次交互后显著偏移。
        F₂等效: 选 rate*28 ≈ 1-2 个bit位，用输入的对应位替换。
        """
        n_bits = max(1, int(28 * rate))  # 替换位数
        # φ切片选择要替换的bit位置
        seed = phi_slice((tick * 13 + self.last_move * 7) % 256, 28)
        mask = 0
        used = set()
        for i in range(n_bits):
            pos = ((seed >> (i * 9)) & 0x1FF) % 28
            if pos not in used:
                mask |= (1 << pos)
                used.add(pos)
        
        # 输入bit替换旧bit
        self.ct = (self.ct & ~mask) | (input_ct & mask)
        self.ct &= CT_MASK
        self.last_move = tick

    def distance_to(self, other_ct: int) -> int:
        """Hamming距离——在F₂空间中离目标多远"""
        return (self.ct ^ other_ct).bit_count()

    def direction_to(self, target_ct: int) -> int:
        """差异向量——哪些bit不同"""
        return self.ct ^ target_ct


# ═══ 出厂设定 ═══
def default_user_tianyuan() -> TianYuan:
    """用户天元出厂: 零位(中性)"""
    return TianYuan(ct=0)

def default_ai_tianyuan() -> TianYuan:
    """AI天元出厂: 水+土偏向(和谐+智慧)

    v4.3设定: 坎(水/和谐)0.7, 坤艮(土/智慧)0.6
    F₂等效: 高位置偏向特定bit模式
    """
    # 和谐+智慧的bit模式: 位模式偏向均匀分布而非极端
    # 用φ生成一个"温和"的初始位置
    ai_ct = 0
    for i in range(28):
        if PHI_BITS[(i * 17) % len(PHI_BITS)] == '1':
            ai_ct |= (1 << i)
    return TianYuan(ct=ai_ct & CT_MASK)
