"""Tongzi v1.2 Demo: 20 words, 100 ticks."""
from tongzi_core import Space, VEC_DIM

WORDS = "火 水 天 地 山 雷 风 泽 日 月 星 光 暗 冷 热 干 湿 动 静 空".split()
CHECKPOINTS = [0, 10, 20, 30, 50, 70, 100]

space = Space()

# === INGEST ===
print("=" * 60)
print("INGEST: 20 seeds")
print("=" * 60)
for w in WORDS:
    g = space.ingest(w)
    print(f"  {w:4s} → vec=0x{g.value:04x}  id_t={g.id_t:2d}  id_l={g.id_l:2d}")
print(f"\n  Total gua: {space.size}\n")

# === TICK with checkpoints ===
print("=" * 60)
print(f"RUNNING: 100 ticks (VEC_DIM={VEC_DIM})")
print("=" * 60)

checkpoint_idx = 0
for t in range(1, 101):
    space.tick()
    if t in CHECKPOINTS:
        s = space.status()
        print(f"\n--- tick {t:3d} ---")
        print(f"  total={s['total']}  active={s['active']}  solid={s['solid']}  max_layer={s['max_layer']}")
        # Show a few active gua
        active = [g for g in space.guas if not g.is_solid]
        if active:
            for g in sorted(active, key=lambda x: -x.energy)[:5]:
                ex = space.express(g)
                print(f"  [{ex:4s}] vec=0x{g.value:04x}  e={g.energy:3d}  hit={g.hit_count:2d}  sol={g.is_solid}  id_t={g.id_t}")

# === FINAL STATE ===
print("\n" + "=" * 60)
print("FINAL STATE")
print("=" * 60)
s = space.status()
print(f"total={s['total']}  active={s['active']}  solid={s['solid']}  tick={s['tick']}")

# Show all gua with express
print("\nAll gua (by id_t):")
for g in sorted(space.guas, key=lambda x: x.id_t):
    ex = space.express(g)
    tag = "[SOLID]" if g.is_solid else "[live] "
    src = g.source or "-"
    print(f"  {tag} [{ex:4s}] ← {src:4s}  vec=0x{g.value:04x}  e={g.energy:3d}  hc={g.hit_count:2d}  id_t={g.id_t:2d}  id_l={g.id_l:2d}")

# Save
space.save()
print(f"\nState saved to tongzi_state.json")
