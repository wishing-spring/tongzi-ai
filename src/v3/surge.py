# -*- coding: utf-8 -*-
"""涌動 — F₂等效灵犀八卦盘旋转"""

from .constants import phi_slice, CT_MASK, rotl_group

SURGE_CYCLE = 3  # 每 N tick 一涌動相
WINDOW_BITS = 16  # 匹配窗口大小(28位中选16)

# 四花色涌動速率
_RATES = {
    0: [1, 3, 5, 7],
    1: [2, 5, 7, 11],
    2: [3, 7, 11, 13],
    3: [5, 11, 13, 17],
}

_BASE_MASK = ((1 << WINDOW_BITS) - 1) << 0  # 低14位窗口


def surge_mask(tick: int) -> int:
    """涌動窗口掩码 — 每相旋转，只匹配窗口内比特。

    灵犀等效: 八卦盘旋转 = 匹配窗口在F₂空间滑动。
    同对卦在不同涌動相看不同比特 → 持续产生新匹配。
    """
    phase = tick // SURGE_CYCLE
    shift = (phase * 3) % 28
    mask = rotl_group(_BASE_MASK, 0, 28, shift)
    return mask & CT_MASK


def surge(v: int, tick: int) -> int:
    """涌動变换 — 用于生子时注入涌動签名。"""
    phase = tick // SURGE_CYCLE
    sid = (v >> 28) & 0xF
    rates = _RATES.get(sid, [1, 3, 5, 7])

    from .constants import ID_MASK
    _GROUPS = [(0, 8), (8, 8), (16, 8), (24, 4)]
    r = v
    for (gs, gz), rate in zip(_GROUPS, rates):
        r = rotl_group(r, gs, gz, phase * rate)

    weather = phi_slice((phase * 13 + sid * 37) % 256, 28)
    r = (r & ID_MASK) | ((r & CT_MASK) ^ weather)
    return r
