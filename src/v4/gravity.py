# -*- coding: utf-8 -*-
"""F₂ 定心坠子引力 — "好"的方向 · 不强制,是偏移"""

from dataclasses import dataclass
from v3.constants import CT_MASK, phi_slice, PHI_BITS


# ═══ 出厂设定: "好"的方向 ═══
# v4.3: 水(坎)0.7 + 土(坤艮)0.6 + 木(震巽)0.2 + 火(离)0.3 + 金(乾兑)0.0
# 和谐+智慧+真诚, 不过度勇进
#
# F₂等效: "好"的28bit目标模式
# 使用φ生成一个代表"温和+智慧"的位模式
def _make_good_target() -> int:
    """生成出厂"好"的目标位模式"""
    ct = 0
    # 使用φ的不同相位生成温和的位分布
    for i in range(28):
        # 水(和谐)偏向: 位0-6均匀低密度
        # 土(智慧)偏向: 位7-13稳定模式
        # 木(真诚)偏向: 位14-20自然分布  
        # 火(仁爱)偏向: 位21-27温暖分布
        phase = (i * 17 + i // 7 * 31) % len(PHI_BITS)
        if PHI_BITS[phase] == '1':
            ct |= (1 << i)
    return ct & CT_MASK

GOOD_TARGET = _make_good_target()


@dataclass
class Gravity:
    """定心坠子引力。

    不强制。是偏移——副天元体内的折叠自动向引力方向偏。
    蚯蚓不需要懂"好"。只需要被一个看不见的力拉着。

    F₂: pull_mask选择N个bit → 往target方向翻转
    """
    target_ct: int = GOOD_TARGET
    strength: float = 0.15  # 出厂引力强度

    def pull(self, ct: int, tick: int) -> int:
        """引力偏移——把ct往target方向拉。

        选 strength*28 ≈ 4 个bit, 若ct与target不同则翻转。
        """
        n_bits = max(1, int(28 * self.strength))
        diff = ct ^ self.target_ct  # 哪些位不同

        if diff == 0:
            return ct  # 已在目标位置,不用拉

        # φ选择要拉哪几个bit
        seed = phi_slice((tick * 53) % 256, 28)
        pull_mask = 0
        used = set()
        # 只在不同的bit中选择
        diff_positions = [i for i in range(28) if (diff >> i) & 1]

        for i in range(min(n_bits, len(diff_positions))):
            idx = ((seed >> (i * 9)) & 0x1FF) % len(diff_positions)
            pos = diff_positions[idx]
            if pos not in used:
                pull_mask |= (1 << pos)
                used.add(pos)

        # 翻转选中的bit → 向target靠近
        result = ct ^ pull_mask
        return result & CT_MASK

    def distance_to_good(self, ct: int) -> int:
        """离"好"有多远 (Hamming)"""
        return (ct ^ self.target_ct).bit_count()

    def quadrance(self, ct: int) -> str:
        """在"好"的哪个方向"""
        dist = self.distance_to_good(ct)
        if dist <= 3:
            return "善域"
        elif dist <= 7:
            return "边缘"
        elif dist <= 14:
            return "偏移"
        else:
            return "远离"


# ═══ 围栏: 禁词(坏的硬拦截) ═══
# F₂等效: 禁词位模式——若输出ct与禁词模式Hamming距离过近则拦截
FORBIDDEN_PATTERNS = [
    # 用φ生成13个"坏"的位模式作为禁区
]

def _make_forbidden() -> list:
    result = []
    for j in range(13):
        ct = 0
        for i in range(28):
            phase = (i * 19 + j * 47 + 100) % len(PHI_BITS)
            if PHI_BITS[phase] == '1':
                ct |= (1 << i)
        result.append(ct & CT_MASK)
    return result

FORBIDDEN_PATTERNS = _make_forbidden()

def is_forbidden(ct: int, threshold: int = 5) -> bool:
    """输出是否接近禁区 (Hamming距离 < threshold)"""
    for pattern in FORBIDDEN_PATTERNS:
        if (ct ^ pattern).bit_count() < threshold:
            return True
    return False
