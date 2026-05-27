# -*- coding: utf-8 -*-
"""V4 full-state output. Returns complete internal state, not just one word."""

from dataclasses import dataclass, field
from typing import List, Dict
from collections import Counter


@dataclass
class V4Response:
    input_text: str = ""
    nearest_char: str = ""
    hamming_dist: int = 0

    # dual tianyuan
    user_tianyuan_ct: int = 0
    ai_tianyuan_ct: int = 0
    user_spine_points: int = 0
    ai_spine_points: int = 0
    user_inertia_bits: int = 0
    ai_delta_bits: int = 0

    # rigid-flex fold
    fold_deviation: float = 0.0
    fold_trend: str = ""
    past_rigid_ct: int = 0
    future_main_ct: int = 0
    generated_now_ct: int = 0
    fold_gap_hamming: int = 0

    # gravity
    hamming_to_good: int = 0
    good_quadrant: str = ""
    forbidden: bool = False
    gravity_pull_applied: int = 0

    # causal
    causal_tension: float = 0.0
    causal_confidence: float = 0.0
    causal_state_ct: int = 0
    stream_sources: Dict[str, int] = field(default_factory=dict)
    stream_similarity: Dict[str, float] = field(default_factory=dict)

    # yinyang clock
    yinyang_freq: float = 0.0
    yinyang_state: str = ""

    # surge pool
    surge_size: int = 0
    native_count: int = 0

    # eco pools
    pools_summary: List[str] = field(default_factory=list)

    # collision
    total_births: int = 0
    total_solid: int = 0
    attractors: List[str] = field(default_factory=list)


def render_response(r: V4Response) -> str:
    lines = [
        "+" + "-" * 46 + "+",
        f"|  V4 Response",
        "+" + "-" * 46 + "+",
        f"|  input : {r.input_text}",
        f"|  reply : {r.nearest_char}" + (f" (hamming {r.hamming_dist})" if r.hamming_dist else ""),
        f"|",
        f"|  clock : {r.yinyang_state} freq={r.yinyang_freq:.2f}",
        f"|",
        f"|  --- dual tianyuan ---",
        f"|  user  : 0x{r.user_tianyuan_ct:07x} ({r.user_spine_points} spine pts)",
        f"|  AI    : 0x{r.ai_tianyuan_ct:07x} ({r.ai_spine_points} spine pts)",
        f"|  delta : {r.ai_delta_bits} bits",
        f"|",
        f"|  --- fold ---",
        f"|  dev   : {r.fold_deviation:.3f} ({r.fold_trend})",
        f"|  gap   : {r.fold_gap_hamming} hamming",
        f"|",
        f"|  --- gravity ---",
        f"|  dist  : {r.hamming_to_good}",
        f"|  pull  : {r.gravity_pull_applied} bits",
        f"|  safe  : {'YES' if not r.forbidden else 'FORBIDDEN'}",
        f"|",
        f"|  --- causal ---",
        f"|  conf  : {r.causal_confidence:.3f} tension={r.causal_tension:.3f}",
        f"|",
        f"|  --- pools ---",
        f"|  surge : {r.surge_size} gua ({r.native_count} native)",
        f"|  births: {r.total_births} solid={r.total_solid}",
        f"|",
        f"|  attractors: {', '.join(r.attractors[:5]) if r.attractors else '-'}",
        f"+{'-' * 46}+",
    ]
    return '\n'.join(lines)
