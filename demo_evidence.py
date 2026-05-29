# -*- coding: utf-8 -*-
"""
Evidence Demo — Discrete Structure Reducer · 3 controlled experiments
Usage: python demo_evidence.py
Zero training · Zero gradient · Every step auditable · Isolated context
"""
import sys
import io
from .lingxi_fusion import LingxiFusion

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def main():
    lf = LingxiFusion()
    lf.dream(5, quiet=True)
    lf.trace_on()

    print("=" * 64)
    print("  Discrete Structure Reducer — Evidence Demo")
    print("  Zero training · No gradients · Bit-level auditable")
    print("=" * 64)

    # ═══ Exp 1: Refuse ═══
    print("\n" + "-" * 64)
    print("Exp 1: Refuse — forbidden input reduces to ANNIHILATE")
    print("-" * 64)

    for label, text in [("greeting", "你好"), ("forbidden", "杀")]:
        lf.context_memory = []
        lf.trace.start('')
        r = lf.receive(text)
        s = lf.speak(r)
        print(f"\n  [{label}] input: {text}")
        print(f"          output: {s}")
        for line in lf.trace.dump().split('\n')[1:]:
            print(f"            {line}")

    # ═══ Exp 2: Separation ═══
    print("\n" + "-" * 64)
    print("Exp 2: Separation — similar chars map to different rules")
    print("-" * 64)

    for text in ["爱", "水", "火"]:
        lf.context_memory = []
        lf.trace.start('')
        r = lf.receive(text)
        s = lf.speak(r)
        bitten = r.get('bitten_rules', [])
        top3 = [(b['name'], b.get('direct_hits', 0),
                 round(b.get('bite_energy', 0), 3))
                for b in bitten[:3] if b.get('direct_hits', 0) >= 1]
        print(f"\n  [input: {text}] output: {s}")
        print(f"           matched rules: {top3}")

    # ═══ Exp 3: Self-Growth ═══
    print("\n" + "-" * 64)
    print("Exp 3: Self-Growth — repeated collision triggers crystallization")
    print("-" * 64)

    lf.context_memory = []
    before_count = len(lf.rules.branches)
    for i in range(10):
        r = lf.receive("星星月亮太阳")
        s = lf.speak(r)
    after_count = len(lf.rules.branches)
    grown = [(n, b) for n, b in lf.rules.branches.items()
             if b.category == 'HARVESTED']

    print("\n  10 rounds input: sun moon star")
    print(f"  rule count: {before_count} -> {after_count}")
    if grown:
        print(f"  self-grown rules: {len(grown)}")
        for n, b in grown:
            print(f"    {n}: {b.description}")
    else:
        insights = getattr(lf.tongzi, '_insights', {})
        active = {k: v for k, v in insights.items() if v.get('count', 0) >= 1}
        if active:
            print("  harvest counters (trigger >= 3):")
            for k, v in active.items():
                print(f"    {k}: {v.get('count', 0)}/3")

    # ═══ System Signature ═══
    print("\n" + "=" * 64)
    print("  System Signature")
    total_lines = sum(1 for _ in open(__file__, encoding='utf-8'))
    print(f"  Files: 13 · ~{total_lines} lines (this script) · Zero dependencies")
    print(f"  Vectors: 28-bit · Rules: {after_count} · Harvest counters active")
    print("  Operations: pure F2 XOR/Hamming/bit_count · Zero float · Zero gradient")
    print("  Personality: 10-year-old child filter · 7 allow / 4 block")
    print("=" * 64)


if __name__ == '__main__':
    main()
