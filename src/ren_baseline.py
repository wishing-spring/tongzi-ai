# -*- coding: utf-8 -*-
"""童子 v2.1 · 基线报告 · 32位 · 31字符库 · 语义评估用原始编码"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi import Tongzi, _fit_32, _tri_encode32

tz = Tongzi(tau=5, fit_min=8)
train = "水河火木天地日月山河金刀剑一二三四五六七八九十万千爱恨生死你我他"
tz.feed(train)
tz.report()

print(f"\n--- 全库档案 ---")
print(f"{'字':<4} {'状态':<8} {'碰数':<4} {'锁定链'}")
print("-" * 60)
for ch in train:
    if ch not in tz.archives: continue
    n = tz.archives[ch]
    print(f"{ch:<4} {n.state:<8} {len(n.scars):<4} {tz._trace(n)}")

r = sum(1 for n in tz.archives.values() if n.state == 'result')
p = sum(1 for n in tz.archives.values() if n.state == 'pruned')
h = sum(1 for n in tz.archives.values() if n.state == 'active')
print(f"\n归约:{r}  剪枝:{p}  悬挂:{h}  剪枝率:{p/max(1,r+p):.0%}")

print("\n--- 语义对 (原始编码, m=8) ---")
pairs = [
    ("水","河","近义"),("火","水","反义"),("爱","恨","反义"),
    ("生","死","反义"),("一","二","数字"),("爱","水","无关"),
]
for a,b,label in pairs:
    gA1,gB1,gC1 = _tri_encode32(a)
    gA2,gB2,gC2 = _tri_encode32(b)
    ok_a = _fit_32(gA1, gA2, 8) or _fit_32(gA2, gA1, 8)
    ok_b = _fit_32(gB1, gB2, 8) or _fit_32(gB2, gB1, 8)
    ok_c = _fit_32(gC1, gC2, 8) or _fit_32(gC2, gC1, 8)
    ax = sum([ok_a, ok_b, ok_c])
    print(f"  {a}-{b} [{label}]  {ax}/3")
