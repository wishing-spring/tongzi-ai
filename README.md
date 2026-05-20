# Tongzi · F₂ Minimalist Group-Domain Architecture — A Thought Experiment

**v1.0.2 | 4 files, ~25KB | Zero dependencies | Zero floats | Zero matrices | Zero gradients | Zero attention | Zero autoregression**

*Not a better AI. A different one. A thought experiment in pure GF(2) discrete space.*

---

## Essence

Tongzi is not an algorithm, not a model, not a processor.

It is an **F₂ⁿ space**. Gua (卦) are points within it. Their associations, alignments, arrangements, and movements are properties of the space itself — not imposed by external rules.

```
Not: input → encode → process → output (pipeline)
But:  F₂ⁿ space + gua population + natural interaction laws
```

---

## Four Axioms (Immutable, Dimension-Independent)

| # | Axiom | Meaning |
|:--|:--|:--|
| 1 | a⊕b = b⊕a | XOR commutativity |
| 2 | a⊕a = 0 | XOR self-cancellation |
| 3 | d(a,b) = popcount(a⊕b) | Hamming distance |
| 4 | d(Rₖ(a), Rₖ(b)) = d(a,b) | Rotation preserves distance |

These four hold for VEC_DIM=16 and for VEC_DIM=65536 equally. No n appears anywhere in the axioms. From them derive: AND (a∧b), cyclic bit rotation Rₖ(v), and the Hamming ball Sᵣ(c).

---

## φ — The Mother Body

All gua originate from the binary fractional expansion of the golden ratio:

```
φ = (1+√5)/2 ≈ 1.6180339...
φ_bits = 1001111000110111... (256 bits, Decimal precision)
```

Each gua is a slice of φ:

```
gua = φ_bits[pos : pos+length]
```

Every gua carries identity at birth:
- **id_t** = pos — birth order in φ
- **id_l** = length — layer code (number of yao)
- Slide ±1 bit → direct predecessor/successor (lineage)

`{id_t, id_l}` is the gua's ID card — globally unique, derived from φ position, no database needed.

---

## Eight Core Operations

### 1. Collision — Full Information Expansion
```
collide(a, b) → (a⊕b, a∧b)
```
Two inputs, two outputs. Information is preserved — diff vector and consensus vector.

### 2. Orbital Circulation
```
orbit(v, c, k) = Rₖ(v⊕c) ⊕ c
```
v rotates around center c on an equidistant spherical surface. d(v,c) invariant.

### 3. Radial Stretch
```
stretch(v, c, λ) = v ⊕ λ·(v⊕c)
λ ∈ {0,1}: 0 = stay, 1 = push to opposite side
```

### 4. Gray Inspection Ring
```
gray(v) = v ⊕ (v>>1)
```
All gua form a ring — adjacent nodes differ by exactly 1 bit. Natural traversal path.

### 5–8. Distance, Clustering, Centrality, Hierarchical Index
```
radius(v, c)     = d(v, c)
Ω(c, r)          = {x | d(x, c) ≤ r}      — Hamming ball
centrality(v, c) = −d(v, c)
layer(v)         = id_l(v),  order(v) = id_t(v)
```

---

## Endogenous Frequency Control

No external clock. Frequency emerges from identity.

### Birth-Order Frequency
```
f₁(x) = F₀ / (1 + id_t)     → rate (energy gained per tick)
```
Early-born gua (small id_t) gain energy fast → high frequency.

### Layer-Differential Frequency
```
f₂(x) = F₀ / (1 + id_l)     → rate
```
Shallow-layer gua interact densely; deep-layer gua interact sparsely.

### Energy Accumulation Trigger
```
per tick:  energy += min(f₁, f₂)
energy ≥ F₀ → discharge (participate), energy −= F₀
```
F₀ = 256. Solidified gua never discharge.

---

## Bit-Field Solidification — Irreversible Memory

