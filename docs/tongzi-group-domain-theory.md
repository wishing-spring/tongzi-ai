# Tongzi · Minimalist Group-Domain Architecture (Final)

**Date**: 2026-05-20 | **Status**: v1.2 Merge Formulas Finalized

---

## 1. Essence

Tongzi is not an algorithm, not a model, not a processor.

It is an **F₂ⁿ space**. Gua are points within it. Their associations, alignments, arrangements, and movements are properties of the space itself — not imposed by external rules.

---

## 2. Four Axioms (Immutable)

| # | Axiom | Meaning |
|:--|:--|:--|
| 1 | a⊕b = b⊕a | XOR commutativity |
| 2 | a⊕a = 0 | XOR self-cancellation |
| 3 | d(a,b) = popcount(a⊕b) | Hamming distance |
| 4 | d(Rₖ(a),Rₖ(b)) = d(a,b) | Rotation preserves distance |

These hold for any dimension. No `n` appears.

---

## 3. φ Mother Body — Birth & Identity

```
φ = (1+√5)/2 ≈ 1.6180339...
φ_bits = 1001111000110111... (256 bits)

gua = φ_bits[pos:pos+length]
```

Every gua carries:
- **id_t = pos** — birth order
- **id_l = length** — layer depth

---

## 4. Eight Core Operations

1. **Collision**: `(a⊕b, a∧b)` — diff + consensus, two-in two-out
2. **Orbit**: `Rₖ(v⊕c) ⊕ c` — rotate around center on equidistant sphere
3. **Stretch**: `v ⊕ λ·(v⊕c)` — λ∈{0,1}: stay / push to opposite
4. **Gray Ring**: `v ⊕ (v>>1)` — adjacent 1-bit traversal
5. **Distance**: `d(v,c) = popcount(v⊕c)`
6. **Cluster**: `Ω(c,r) = {x | d(x,c) ≤ r}` — Hamming ball
7. **Centrality**: `−d(v,c)`
8. **Layer Index**: `id_l(v)`, `id_t(v)`

---

## 4-B. Gua Merging (v1.2)

When two gua collide, if their Hamming distance falls in the merge window (4, 12):

### Merge Criterion
```
h = popcount(a ⊕ b)
Merge if: 4 < h < 12  (VEC_DIM/4 ∼ 3·VEC_DIM/4)
```

### XOR Merge — Difference Chain
```
C_xor = a ⊕ b
d_H(C_xor, a) = popcount(b)  — fusion depth = partner's weight
```
Reversible: C_xor ⊕ a = b, C_xor ⊕ b = a. Association, contrast, progression.

### AND Merge — Consensus Deposit
```
C_and = a ∧ b
```
Generalization, rule extraction. Complements XOR's blind spot.

### Merge Rules
- Original gua (A, B) **never modified** — collision unchanged, merge is additive
- Zero-value children skipped
- Merge children follow same frequency + density rules
- Density self-cleaning handles useless children naturally

### Dual-Chain Semantics
| Chain | Operation | Use |
|:--|:--|:--|
| XOR | A ⊕ B | Association, contrast, progression |
| AND | A ∧ B | Generalization, consensus, rule extraction |

---

## 5. Endogenous Frequency Control (v1.2 Simplified)

```
rate = F₀ / (1 + id_l)     → energy per tick
```

Shallow gua (small id_l) → fast. Deep gua → slow.
Same-layer = same rhythm. No birth-order bias.

```
per tick:  energy += rate
energy ≥ F₀ (256) → discharge, energy = 0
```

Solidified gua never discharge.

---

## 6. Bit-Field Solidification — Irreversible Memory

| Segment | Source | Property |
|:--|:--|:--|
| Core | φ base bits, length = id_l | Immutable |
| Moving | φ sliding extension | Evolvable |

```
Solid(x) = G(x) ∧ M(x)
M(x) = mask(id_l, id_t)  — identity-derived
```

Core bits permanently locked. Moving bits remain free.

**Trigger**: collision count exceeds threshold. Deeper gua solidify faster.
**Weak unlock**: only direct lineage (pos±1) may micro-adjust — prevents total rigidity.

---

## 7. Spatial Self-Awareness & Density Regulation

```
S(x) = N / (d̄_H + 1)                     — local crowding
λ_new = λ_base × (1 − μ·S/S_max)         — auto-disperse
μ = id_l / L_max                          — sensitivity (endogenous)
```

Crowded → λ increases → gua spread → density drops → closed negative-feedback loop.

### Dual-Layer Volume Control
```
Mild congestion  → self-disperse (gentle)
Extreme overload → density merge  (forceful)
```

---

## 8. Removed (v0.5 → v1.0)

| Component | Reason |
|:--|:--|
| Loom weaver | Collide+orbit+stretch subsume weaving |
| Balancer | Thresholds bound to n; replaced by endogenous rate |
| Responder (9 replies) | Form without soul |
| 12 Anchor Frames | 12 is a fixed number |
| ⌊√n⌋ / ⌊n/3⌋+4 | Contain n |
| External cron | Replaced by density self-clean |
| Projection mapping | Decoration |

---

## 9. Framework Properties

| Property | Mechanism |
|:--|:--|
| Dimension-independent | Four axioms + eight ops contain no n |
| Inherent order | φ birth sequence = natural order |
| Self-referential | Status bits = gua knows its type |
| Mixed-size gua | Different length gua coexist |
| Natural hierarchy | id_l distinguishes inner/outer layers |
| Free morphology | Birth-order / Gray-ring / Hamming-sphere arrangements |

---

## 10. Known Costs (Accepted)

| Cost | Note |
|:--|:--|
| No continuous transitions | F₂ discrete |
| Output = bit strings | Needs express() for readability |
| Local irreversibility | Solidification = one-way |
| Finite combinatorial pool | All ops are rearrangements |
| Pseudo-3D | Hamming ball ≠ true geometry |
| No external clock | Silence without input (by design) |

---

**Theory finalized. v1.2 merge formulas landed. 80 tests, 0 failures.**
