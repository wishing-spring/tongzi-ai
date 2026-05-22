"""Exp 002b: 32-bit × 40 seeds — double the population density."""
import random, importlib, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
import tongzi_constants
import tongzi_core

WORDS = '火 水 天 地 山 雷 风 泽 日 月 星 光 暗 冷 热 干 湿 动 静 空 云 雨 雪 霜 露 虹 霞 烟 雾 尘 土 石 沙 泉 江 湖 海 浪 冰 泥'.split()

_orig_vd = tongzi_constants.VEC_DIM
_orig_fm = tongzi_constants.FULL_MASK
tongzi_constants.VEC_DIM = 32
tongzi_constants.FULL_MASK = (1 << 32) - 1
PHI_LEN = tongzi_constants.PHI_LEN

importlib.reload(tongzi_core)
Space = tongzi_core.Space

def trial(label, mother_str):
    tongzi_constants.PHI_BITS = mother_str
    importlib.reload(tongzi_core)
    S = tongzi_core.Space
    s = S()
    for w in WORDS:
        s.ingest(w)
    for _ in range(300):
        s.tick()

    solid = [g for g in s.guas if g.is_solid]
    active = len(s.guas) - len(solid)
    drifts = {}
    for g in solid:
        if g.source and g.source in WORDS:
            ex = s.express(g)
            if ex != g.source:
                drifts[ex] = drifts.get(ex, 0) + 1

    drifts_tuple = []
    for g in solid:
        if g.source and g.source in WORDS:
            drifts_tuple.append((g.source, s.express(g)))

    top = max(drifts, key=drifts.get) if drifts else 'none'
    top_n = drifts.get(top, 0)
    total_d = sum(drifts.values())
    top5 = ', '.join(f'{k}={v}' for k, v in sorted(drifts.items(), key=lambda x: -x[1])[:5])
    n_attractors = len(set(d[1] for d in drifts_tuple if d[0] != d[1]))
    print(f'  {label:6s}  guas={len(s.guas):3d}  solid={len(solid):3d}  active={active:3d}  drift={total_d}/40  attractor_pools={n_attractors}  top="{top}"({top_n})  [{top5}]')
    return total_d, top, top_n, len(s.guas), len(solid), active, n_attractors

print('=== Exp 002b: 32-bit × 40 seeds ===')
print()

a_out = trial('φ', tongzi_constants.PHI_BITS)
a_d, a_top, a_n, a_g, a_s, a_a, a_nattr = a_out

PI = ("0010010000111111011010101000100010000101101000110000100011010011"
      "0001001100011001100010100010111000000001101110000011100110100010"
      "0010010100101000010100100000010011110011000001001100101001101100"
      "110000101101010001100001100011010100000010100001001011000110101100")[:PHI_LEN]
b_out = trial('π', PI)

rand = []
for i in range(3):
    random.seed(i * 101)
    rb = ''.join(str(random.randint(0, 1)) for _ in range(PHI_LEN))
    rand.append(trial(f'随机{i+1}', rb))

print()
print('=== Comparison ===')
print(f'  20 seeds  16-bit φ: drift=11/20  guas=47  active=24   top=地(10)  fertile')
print(f'  20 seeds  32-bit φ: drift=20/20  guas=26  active=0    top=水(19)  sterile')
print(f'  40 seeds  32-bit φ: drift={a_d}/40  guas={a_g}  active={a_a}   top={a_top}({a_n})  attractors={a_nattr}')
ravg = sum(r[0] for r in rand) / len(rand)
ravg_a = sum(r[5] for r in rand) / len(rand)
ravg_n = sum(r[6] for r in rand) / len(rand)
if a_a > 0:
    print(f'  → Active gua present! 32-bit space regains dynamics with 40 seeds.')

tongzi_constants.VEC_DIM = _orig_vd
tongzi_constants.FULL_MASK = _orig_fm
importlib.reload(tongzi_core)
print()
print('✅ Restored to 16-bit.')
