# Tongzi · Evolution Log

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
