# Tongzi · F₂ Minimalist Group-Domain Architecture — A Thought Experiment

**v1.2 | 3 source files, ~25KB | Zero dependencies | Zero floats | Zero matrices | Zero gradients | Zero attention | Zero autoregression**

*Not a better AI. A different one. Built from scratch on pure GF(2) discrete space.*

---

## Essence

Tongzi is not an algorithm, not a model, not a processor.

It is an **F₂ⁿ space**. Gua (卦 yuan) are points within it. Their associations, alignments, arrangements, and movements are properties of the space itself — not imposed by external rules.

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

From these derive: AND (a∧b), cyclic bit rotation Rₖ(v), and the Hamming ball Sᵣ(c).

---

## φ — The Mother Body

All gua originate from the binary fractional expansion of the golden ratio:

```
φ = (1+√5)/2 ≈ 1.6180339...
φ_bits = 1001111000110111... (256 bits)
```

Each gua is a slice of φ. Every gua carries identity at birth: **id_t** (birth order) and **id_l** (layer depth).

---

## Eight Core Operations

| # | Operation | Formula | Purpose |
|:--|:--|:--|:--|
| 1 | Collision | (a⊕b, a∧b) | Full expansion — diff + consensus |
| 2 | Orbit | Rₖ(v⊕c) ⊕ c | Rotate around center |
| 3 | Stretch | v ⊕ λ·(v⊕c) | Push toward / away from center |
| 4 | Gray ring | v ⊕ (v>>1) | Adjacent 1-bit traversal |
| 5 | Distance | d(v,c) = popcount(v⊕c) | Exact Hamming distance |
| 6 | Cluster | Ω(c,r) = {x | d(x,c) ≤ r} | Hamming ball |
| 7 | Centrality | −d(v,c) | Proximity to center |
| 8 | Layer index | id_l(v), id_t(v) | Identity from φ |

---

## Gua Merging — v1.2 New

When two gua collide, if their Hamming distance falls within the merge window, two child gua are spawned simultaneously:

### Merge Criterion
```
h = popcount(a ⊕ b)
Merge if:  4 < h < 12   (VEC_DIM/4 ∼ 3·VEC_DIM/4)
```
Too close → no new information. Too far → unrelated. Sweet spot → merge.

### XOR Merge — Difference Chain
```
C_xor = a ⊕ b
```
Association, contrast, progression. Reversible: C_xor ⊕ a = b, C_xor ⊕ b = a.

### AND Merge — Consensus Deposit
```
C_and = a ∧ b
```
Generalization, rule extraction. Complements XOR's blind spot for shared information.

### Merge Rules
- Original gua (A, B) **never modified** — merge produces additional children only
- Zero-value children (XOR or AND result = 0) are skipped
- Merge children follow the same frequency control + density self-cleaning as all gua

---

## Endogenous Frequency Control (v1.2 Simplified)

```
rate = F₀ / (1 + id_l)     → energy gained per tick
```

Shallow gua (small id_l) → fast. Deep gua (large id_l) → slow.
Same-layer gua share the same rhythm. Birth order no longer skews frequency.

```
per tick:  energy += rate
energy ≥ F₀ (256) → discharge, energy = 0
```

Solidified gua never discharge.

---

## Bit-Field Solidification — Irreversible Memory

Core bits (derived from id_l mask) are permanently locked — never participate in XOR, rotation, or stretch. Moving bits remain free.

Triggered when collision count exceeds threshold. Deep gua solidify faster.

---

## Spatial Self-Awareness & Density Regulation

```
S(x) = N / (d̄_H + 1)                      — local crowding
λ_new = λ_base × (1 − μ · S/S_max)        — auto-disperse (negative feedback)
μ = id_l / L_max                           — sensitivity (pure endogenous)
```

Crowded → gua spread out → density drops → closed loop. Overload → forceful merge.

---

## Minimal Inner Alchemy — Reverse Translation

```
express(gua) = source_text of gua with minimum Hamming distance
```

Not a fixed response. The gua's current bit-state maps back to the closest remembered word.

---

## Code Status

| File | Lines | Content |
|:--|:--|:--|
| `src/tongzi_constants.py` | 28 | VEC_DIM=16, FULL_MASK, φ_bits(256) |
| `src/tongzi_core.py` | ~690 | Gua class + Space container: 8 ops + solidification + density + merge + express |
| `src/tongzi.py` | ~197 | Interactive entry: ingest, /tick, /status, /list, /show, /chain |
| `src/test_tongzi.py` | ~315 | 80 tests, 13 sections, 0 failures |

