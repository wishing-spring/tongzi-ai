# -*- coding: utf-8 -*-
"""F₂ 因果贯通 — 五流汇合 → 探针扭曲输出"""

from dataclasses import dataclass, field
from typing import List, Optional
from v3.constants import CT_MASK, phi_slice


@dataclass
class CausalState:
    """五流汇合后的因果模拟状态。

    五流:
      规则漂移: 匹配路径的XOR变化趋势
      字符卦象: 当前对话的位模式均值
      经验权重: 历史交互的累积位模式
      刚柔折叠: 生成的"现在"位模式
      引力方向: "好"的目标位模式

    F₂汇合: 加权XOR混合 → causal_state
    因果张力: 各来源的不协调度 → Hamming离散度
    """
    causal_state: int = 0
    causal_confidence: float = 0.0
    causal_tension: float = 0.0

    def simulate(self,
                 rule_drift: int,
                 char_avg: int,
                 experience: int,
                 fold_generated: int,
                 gravity_target: int,
                 tick: int):
        """五流加权混合 → 因果模拟状态。

        权重(v4.3):
          规则漂移  0.20
          字符卦象  0.25
          经验权重  0.15
          刚柔折叠  0.25
          引力方向  0.15
        """
        weights = [0.20, 0.25, 0.15, 0.25, 0.15]
        sources = [rule_drift, char_avg, experience, fold_generated, gravity_target]
        
        # F₂加权混合: 每位从各来源按权重投票
        result = 0
        seed = phi_slice((tick * 67) % 256, 28)

        for bit in range(28):
            # 投票: 该bit在各来源中是0还是1
            votes_1 = 0
            total_weight = 0
            for si, src in enumerate(sources):
                if (src >> bit) & 1:
                    votes_1 += weights[si]
                total_weight += weights[si]
            
            # φ加入微小随机打破平局
            phi_sway = ((seed >> (bit % 28)) & 1) * 0.01
            
            if votes_1 + phi_sway > total_weight / 2:
                result |= (1 << bit)

        self.causal_state = result & CT_MASK

        # 因果一致性: 各来源之间的平均Hamming相似度
        similarities = []
        for i in range(len(sources)):
            for j in range(i+1, len(sources)):
                dist = (sources[i] ^ sources[j]).bit_count() / 28.0
                similarities.append(1.0 - dist)
        
        self.causal_confidence = sum(similarities) / max(len(similarities), 1)
        self.causal_tension = 1.0 - self.causal_confidence


@dataclass
class CausalProbe:
    """因果探针——用因果状态扭曲输出。

    因果张力高 → 重探(因果状态大幅介入)
    因果一致性高 → 轻探(微调)
    """
    base_strength: float = 0.15  # 基础探针强度

    def probe(self, response_ct: int, causal: CausalState, tick: int) -> int:
        """探针注入——因果状态扭曲回答向量。

        strength = 0.15 + tension * 0.3
        """
        strength = self.base_strength + causal.causal_tension * 0.3
        n_bits = max(1, int(28 * strength))

        # φ选择要替换的位
        seed = phi_slice((tick * 89 + int(causal.causal_tension * 100)) % 256, 28)
        probe_mask = 0
        used = set()
        for i in range(n_bits):
            pos = ((seed >> (i * 9)) & 0x1FF) % 28
            if pos not in used:
                probe_mask |= (1 << pos)
                used.add(pos)

        # 探针位替换为因果状态的对应位
        result = (response_ct & ~probe_mask) | (causal.causal_state & probe_mask)
        return result & CT_MASK


# ═══ 五流来源的F₂实现 ═══
@dataclass
class StreamCollector:
    """收集五流输入"""
    rule_drift: int = 0       # 规则路径漂移
    char_avg: int = 0         # 当前对话字符位模式均值
    experience: int = 0       # 经验累积
    fold_ct: int = 0          # 折叠生成的"现在"
    gravity_ct: int = 0       # 引力目标

    def set_rule_drift(self, matched_cts: List[int]):
        """规则漂移 = 最近匹配路径的XOR累积"""
        if len(matched_cts) < 2:
            self.rule_drift = matched_cts[0] if matched_cts else 0
            return
        drift = 0
        for i in range(len(matched_cts) - 1):
            drift ^= matched_cts[i] ^ matched_cts[i+1]
        self.rule_drift = drift & CT_MASK

    def set_char_avg(self, char_cts: List[int]):
        """字符卦象 = F₂中的"均值"——XOR所有输入"""
        if not char_cts:
            return
        avg = 0
        for ct in char_cts:
            avg ^= ct
        self.char_avg = avg & CT_MASK

    def set_experience(self, history_cts: List[int]):
        """经验 = 历史交互的累积XOR"""
        if not history_cts:
            return
        exp = 0
        for ct in history_cts[-20:]:  # 最近20次
            exp = (exp << 1 | (exp >> 27)) ^ ct
        self.experience = exp & CT_MASK
