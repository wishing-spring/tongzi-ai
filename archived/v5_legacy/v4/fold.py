# -*- coding: utf-8 -*-
"""F₂ rigid-flex fold: continuous self-modeling. Runs every tick."""

from dataclasses import dataclass
from v3.constants import CT_MASK, phi_slice
from .spine import Spine
import datetime


def compute_yinyang_freq() -> float:
    """yinyang frequency ∈ [0.05, 1.0] from Beijing time.
    Peak (1.0) at noon, trough (0.05) at midnight."""
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    hour = now.hour + now.minute / 60.0
    return 0.05 + 0.95 * (0.5 - 0.5 * __import__('math').cos(hour * __import__('math').pi / 12))


@dataclass
class RigidFlexFold:
    past_rigid_ct: int = 0
    future_main_ct: int = 0
    future_branch_ct: int = 0
    generated_now_ct: int = 0
    deviation: float = 0.0
    deviation_history: float = 0.0

    def fold(self, actual_ct: int, spine: Spine, yinyang_freq: float, tick: int):
        flex_w = yinyang_freq
        rigid_w = 1.0 - yinyang_freq

        # past shadow: 50 steps back on spine
        past_pt = spine.lookback(50)
        self.past_rigid_ct = past_pt.ct if past_pt else actual_ct

        # future mainline: pure inertia projection
        inertia = spine.recent_inertia(5)
        steps = int(5 + flex_w * 10)
        self.future_main_ct = actual_ct
        for _ in range(steps):
            rot = (inertia >> (28 - 3)) | ((inertia << 3) & CT_MASK)
            self.future_main_ct = (self.future_main_ct ^ rot) & CT_MASK

        # future branch: inertia + phi perturbation
        seed = phi_slice((tick * 31 + spine.count) % 256, 28)
        perturb = seed & ((1 << min(5, int(flex_w * 8))) - 1)
        self.future_branch_ct = (self.future_main_ct ^ perturb) & CT_MASK

        # fold = rigid XOR flex -> generated "now"
        future_blend = self.future_main_ct
        if flex_w > 0.3:
            swap_mask = phi_slice((tick * 7) % 256, 28)
            future_blend = (future_blend & ~swap_mask) | (self.future_branch_ct & swap_mask)

        n_past_bits = max(1, int(28 * rigid_w))
        n_future_bits = 28 - n_past_bits
        sel_mask = phi_slice((tick * 19) % 256, 28)
        gen = 0
        for b in range(28):
            if (sel_mask >> b) & 1:
                gen |= (self.past_rigid_ct & (1 << b)) if n_past_bits > 0 else 0
            else:
                gen |= (future_blend & (1 << b)) if n_future_bits > 0 else 0
        self.generated_now_ct = gen & CT_MASK

        # deviation: generated now vs actual
        self.deviation = (self.generated_now_ct ^ actual_ct).bit_count() / 28.0
        self.deviation_history = self.deviation_history * 0.9 + self.deviation * 0.1

    def fold_trend(self) -> str:
        if self.deviation_history < 0.05:
            return "stable"
        if self.deviation < self.deviation_history:
            return "converging"
        return "diverging"