**Iron Rules:** No floats. No matrices. No gradients. No embeddings. No attention. No autoregression. No neural networks.

---

## Evolution

| Tag | Date | Milestone |
|:--|:--|:--|
| v0.5 | May 19 | Loom weaver + Balancer + Responder, open-sourced |
| v1.0-arch | May 20 | Theory finalized: four axioms, φ mother, eight operations |
| v1.0-code | May 20 | Code landing, removed old Loom pipeline (6 files) |
| v1.0.2 | May 20 | Inner alchemy: express() reverse translation |
| v1.1 | May 20 | /chain association chains |
| v1.2 | May 20 | Gua merging: XOR+AND dual-chain + criterion + rate simplification |

Full evolution log: [CHANGELOG.md](CHANGELOG.md)

---

## Live Evidence — 20 Words, 100 Ticks

A reproducible demo: 20 Chinese single-character words ingested, 100 ticks run, zero human intervention. Full log: `src/demo_100tick_output.txt`

```
20 seeds → 47 gua (135% growth through XOR+AND merging)
24 solidified (51%, irreversible memory)
23 active (49%, still colliding)
```

### Emergent Attractor: "地" (Earth)

After 100 ticks, **9 of 20 original seeds had express() converge to "地"**:

| Source word | Original meaning | express() after 100 ticks |
|:--|:--|:--|
| 火 | fire | 地 |
| 干 | dry | 地 |
| 空 | emptiness | 地 |
| 湿 | wet | 地 |
| 动 | move | 地 |
| 冷 | cold | 地 |
| 日 | sun | 地 |
| 雷 | thunder | 地 |
| 静 | still | 地 |

**These 9 words had zero programmed relationship.** Fire, sun, thunder, cold, dry, wet, move, still, emptiness — no taxonomy, no ontology, no embedding. They converged because bit-patterns drifted through XOR/AND collisions and "地" became the nearest Hamming neighbor for all of them.

Meanwhile, merge children (those born from XOR/AND during collision, with no source text) clustered around **"光" (light)**, **"日" (sun)**, and **"雷" (thunder)** — forming a two-layer structure: inward gravitational center ("地") + outward diffusion clusters.

This is **not designed**. It is **emerged**.

---

## Known Limitations

| Limitation | Explanation |
|:--|:--|
| 16-bit encoding collisions | F₂¹⁶ has only 65,536 possible states. Different inputs may map to the same gua. This is inherent to the 16-bit space, not a bug — treat it as "finite memory capacity." |
| express() is retrieval, not generation | `express()` finds the nearest neighbor in Hamming space and returns its original source text. It does not synthesize new content. The system is an **associative memory vessel** with endogenous dynamics, not a chatbot. |
| Not a consumer product | No training, no inference, no benchmarks. This is a thought experiment exploring whether structure emerges from pure F₂ space + φ origin — nothing more. |

### On 16-bit: Not a Cap, a Foundation Stage

VEC_DIM=16 is the **current** dimension, not a permanent ceiling. The four axioms are dimension-independent — 32-bit, 64-bit, 128-bit all self-consistent. The merge criterion, frequency control, solidification, and density regulation all scale automatically.

At 32 bits: **4.2 billion possible gua states** — collision risk drops exponentially. φ has 256 bits in reserve, more than enough to feed wider dimensions.

16-bit is the seedbed: keep the space small, observe structural emergence, confirm the self-organizing mechanisms work, then unlock larger dimensions. Like an infant's neural capacity — limits are developmental, not architectural.

---

## Known Costs (Accepted)

| Cost | Note |
|:--|:--|
| No continuous transitions | F₂ is discrete |
| Output is bit strings | Not human-readable without express() |
| Finite combinatorial pool | All operations are rearrangements |
| No external clock | Silence when no input (by design) |

---

## License

MIT © 2026 [wishing-spring](https://github.com/wishing-spring)

---

## About the Author

I'm a pure hobbyist — not a programmer, never wrote code before this project. Everything here was built through conversation with my AI assistant **Copperbeard** (铜须, a blacksmith/dream-builder), with external consultation from **Doubao AI**.

The goal: find a new underlying framework for AI that doesn't rely on matrices, gradients, attention, or neural networks. This is a thought experiment, not a product.

---

*"Not a better AI. A different one."*
