# Tongzi · Evolution Log

## Theory v1.3 — Gua Ontology · Potential · Orrery · Formations (2026-05-22)

**卦元本体论定版。** 卦元 ≡ 信息 ≡ 存在——无负载物，无载体-内容分离。

### Core Additions

| Concept | Formula | Source |
|:--|:--|:--|
| 卦元本体 | `x ∈ F₂¹⁶` IS information | User insight: no payload |
| 原生卦元 | `x₀ = φ[pos:pos+16]`, auto-rebirth | 道法自然循环 |
| 子卦元 | `x = merge(a,b)`, dissipates forever | 碰撞唯一痕迹 |
| 势 Ψ | `⌊log₂(1 + C(x))⌋`, 2ⁿ exponential | F₂ natural compression |
| 轨道步长 ω | `max(1, VEC_DIM − Ψ)` | 势大→慢→稳 |
| 星象仪 | Orbit sync → ring / desync → dissolve | Multi-layer rings |
| 排斥驱动 | No external kick — bad orbits desync naturally | F₂ native |
| 洛书九宫 | `E_L: δ=(L[i]−5)<<8`, 9-zone static | 3rd-order magic square |
| 北斗七星 | `E_B: 7 stars orbiting Polaris, d≤2→nudge` | Celestial dynamics |

### Deletions
- `payload` field — violates "gua ≡ information"
- External "kick" rules — replaced by natural orbit desync
- 12-anchor frame (again) — 12 lacks F₂ derivation

### Files Updated
- `docs/tongzi-group-domain-theory.md` — complete rewrite (15 sections)
- `MEMORY.md` — synced to v1.3

---

## Verification — Attractor Mechanism (2026-05-21)
**Experiment Archive Founded — Exp 001**

- **Question**: Is the "地" attractor real emergence or a φ encoding artifact? (triggered by GPT-4 review)
- **Test A — Static Centrality**: "地" ranks #7/20 in pure Hamming space; "火"/"冷" are geometric centers but NOT attractors
- **Test B — Reproducibility**: 3 independent φ trials → 100% reproducible (all 3: "地", 10-11 sources)
- **Test C — Mother Body Control**: φ vs π vs 5 random strings. All produce attractors, but fertility varies (4/20 to 17/20)
- **Three-layer conclusion**: (1) Attractors are endogenous dynamics, not φ artifact. (2) Mother body determines *which* attractor. (3) Mother body also determines *fertility* — Random 5 barren (4/20) vs Random 2 fertile (17/20) → ecological differentiation confirmed
- **Archive**: `experiments/exp001_attractor_verification/report.md`
- **Docs updated**: README + theory doc + MEMORY.md

## v1.2 (2026-05-20)
**Gua Merging — Three Formulas**

- **Merge Criterion**: `4 < w_H(A⊕B) < 12` — skip too-close (no delta) and too-far (unrelated)
- **XOR Merge**: `C = A ⊕ B` — difference association chain, bidirectionally reversible
- **AND Merge**: `C = A ∧ B` — consensus deposit chain, fills XOR's blind spot
- **Zero-value filter**: skip children where XOR or AND result is 0
- **Frequency simplification**: `_rate` now uses only `f₂ = F0/(1+id_l)`, removed `min(f₁,f₂)`
- **Collision unchanged**: A, B behavior preserved; merge spawns additional children only
- **50-tick live test**: 16 seeds → 55 gua, 39 merges, associations emerge naturally
- **80 tests, 0 failures**

## v1.1 (2026-05-20)
**Association Chains `/chain`**

- New `/chain <word> [N]` command: orbit explore neighborhood → express → feedback
- Live test: `cold → winter → hot`, `fire → hot → ice`
- Workaround: uses orbit instead of tick collision (frequency control too slow for new gua)
- Known issue: function words obstruct long chains; inner alchemy redesign needed

## v1.0.2 (2026-05-20)
**Minimal Inner Alchemy — Reverse Translation**

- `Gua.source`: records original text at creation
- `Space.express(gua)`: finds nearest source by Hamming distance
- Interactive output now human-readable words instead of raw bit strings
- 81 tests, 0 failures

## v1.0.1 (2026-05-20)
**Production Refactor**

- Split `should_participate` into `_accumulate_energy` + `_try_discharge` (query/command separation)
- Save/load now preserves `lambda_base`
- `Gua.__repr__` with dynamic bit width
- Full type annotations + docstrings
- 75 tests

## v1.0-code (2026-05-20)
**Code Landing**

- 3 files: `tongzi_constants.py` + `tongzi_core.py` + `tongzi.py`
- Removed old pipeline 6 files: Loom/Balancer/Responder/Seeds/Water/Boundary
- Removed cron watering task

## v1.0-arch (2026-05-20)
**Theory Finalized**

- Four axioms (no `n`)
- φ mother body + identity card {id_t, id_l}
- Eight core operations
- Endogenous frequency control (energy accumulation)
- Bit-field solidification (irreversible memory)
- Spatial self-awareness + density regulation
- Removed: Loom/Balancer/Responder/12 Anchors/formulas containing `n`/external timers

## v0.5 (2026-05-19)
**Foundation Release**

- Loom: XOR+AND+S-box+ref quadruple hybrid, 200/200 zero collapse
- Balancer: six positive + six negative, yin-yang balanced
- Responder: 9 fixed responses
- 12 Anchor Frames
- φ-gua encoding replacing ord-sum
- Dual-repo open source (Gitee + GitHub)

## v0.4 (2026-05-18)
**First Complete Edition**

- Inner alchemy · Nine-grade cultivation · Twelve anchor frames
- 35KB code
- Tri-party review (Doubao/Qwen/DeepSeek)

---

**Rollback**: `git checkout <tag>`
**Back to latest**: `git checkout master`