Each gua naturally splits into two segments:

| Segment | Source | Property |
|:--|:--|:--|
| Core | φ base bits, length = id_l | Immutable root |
| Moving | φ sliding extension | Evolvable |

```
Solid(x)   = G(x) ∧ M(x)
M(x)       = mask(id_l, id_t)    — derived from identity, not stored
```

Core bits are permanently locked — they never participate in XOR, rotation, or stretch. Moving bits remain free.

**Trigger (endogenous):** collision count exceeds threshold (lower for deeper layers → deeper gua solidify faster).

**Weak unlock:** only direct lineage (pos±1) may micro-adjust a single locked bit — prevents complete rigidity.

---

## Spatial Self-Awareness & Density Regulation

### Local Density Perception
```
S(x) = N / (d̄_H + 1)
  N  = same-layer gua within Hamming radius r
  d̄_H = average Hamming distance among neighbors
```
S large = crowded. S small = sparse.

### λ Auto-Adjustment (Negative Feedback)
```
λ_new = λ_base × (1 − μ(id_l) × S / S_max)
```
Crowding sensed → λ increases → gua spread outward → S drops (closed loop).

### μ Sensitivity — Purely Endogenous
```
μ(id_l) = id_l / L_max
  L_max = current maximum layer code (computed at runtime, not a parameter)
```
Shallow gua: low μ (tolerant of crowding). Deep gua: high μ (avoidance on slightest crowding).

### Dual-Layer Volume Control
```
Mild congestion  → self-disperse (pre-regulation, gentle)
Extreme overload → density-triggered merge (post-safety, forceful)
```

---

## Minimal Inner Alchemy — Reverse Translation

```
express(gua) = source_text of gua with minimum Hamming distance to moving_bits
```

Not a fixed response. Not a template. The gua's current state maps back to the closest remembered source text.

---

## Current Code Status

| File | Lines | Content |
|:--|:--|:--|
| `src/tongzi_constants.py` | 28 | VEC_DIM=16, FULL_MASK, PHI_BITS(256) |
| `src/tongzi_core.py` | 680 | Gua class + Space container: 8 ops + solidification + density + express |
| `src/tongzi.py` | 108 | Interactive entry point |
| `src/test_tongzi.py` | 250 | 81 tests, 13 sections, 0 failures |

**Iron Rules:**
- ❌ No floats
- ❌ No matrix multiplication
- ❌ No gradient descent
- ❌ No word embeddings
- ❌ No attention
- ❌ No autoregression
- ❌ No neural networks of any form

---

## Removed (v0.5 → v1.0)

| Component | Reason |
|:--|:--|
| Loom (GF(2) 2D weaver) | Collide + orbit + stretch subsume weaving |
| Balancer (yin-yang flags) | Thresholds bound to n; replaced by endogenous f₁+f₂ |
| Responder (9 fixed replies) | Form without soul; output is now collision products |
| 12 Anchor Frames | 12 is a fixed number |
| ⌊√n⌋ / ⌊n/3⌋+4 | Contain n |
| External cron watering | Replaced by density self-clean + endogenous frequency |
| Projection mapping | Decoration, no substance |

---

## Known Costs (Accepted)

| Cost | Note |
|:--|:--|
| No continuous transitions | F₂ is discrete, no gradients |
| Output not directly readable | Collision results are bit strings |
| Reversibility | **Resolved** — bit-field solidification = local irreversibility |
| Evolution trapped in combinatorial pool | All operations are rearrangements in finite set |
| Pseudo-3D | Hamming ball is not a true geometric body |
| No external clock | Silence when no input (by design) |

---

## License

MIT

---

## Repositories

- **Gitee (primary):** https://gitee.com/wishing-spring/tongzi-ai
- **GitHub (mirror):** https://github.com/wishing-spring/tongzi-ai

---

**Theory finalized. Code v1.0.2 landed. Next: observe, do not add new features.**
