# -*- coding: utf-8 -*-
"""F₂ causal probe: five streams merge, probe twists output."""

from dataclasses import dataclass, field
from typing import List
from v3.constants import CT_MASK, phi_slice


@dataclass
class CausalState:
    causal_state: int = 0
    causal_confidence: float = 0.0
    causal_tension: float = 0.0

    def simulate(self, rule_drift: int, char_avg: int, experience: int,
                 fold_generated: int, gravity_target: int, tick: int):
        weights = [0.20, 0.25, 0.15, 0.25, 0.15]
        sources = [rule_drift, char_avg, experience, fold_generated, gravity_target]
        result = 0
        seed = phi_slice((tick * 67) % 256, 28)
        for bit in range(28):
            votes_1 = 0.0
            for si, src in enumerate(sources):
                if (src >> bit) & 1:
                    votes_1 += weights[si]
            phi_sway = ((seed >> (bit % 28)) & 1) * 0.01
            if votes_1 + phi_sway > 0.5:
                result |= (1 << bit)
        self.causal_state = result & CT_MASK
        similarities = []
        for i in range(len(sources)):
            for j in range(i + 1, len(sources)):
                dist = (sources[i] ^ sources[j]).bit_count() / 28.0
                similarities.append(1.0 - dist)
        self.causal_confidence = sum(similarities) / max(len(similarities), 1)
        self.causal_tension = 1.0 - self.causal_confidence


@dataclass
class CausalProbe:
    base_strength: float = 0.15

    def probe(self, response_ct: int, causal: CausalState, tick: int) -> int:
        strength = self.base_strength + causal.causal_tension * 0.3
        n_bits = max(1, int(28 * strength))
        seed = phi_slice((tick * 89) % 256, 28)
        mask = 0
        used = set()
        for i in range(n_bits):
            pos = ((seed >> (i * 9)) & 0x1FF) % 28
            if pos not in used:
                mask |= (1 << pos)
                used.add(pos)
        return (response_ct & ~mask) | (causal.causal_state & mask) & CT_MASK


@dataclass
class StreamCollector:
    sources: dict = field(default_factory=dict)

    def collect(self, **kwargs):
        for k, v in kwargs.items():
            self.sources[k] = v

    def similarity(self, a: str, b: str) -> float:
        av = self.sources.get(a, 0)
        bv = self.sources.get(b, 0)
        if av == 0 and bv == 0:
            return 1.0
        return 1.0 - ((av ^ bv) & CT_MASK).bit_count() / 28.0
