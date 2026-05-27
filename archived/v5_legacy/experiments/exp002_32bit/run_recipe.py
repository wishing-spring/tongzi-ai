"""Exp 002c: 32-bit recipe — 浓度补密度 + 窗口卡峰腰

配方: VEC_DIM=32, 80种子, 窗口12~20, 500 tick
"""
import random, importlib, sys, os, shutil
BASE = os.path.dirname(__file__)
SRC = os.path.join(BASE, '..', '..', 'src')

sys.path.insert(0, SRC)

# ── 生成 patched 模块 (改合并窗口) ──
PATCHED = os.path.join(BASE, '_core_patched.py')
core_src = open(os.path.join(SRC, 'tongzi_core.py'), encoding='utf-8').read()
core_src = core_src.replace('should_merge = (4 < h < 12)', 'should_merge = (12 < h < 20)')
open(PATCHED, 'w', encoding='utf-8').write(core_src)

# ── Patch constants ──
import tongzi_constants as tc
_orig_vd = tc.VEC_DIM
_orig_fm = tc.FULL_MASK
tc.VEC_DIM = 32
tc.FULL_MASK = (1 << 32) - 1
PHI_LEN = tc.PHI_LEN

# ── Import patched module ──
import importlib.util
spec = importlib.util.spec_from_file_location("_core_patched", PATCHED)
patched = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patched)
Space = patched.Space

# ── 种子 ──
WORDS = ('火 水 天 地 山 雷 风 泽 日 月 星 光 暗 冷 热 干 湿 动 静 空 '
         '云 雨 雪 霜 露 虹 霞 烟 雾 尘 '
         '土 石 沙 泉 江 湖 海 浪 冰 泥 '
         '春 夏 秋 冬 朝 暮 夜 昼 明 幽 '
         '远 近 高 低 深 浅 厚 薄 轻 重 '
         '快 慢 柔 刚 清 浊 生 死 开 合 '
         '聚 散 盈 亏 曲 直 圆 方 正 斜 '
         '红 蓝 绿 白 黑').split()

def trial(label, mother_str, seed_count, window_label):
    tc.PHI_BITS = mother_str
    spec.loader.exec_module(patched)  # re-exec to pick up new PHI_BITS
    S = patched.Space
    s = S()
    for w in WORDS[:seed_count]:
        s.ingest(w)
    for _ in range(500):
        s.tick()

    solid = [g for g in s.guas if g.is_solid]
    active = len(s.guas) - len(solid)
    drifts = {}
    for g in solid:
        if g.source and g.source in WORDS:
            ex = s.express(g)
            if ex != g.source:
                drifts[ex] = drifts.get(ex, 0) + 1

    drifts_list = sorted(drifts.items(), key=lambda x: -x[1])
    top = drifts_list[0][0] if drifts_list else 'none'
    top_n = drifts_list[0][1] if drifts_list else 0
    n_attractors = len([k for k, v in drifts_list if v >= 2])
    total_d = sum(drifts.values())

    top5 = ', '.join(f'{k}={v}' for k, v in drifts_list[:5])
    print(f'  {label:10s} win={window_label} seeds={seed_count:3d}  '
          f'guas={len(s.guas):3d} solid={len(solid):3d} active={active:3d}  '
          f'drift={total_d}/{seed_count}  pools={n_attractors}  '
          f'top="{top}"({top_n})  [{top5}]')
    return total_d, top, top_n, len(s.guas), active, n_attractors

print('=== Exp 002c: 32-bit 配方实验 ===')
print(f'  配方: 窗口12~20 (原4~12) · 80/100/120种子 · 500 tick')
print()

# φ
phi_80 = trial('φ-80', tc.PHI_BITS, 80, '12~20')
phi_100 = trial('φ-100', tc.PHI_BITS, 100, '12~20')
phi_120 = trial('φ-120', tc.PHI_BITS, 120, '12~20')

print()

# π
PI = ("0010010000111111011010101000100010000101101000110000100011010011"
      "0001001100011001100010100010111000000001101110000011100110100010"
      "0010010100101000010100100000010011110011000001001100101001101100"
      "110000101101010001100001100011010100000010100001001011000110101100")[:PHI_LEN]
pi_80 = trial('π-80', PI, 80, '12~20')
pi_100 = trial('π-100', PI, 100, '12~20')
pi_120 = trial('π-120', PI, 120, '12~20')

print()

# 对照: 原窗口 4~12 跑一次 80 种子
core_src_orig = open(os.path.join(SRC, 'tongzi_core.py'), encoding='utf-8').read()
open(PATCHED, 'w', encoding='utf-8').write(core_src_orig)
spec.loader.exec_module(patched)
tc.PHI_BITS = tc.PHI_BITS  # restore
spec.loader.exec_module(patched)
_orig_window = trial('φ-80(4~12)', tc.PHI_BITS, 80, '4~12')

print()
print('=== 对比 ===')
print(f'  16位/20种/窗口4~12: guas=47  active=24  drift=11/20  pools=多')
print(f'  32位/80种/窗口12~20: guas={phi_80[3]}  active={phi_80[4]}  drift={phi_80[0]}/80  pools={phi_80[5]}')
print(f'  32位/80种/窗口4~12(原): guas={_orig_window[3]}  active={_orig_window[4]}  drift={_orig_window[0]}/80')

# ── 恢复 ──
tc.VEC_DIM = _orig_vd
tc.FULL_MASK = _orig_fm
os.remove(PATCHED)
print()
print('✅ Cleanup done.')
