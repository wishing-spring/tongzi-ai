"""Exp 003b: 松绑密度清理 — VEC_DIM×4 → 看生态是否复活"""
import sys, os, shutil
BASE = os.path.dirname(__file__)
SRC = os.path.join(BASE, '..', '..', 'src')
sys.path.insert(0, SRC)

# ── Patch: VEC_DIM*2 → VEC_DIM*4 ──
PATCHED = os.path.join(BASE, '_core_loose.py')
src = open(os.path.join(SRC, 'tongzi_core.py'), encoding='utf-8').read()
src = src.replace('max(5, VEC_DIM * 2)', 'max(5, VEC_DIM * 4)')
open(PATCHED, 'w', encoding='utf-8').write(src)

import importlib.util
spec = importlib.util.spec_from_file_location("_core_loose", PATCHED)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
Space = mod.Space

WORDS = ('火 水 天 地 山 雷 风 泽 日 月 星 光 暗 冷 热 干 湿 动 静 空 '
         '云 雨 雪 霜 露 虹 霞 烟 雾 尘 土 石 沙 泉 江 湖 海 浪 冰 泥 '
         '春 夏 秋 冬 朝 暮 夜 昼 明 幽 远 近 高 低 深 浅 厚 薄 轻 重 '
         '快 慢 柔 刚 清 浊 生 死 开 合 聚 散 盈 亏').split()

def run(seeds, ticks=300):
    s = Space()
    for w in WORDS[:seeds]: s.ingest(w)

    snapshots = []
    for t in range(1, ticks+1):
        s.tick()
        if t % 100 == 0:
            solid = [g for g in s.guas if g.is_solid]
            active = len(s.guas) - len(solid)
            drifts = {}
            for g in solid:
                if g.source and g.source in WORDS:
                    ex = s.express(g)
                    if ex != g.source: drifts[ex] = drifts.get(ex,0)+1
            dl = sorted(drifts.items(), key=lambda x:-x[1])
            pools = len([1 for k,v in dl if v>=2])
            top = dl[0] if dl else ('none',0)
            snapshots.append((t, active, pools, top[0], top[1]))

    solid = [g for g in s.guas if g.is_solid]
    final_active = len(s.guas) - len(solid)
    drifts = {}
    for g in solid:
        if g.source and g.source in WORDS:
            ex = s.express(g)
            if ex != g.source: drifts[ex] = drifts.get(ex,0)+1
    dl = sorted(drifts.items(), key=lambda x:-x[1])
    final_pools = len([1 for k,v in dl if v>=2])
    final_top = dl[0] if dl else ('none',0)

    return len(s.guas), final_active, final_pools, final_top, sum(drifts.values()), snapshots

print('=== Exp 003b: Loose Gardener (VEC_DIM×4) ===')
print(f'  limit: 32 → 64  |  300 ticks')
print()

# 20 seeds (compare to exp001)
g, a, p, t, d, snaps = run(20, 300)
trace = ' -> '.join(f't{x[0]}:{x[1]}' for x in snaps)
print(f'  20 seeds: guas={g}  active={a}  pools={p}  drift={d}/20  top={t[0]}({t[1]})')
print(f'           {trace}')
print(f'  exp001:  guas=47  active=24  pools=多  drift=11/20  top=地(10)')

print()
g, a, p, t, d, snaps = run(30, 300)
trace = ' -> '.join(f't{x[0]}:{x[1]}' for x in snaps)
print(f'  30 seeds: guas={g}  active={a}  pools={p}  drift={d}/30  top={t[0]}({t[1]})')
print(f'           {trace}')

print()
g, a, p, t, d, snaps = run(40, 300)
trace = ' -> '.join(f't{x[0]}:{x[1]}' for x in snaps)
print(f'  40 seeds: guas={g}  active={a}  pools={p}  drift={d}/40  top={t[0]}({t[1]})')
print(f'           {trace}')

os.remove(PATCHED)
print()
print('✅ Done.')
