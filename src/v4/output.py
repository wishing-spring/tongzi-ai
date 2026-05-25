# -*- coding: utf-8 -*-
"""灵悉 v4 · 全态输出 · 不返回单字,返回完整内在状态"""

from dataclasses import dataclass, field
from typing import List, Dict
from collections import Counter


@dataclass
class V4Response:
    """一次对话的完整输出。

    不是回一个字。是把系统此刻的全部内在状态摊开。
    """
    # ── 原始输出 ──
    input_text: str = ""
    nearest_char: str = ""       # 原始回答映射到的最近字
    hamming_dist: int = 0        # 离最近字的Hamming距离

    # ── 双天元 ──
    user_tianyuan_ct: int = 0
    ai_tianyuan_ct: int = 0
    user_spine_points: int = 0
    ai_spine_points: int = 0
    user_inertia_bits: int = 0   # 用户天元最近惯性(活跃bit数)
    ai_delta_bits: int = 0       # AI天元本轮偏移bit数

    # ── 刚柔折叠 ──
    fold_deviation: float = 0.0
    fold_trend: str = ""
    past_rigid_ct: int = 0
    future_main_ct: int = 0
    generated_now_ct: int = 0
    fold_gap_hamming: int = 0    # 生成的现在 vs 实际AI天元 Hamming距离

    # ── 引力 ──
    hamming_to_good: int = 0
    good_quadrant: str = ""
    forbidden: bool = False
    gravity_pull_applied: int = 0  # 本轮的引力位翻转数

    # ── 因果贯通 ──
    causal_tension: float = 0.0
    causal_confidence: float = 0.0
    causal_state_ct: int = 0
    stream_sources: Dict[str, int] = field(default_factory=dict)  # 五流各自的值
    stream_similarity: Dict[str, float] = field(default_factory=dict)  # 流间相似度

    # ── 阴阳时钟 ──
    yinyang_freq: float = 0.0
    yinyang_state: str = ""

    # ── 涌动池 ──
    surge_size: int = 0
    native_count: int = 0

    # ── 生态池 ──
    pools_summary: List[str] = field(default_factory=list)

    # ── 碰撞 ──
    total_births: int = 0
    total_solid: int = 0
    attractors: List[str] = field(default_factory=list)  # 当前吸引子top5


def render_response(r: V4Response) -> str:
    """全态渲染——中文面板"""

    lines = []
    lines.append("╔══════════════════════════════════════════════╗")
    lines.append("║           灵 悉 回 应                          ║")
    lines.append("╠══════════════════════════════════════════════╣")

    # 用户输入
    lines.append(f"║  你说: {r.input_text}")
    lines.append(f"║")

    # 原始回应
    tag = r.nearest_char if r.hamming_dist == 0 else f"≈{r.nearest_char}(±{r.hamming_dist})"
    lines.append(f"║  回应: {tag}")
    lines.append(f"║")

    # 时钟
    lines.append(f"║  ⏰ {r.yinyang_state} 频率{r.yinyang_freq:.2f}")
    lines.append(f"║")

    # 天元
    lines.append(f"║  ── 双天元 ──")
    lines.append(f"║  用户: 0x{r.user_tianyuan_ct:07x}  脊骨{r.user_spine_points}点  惯性{r.user_inertia_bits}bit")
    lines.append(f"║  AI:   0x{r.ai_tianyuan_ct:07x}  脊骨{r.ai_spine_points}点  本轮Δ{r.ai_delta_bits}bit")
    lines.append(f"║")

    # 折叠
    lines.append(f"║  ── 刚柔折叠 ──")
    lines.append(f"║  偏差: {r.fold_deviation:.3f} ({r.fold_trend})  沟壑: {r.fold_gap_hamming}bit")
    lines.append(f"║  过去虚影: 0x{r.past_rigid_ct:07x}")
    lines.append(f"║  未来主线: 0x{r.future_main_ct:07x}")
    lines.append(f"║  生成现在: 0x{r.generated_now_ct:07x}")
    lines.append(f"║")

    # 引力
    lines.append(f"║  ── 引力 ──")
    quad = r.good_quadrant
    lines.append(f"║  离「善」: {r.hamming_to_good}bit  区域: {quad}")
    lines.append(f"║  引力翻转: {r.gravity_pull_applied}bit  {'⚠️禁区边缘!' if r.forbidden else '✓安全'}")
    lines.append(f"║")

    # 因果
    lines.append(f"║  ── 因果贯通 ──")
    lines.append(f"║  张力: {r.causal_tension:.2f}  一致性: {r.causal_confidence:.2f}")
    lines.append(f"║  五流汇合: 0x{r.causal_state_ct:07x}")
    for name, val in r.stream_sources.items():
        lines.append(f"║    {name}: 0x{val:07x}")
    lines.append(f"║")

    # 系统规模
    lines.append(f"║  ── 系统 ──")
    lines.append(f"║  涌池: {r.surge_size}卦({r.native_count}原生)  {r.total_births}孩子 {r.total_solid}固化")
    for ps in r.pools_summary:
        lines.append(f"║  {ps}")

    # 吸引子
    if r.attractors:
        lines.append(f"║")
        lines.append(f"║  吸引子: {' · '.join(r.attractors)}")

    lines.append(f"╚══════════════════════════════════════════════╝")
    return '\n'.join(lines)
