import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from tongzi_core import Space

s = Space()
words = ['冷','热','冬','夏','雪','火','冰','春','秋','风','雨','寒','暖','霜','雷','云']
for w in words:
    s.ingest(w)

print(f"播种: {s}\n")

total_merges = 0
for i in range(50):
    r = s.tick()
    total_merges += r['merges']
    if r['merges'] > 0 or r['collisions'] > 0:
        print(f"  tick {s.tick_count:>3}: 撞{r['collisions']} 固{r['solidified']} 合{r['merges']}")

print(f"\n总合体: {total_merges}")
print(f"空间: {s}")

merge_guas = [g for g in s.guas if g.id_l < 16]
print(f"\n合体卦 ({len(merge_guas)} 个):")
for g in merge_guas:
    expr = s.express(g)
    print(f"  XOR" if g.id_l == 8 else f"  AND", f"| {g} → {expr if expr else '(无)'}")
