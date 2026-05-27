# -*- coding: utf-8 -*-
"""桥 · Hamming投影 — 童子28bit→灵犀卦名+语义"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from ref8 import REF_28BIT, BAGUA, BAGUA_NAMES


def hamming(a: int, b: int) -> int:
    """popcount(a XOR b)"""
    return (a ^ b).bit_count()


def project(ct: int) -> dict:
    """童子28位吸引子 → 最近的卦 + 语义

    Returns: {
        'name': 卦名,
        'distance': Hamming距离,
        'meaning': 语义标注,
        'mood': 情绪,
        'act': 行为倾向,
        'ct': 原始28bit
    }
    """
    best = None
    best_d = 999
    for name in BAGUA_NAMES:
        d = hamming(ct, REF_28BIT[name])
        if d < best_d:
            best_d = d
            best = name

    info = BAGUA[best]
    return {
        'name': best,
        'distance': best_d,
        'meaning': info['meaning'],
        'mood': info['mood'],
        'act': info['act'],
        'ct': ct,
    }


def project_all(cts: list[int]) -> list[dict]:
    """批量投影"""
    return [project(ct) for ct in cts]


# ── 测试 ──
if __name__ == '__main__':
    print("=== 精确匹配 ===")
    for name in BAGUA_NAMES:
        r = project(REF_28BIT[name])
        print(f"  ct=0x{REF_28BIT[name]:07X} → {r['name']} (d={r['distance']}) "
              f"{r['meaning']} · {r['mood']}")

    print("\n=== 噪声匹配 ===")
    test_cts = [0x0000000, 0x0000001, 0x0000003, 0x0000007,
                0x0A3F2B1, 0x1234567, 0x0FFFFFF, 0x0000000]
    for ct in test_cts:
        r = project(ct)
        print(f"  ct=0x{ct:07X} → {r['name']} (d={r['distance']}) "
              f"{r['meaning']}")
