# -*- coding: utf-8 -*-
"""全链路测试 · 三轴童子"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tri_tongzi import TriTongzi
from tools.strokes import STROKE_COUNT

t = TriTongzi()
all_chars = list(STROKE_COUNT.keys())
t.learn(''.join(all_chars))
print(f"学 {len(all_chars)} 字\n")

tests = ["水河火","天地人","日月星","爱恨","红绿蓝","你我他","上下左右","生死","森林","道法自然"]
for q in tests:
    r = t.ask(q)
    parts = [f"{it['字']}[{it['A']}/{it['B']}/{it['C']}]->{it['结果']}" for it in r['逐字']]
    print(f"「{q}」")
    for p in parts:
        print(f"  {p}")
    print()

print(t.stats())
