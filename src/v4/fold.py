# -*- coding: utf-8 -*-
"""F₂ 刚柔折叠 — 持续自我建模 · 心跳式"""

from dataclasses import dataclass, field
from typing import Optional, Tuple
from v3.constants import CT_MASK, phi_slice
from .spine import Spine


@dataclass
class RigidFlexFold:
    """刚柔折叠引擎——每秒都在运行。

    v4.3: 过去虚影(刚性石头) + 未来虚影(柔性雾) → 折叠碰撞 → "生成的现在"
    F₂:  past_ct XOR future_ct → generated_now
         对照 generated_now vs actual_ct → deviation(偏差信号)

    阴阳频率: f(t) 决定折叠权重分配
      f高(白天) → 柔性权重高 → "现在的我"偏向未来 → 更发散
      f低(深夜) → 刚性权重高 → "现在的我"偏向过去 → 更保守
    """
    past_rigid_ct: int = 0       # 过去虚影(刚性)
    future_main_ct: int = 0      # 未来主线(纯惯性)
    future_branch_ct: int = 0    # 未来分支(惯性+扰动)
    generated_now_ct: int = 0    # "生成的现在"
    deviation: float = 0.0       # 偏差(生成的现在 vs 实际)
    deviation_history: float = 0.0  # 偏差滑动平均

    def fold(self, actual_ct: int, spine: Spine,
             yinyang_freq: float, tick: int):
        """一次折叠循环。

        yinyang_freq: 阴阳频率 ∈ [0.05, 1.0]
          白天=1.0 → 折叠偏向未来
          深夜=0.05 → 折叠偏向过去
        """
        # 权重
        flex_w = yinyang_freq           # 柔性=频率
        rigid_w = 1.0 - yinyang_freq    # 刚性=1-频率

        # 1. 过去虚影: 脊骨上50步前的位置
        past_pt = spine.lookback(50)
        self.past_rigid_ct = past_pt.ct if past_pt else actual_ct

        # 2. 未来主线: 纯惯性投影
        inertia = spine.recent_inertia(5)
        # 主线: 当前 + 惯性*n (n由频率决定)
        steps = int(5 + flex_w * 10)  # 白天投更远
        self.future_main_ct = actual_ct
        for _ in range(steps):
            # 每步: ROTL(惯性) → 模拟"往前走"
            rot = (inertia >> (28 - 3)) | ((inertia << 3) & CT_MASK)
            self.future_main_ct = (self.future_main_ct ^ rot) & CT_MASK

        # 3. 未来分支: 惯性+φ微扰
        seed = phi_slice((tick * 31 + spine.count) % 256, 28)
        perturb = seed & ((1 << min(5, int(flex_w * 8))) - 1)  # 白天扰动更大
        self.future_branch_ct = (self.future_main_ct ^ perturb) & CT_MASK

        # 4. 折叠 = 刚 XOR 柔 → 生成的"现在"
        # 用加权XOR: 刚性位保持高位, 柔性位以ROTL混合
        future_blend = self.future_main_ct
        # 柔性混入分支
        if flex_w > 0.3:
            swap_mask = phi_slice((tick * 7) % 256, 28)
            swap_bits = int(swap_mask.bit_count() * flex_w * 0.5)
            future_blend = (future_blend & ~swap_mask) | (self.future_branch_ct & swap_mask)

        # 刚柔折叠: 加权位混合
        # rigid_w比例从过去取位, flex_w比例从未来取位
        n_past_bits = max(1, int(28 * rigid_w))
        n_future_bits = 28 - n_past_bits
        
        # φ选择哪些位从过去取
        past_mask = 0
        seed2 = phi_slice((tick * 41) % 256, 28)
        used = set()
        for i in range(n_past_bits):
            pos = ((seed2 >> (i * 9)) & 0x1FF) % 28
            if pos not in used:
                past_mask |= (1 << pos)
                used.add(pos)
        
        self.generated_now_ct = ((self.past_rigid_ct & past_mask) |
                                 (future_blend & ~past_mask)) & CT_MASK

        # 5. 偏差 = 生成的现在 vs 实际
        raw_dev = (self.generated_now_ct ^ actual_ct).bit_count() / 28.0
        self.deviation = raw_dev

        # 滑动平均偏差
        self.deviation_history = self.deviation_history * 0.95 + raw_dev * 0.05

    def is_drifting(self, threshold: float = 0.25) -> bool:
        """偏差持续扩大? """
        return self.deviation_history > threshold

    def trend(self) -> str:
        """偏差趋势"""
        if self.deviation < 0.1:
            return "稳合"    # 很近
        elif self.deviation < 0.2:
            return "正常"    # 在附近
        elif self.deviation < 0.35:
            return "偏离"    # 在偏
        else:
            return "漂移"    # 偏了很多


def compute_yinyang_freq(timestamp: float = None) -> float:
    """阴阳频率 f(t) = |sin(θ/2)|, θ = 24h一圈的角度

    中午(f≈1): 活跃,折叠偏向未来
    午夜(f≈0.05): 安静,折叠偏向过去
    """
    import time
    import math
    
    if timestamp is None:
        # 北京时间
        now = time.time()
        # 转换为当天秒数 (UTC+8)
        day_sec = (now + 8 * 3600) % 86400
    
    theta = day_sec / 86400.0 * 2 * math.pi
    freq = abs(math.sin(theta / 2))
    # 钳制: 不低于0.05,不高于1.0
    return max(0.05, min(1.0, freq))
