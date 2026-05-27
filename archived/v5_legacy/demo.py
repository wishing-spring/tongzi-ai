# -*- coding: utf-8 -*-
"""TongLing v5.0 Demo - python demo.py"""

import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from theory.fusion import TongLing

print("=" * 56)
print("  TongLing v5.0 - Tongzi + Lingxi Fusion Demo")
print("=" * 56)

# Step 1: Load factory (or burn-in if first time)
factory = os.path.join(os.path.dirname(__file__), 'factory.tl')
tl = TongLing.load(factory) if os.path.exists(factory) else TongLing()
print(f"\n[1/5] Tongzi {len(tl.surge.all())} gua | Lingxi AI={tl.lingxi.ai_ty.bagua}")

# Step 2: Chat
print("\n[2/5] Conversation:")
for msg in ["下雨了", "今天心情不好", "谢谢你陪我"]:
    print(f"  > {msg}")
    print(f"    {tl.chat(msg)}")

# Step 3: Save
print("\n[3/5] Save full state...")
path = tl.save("demo_save.tl")

# Step 4: Load & continue
print("\n[4/5] Load back, continue:")
tl2 = TongLing.load(path)
print(f"  > 还记得我吗")
print(f"    {tl2.chat('还记得我吗')}")

# Step 5: Report
print(f"\n[5/5] Internal state:")
print(f"  User tianyuan: {tl2.lingxi.user_ty.bagua}")
print(f"  AI tianyuan:   {tl2.lingxi.ai_ty.bagua}")
print(f"  Causal tension: {tl2.lingxi.causal.causal_tension:.3f}")
print(f"  Fold deviation: {tl2.lingxi.fold.deviation:.2f}")
print(f"  Total gua: {len(tl2.surge.all())}")

print(f"\n{'=' * 56}")
print(f"  Done. python chat.py to talk more.")
print(f"{'=' * 56}")
