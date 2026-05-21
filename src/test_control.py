"""Control experiment: φ vs random vs π — does attractor depend on φ?"""
import random
from tongzi_core import Space, VEC_DIM
from tongzi_constants import PHI_BITS, PHI_LEN

WORDS = '火 水 天 地 山 雷 风 泽 日 月 星 光 暗 冷 热 干 湿 动 静 空'.split()

random.seed(42)

# Generate alternative mother bodies as strings
def rand_bits(n):
    return ''.join(str(random.randint(0, 1)) for _ in range(n))

# π binary expansion (first 256 bits from fractional part)
PI_BITS_STR_256 = (
    "00100100001111110110101010001000"  # 3.14159...
    "10000101101000110000100011010011"
    "00010011000110011000101000101110"
    "00000001101110000011100110100010"
    "00100101001010000101001000000100"
    "11110011000001001100101001101100"
    "11000010110101000110000110001101"
    "01000000101000010010110001101011"
    "00"  # pad to 256
)[:PHI_LEN]

def run_one(label, bits_str):
    import tongzi_constants
    orig = tongzi_constants.PHI_BITS
    tongzi_constants.PHI_BITS = bits_str

    import importlib, tongzi_core
    importlib.reload(tongzi_core)
    from tongzi_core import Space as SR

    s = SR()
    for w in WORDS:
        s.ingest(w)
    for _ in range(100):
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

    tongzi_constants.PHI_BITS = orig
    importlib.reload(tongzi_core)

    detail = ", ".join(f"{k}={v}" for k, v in sorted(drifts.items(), key=lambda x: -x[1])[:5])
    print(f"  {label:6s}  drift={total}/20  top='{top}' ({top_n})  [{detail}]")
    return total, top, top_n

print(f"PHI_LEN={PHI_LEN}, VEC_DIM={VEC_DIM}\n")
print("=== Mother Body Comparison ===\n")

phi_t, phi_top, phi_n = run_one("φ母体", PHI_BITS)
pi_t, pi_top, pi_n = run_one("π", PI_BITS_STR_256)

print()
print("=== 5 Random Mother Bodies ===")
rand_results = []
for i in range(5):
    random.seed(i * 101)
    rbits = rand_bits(PHI_LEN)
    t, top, n = run_one(f"随机{i+1}", rbits)
    rand_results.append((t, top, n))

print()
print("=== Summary ===")
print(f"  φ母体:  drift={phi_t}/20  attractor='{phi_top}' ({phi_n})")
print(f"  π母体:  drift={pi_t}/20  attractor='{pi_top}' ({pi_n})")
r_total = sum(r[0] for r in rand_results) / len(rand_results)
r_tops = [r[1] for r in rand_results]
print(f"  随机均值: drift={r_total:.1f}/20  tops={r_tops}")
