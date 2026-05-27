"""Exp 003: 浓度梯度扫描 — 16位甜点区边界测绘 + 周期监测

扫描: 10/20/30/40/50/60 种子 × 800 tick
追踪: 活跃卦数 · 池数 · 霸主强度 · 每100tick快照
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from tongzi_core import Space

WORDS = ('火 水 天 地 山 雷 风 泽 日 月 星 光 暗 冷 热 干 湿 动 静 空 '
         '云 雨 雪 霜 露 虹 霞 烟 雾 尘 土 石 沙 泉 江 湖 海 浪 冰 泥 '
         '春 夏 秋 冬 朝 暮 夜 昼 明 幽 远 近 高 低 深 浅 厚 薄 轻 重 '
         '快 慢 柔 刚 清 浊 生 死 开 合 聚 散 盈 亏').split()

SEEDS = [10, 20, 30, 40]
TICKS = 400
SNAP_INTERVAL = 100

def run_scan(seed_count):
    s = Space()
    for w in WORDS[:seed_count]:
        s.ingest(w)

    history = []

    for t in range(1, TICKS + 1):
        s.tick()

        if t % SNAP_INTERVAL == 0:
            solid = [g for g in s.guas if g.is_solid]
            active = len(s.guas) - len(solid)

            drifts = {}
            for g in solid:
                if g.source and g.source in WORDS:
                    ex = s.express(g)
                    if ex != g.source:
                        drifts[ex] = drifts.get(ex, 0) + 1
            drifts_list = sorted(drifts.items(), key=lambda x: -x[1])
            pools = len([k for k, v in drifts_list if v >= 2])
            top = drifts_list[0] if drifts_list else ('none', 0)
            history.append((t, active, pools, top[0], top[1]))

    solid = [g for g in s.guas if g.is_solid]
    final_active = len(s.guas) - len(solid)
    drifts = {}
    for g in solid:
        if g.source and g.source in WORDS:
            ex = s.express(g)
            if ex != g.source:
                drifts[ex] = drifts.get(ex, 0) + 1
    drifts_list = sorted(drifts.items(), key=lambda x: -x[1])
    final_pools = len([k for k, v in drifts_list if v >= 2])
    final_top = drifts_list[0] if drifts_list else ('none', 0)

    # 周期检测
    actives = [h[1] for h in history]
    peaks = 0
    if len(actives) >= 4:
        for i in range(2, len(actives) - 1):
            if actives[i] > actives[i-1] and actives[i] > actives[i-2] and actives[i] > actives[i+1]:
                peaks += 1

    return {
        'seeds': seed_count,
        'guas': len(s.guas),
        'final_active': final_active,
        'final_pools': final_pools,
        'final_top': final_top,
        'history': history,
        'oscillation_peaks': peaks,
        'drift_rate': sum(drifts.values()),
    }

print('=== Exp 003: 16-bit Concentration Gradient Scan ===')
print(f'  {SEEDS} seeds x {TICKS} ticks · snapshot every {SNAP_INTERVAL}tick')
print()

results = []
for n in SEEDS:
    r = run_scan(n)
    results.append(r)
    h = r['history']
    trace = ' -> '.join(f't{h[i][0]}:{h[i][1]}' for i in range(len(h)))
    print(f'  seeds={n:2d}  guas={r["guas"]:2d}  final_active={r["final_active"]:2d}  '
          f'pools={r["final_pools"]}  drift={r["drift_rate"]}/{n}  '
          f'top={r["final_top"][0]}({r["final_top"][1]})  peaks={r["oscillation_peaks"]}')
    print(f'         trace: {trace}')

print()
print('=== Sweet Spot Boundary ===')

header = f'{"seeds":>5s}  {"guas":>4s}  {"active":>6s}  {"pools":>5s}  {"drift":>6s}  {"waves":>5s}  state'
print(header)
print('-' * 60)

for r in results:
    drift_pct = f'{r["drift_rate"]}/{r["seeds"]}'
    pk = r['oscillation_peaks']
    if r['final_active'] >= 15 and r['final_pools'] >= 2:
        state = 'ALIVE·multi'
    elif r['final_active'] >= 5:
        state = 'SEMI'
    elif r['final_active'] >= 1:
        state = 'DYING'
    else:
        state = 'DEAD'
    if pk >= 3:
        state += '·breathing'
    print(f'{r["seeds"]:>5d}  {r["guas"]:>4d}  {r["final_active"]:>6d}  '
          f'{r["final_pools"]:>5d}  {drift_pct:>6s}  {pk:>5d}  {state}')

print()
print('Done.')
