"""Exp 002: 32-bit expansion — does the attractor mechanism hold at scale?"""
import random, importlib, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import tongzi_constants
import tongzi_core

WORDS = '火 水 天 地 山 雷 风 泽 日 月 星 光 暗 冷 热 干 湿 动 静 空'.split()

# --- Patch to 32-bit ---
_orig_vec_dim = tongzi_constants.VEC_DIM
_orig_full_mask = tongzi_constants.FULL_MASK
tongzi_constants.VEC_DIM = 32
tongzi_constants.FULL_MASK = (1 << 32) - 1
PHI_LEN = tongzi_constants.PHI_LEN

importlib.reload(tongzi_core)
Space = tongzi_core.Space

print(f"=== Exp 002: 32-bit Expansion ===")
print(f"VEC_DIM: {_orig_vec_dim} → 32")
print(f"PHI_LEN: {PHI_LEN}")
print()

def run_trial(label, mother_str):
    """Run one trial with given mother body bits."""
    tongzi_constants.PHI_BITS = mother_str
    importlib.reload(tongzi_core)
    S = tongzi_core.Space  # fresh class with new PHI_BITS

    s = S()
    for w in WORDS:
        s.ingest(w)
    for _ in range(200):
        s.tick()

    solid = [g for g in s.guas if g.is_solid]
    drifts = {}
    for g in solid:
        if g.source and g.source in WORDS:
            ex = s.express(g)
            if ex != g.source:
                drifts[ex] = drifts.get(ex, 0) + 1

    top = max(drifts, key=drifts.get) if drifts else "none"
    top_n = drifts.get(top, 0)
    total = sum(drifts.values())
    total_guas = len(s.guas)
    solid_n = len(solid)

    detail = ", ".join(f"{k}={v}" for k, v in sorted(drifts.items(), key=lambda x: -x[1])[:5])
    print(f"  {label:6s}  guas={total_guas} solid={solid_n} drift={total}/20  top='{top}' ({top_n})  [{detail}]")
    return total, top, top_n, total_guas, solid_n

# φ
phi_t, phi_top, phi_n, phi_guas, phi_solid = run_trial("φ", tongzi_constants.PHI_BITS)

# π
PI_BITS_STR = (
    "00100100001111110110101010001000"
    "10000101101000110000100011010011"
    "00010011000110011000101000101110"
    "00000001101110000011100110100010"
    "00100101001010000101001000000100"
    "11110011000001001100101001101100"
    "11000010110101000110000110001101"
    "01000000101000010010110001101011"
    "00"
)[:PHI_LEN]
pi_t, pi_top, pi_n, pi_guas, pi_solid = run_trial("π", PI_BITS_STR)

# 3 random mother bodies
print()
rand_results = []
for i in range(3):
    random.seed(i * 101)
    rbits = ''.join(str(random.randint(0, 1)) for _ in range(PHI_LEN))
    t, top, n, guas, solid_n = run_trial(f"随机{i+1}", rbits)
    rand_results.append((t, top, n, guas, solid_n))

# Summary
print()
print("=== Summary: 16-bit vs 32-bit ===")
print(f"  16-bit φ: drift=11/20  attractor='地'(10)  guas=47")
print(f"  32-bit φ: drift={phi_t}/20  attractor='{phi_top}'({phi_n})  guas={phi_guas}")

r_avg_t = sum(r[0] for r in rand_results) / len(rand_results)
r_tops = [r[1] for r in rand_results]
r_avg_guas = sum(r[3] for r in rand_results) / len(rand_results)
print(f"  32-bit random avg: drift={r_avg_t:.1f}/20  guas={r_avg_guas:.0f}  tops={r_tops}")

# Restore
tongzi_constants.VEC_DIM = _orig_vec_dim
tongzi_constants.FULL_MASK = _orig_full_mask
importlib.reload(tongzi_core)
print()
print("Restored to 16-bit. ✅")
