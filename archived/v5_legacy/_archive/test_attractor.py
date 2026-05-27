"""Test: is '地' attractor real emergence or encoding artifact?"""
from tongzi_core import Space

WORDS = '火 水 天 地 山 雷 风 泽 日 月 星 光 暗 冷 热 干 湿 动 静 空'.split()

space = Space()
vecs = {}
for w in WORDS:
    g = space.ingest(w)
    vecs[w] = g.value

# 1. Vectors and popcount
print("=== 20 vectors (sorted by bit pattern) ===")
for w, v in sorted(vecs.items(), key=lambda x: x[1]):
    bits = f'{v:016b}'.replace('0','·').replace('1','█')
    print(f"  {w:4s}  0x{v:04x}  [{bits}]  pop={v.bit_count()}")

# 2. Centrality: avg Hamming distance to all others
print("\n=== Centrality (lower = more central) ===")
cent = {}
for w, v in vecs.items():
    avg_h = sum((v ^ v2).bit_count() for v2 in vecs.values()) / len(vecs)
    cent[w] = avg_h

for w, a in sorted(cent.items(), key=lambda x: x[1]):
    marker = " ← MOST CENTRAL" if w == '地' else ""
    print(f"  {w:4s}  avg_hamming={a:.1f}{marker}")

# 3. Check if '地' is the natural gravity center just from its bit pattern
print("\n=== Answer: Is '地' naturally central? ===")
rank = sorted(cent.items(), key=lambda x: x[1])
di_rank = [i for i, (w, _) in enumerate(rank) if w == '地'][0]
print(f"  '地' centrality rank: #{di_rank+1} of 20")

# 4. Run 3 independent trials to see if attractor changes
print("\n=== Reproducibility: 3 trials, attractor consistency ===")
for trial in range(3):
    s = Space()
    for w in WORDS:
        s.ingest(w)
    for _ in range(100):
        s.tick()
    
    # Find which source word maps to which express
    solid = [g for g in s.guas if g.is_solid]
    drift_count = 0
    drift_targets = {}
    for g in solid:
        if g.source and g.source in WORDS:
            ex = s.express(g)
            if ex != g.source:
                drift_count += 1
                drift_targets[ex] = drift_targets.get(ex, 0) + 1
    
    top_attractor = max(drift_targets, key=drift_targets.get) if drift_targets else "none"
    print(f"  Trial {trial+1}: drift={drift_count}/20  top_attractor='{top_attractor}' ({drift_targets.get(top_attractor,0)} sources)")
