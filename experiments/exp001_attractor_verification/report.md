# Experiment 001 — Attractor Verification

**Date**: 2026-05-21 | **Tongzi version**: v1.2 | **Triggered by**: GPT-4 review

---

## Question

After 100 ticks with 20 Chinese seed words, 9 source words' `express()` converged to "地" (earth). Is this:

1. **Real emergence** — dynamics genuinely created a structural attractor?
2. **Encoding bias** — φ mother body just happens to encode "地" at a central position?
3. **Hamming space clustering** — any random set of bit vectors naturally collapses?
4. **Small space collapse** — 16-bit space only has 65536 states, collapse is inevitable?

---

## Method

### Test A: Static Centrality
20 seed vectors analyzed in pure Hamming space with zero dynamics — just geometric centrality (average Hamming distance to all other vectors).

### Test B: Reproducibility
3 independent trials with φ mother body, 100 ticks each.

### Test C: Mother Body Control
Swap φ for π binary expansion and 5 random 256-bit strings. 100 ticks each. Count drift events and identify attractors.

---

## Results

### A: Static Centrality

| Rank | Word | Avg Hamming | 
|:--|:--|:--|
| 1 | 火 (fire) | 7.0 |
| 1 | 冷 (cold) | 7.0 |
| 3 | 湿 (wet) | 7.1 |
| 4 | 星 (star) | 7.2 |
| 5 | 日 (sun) | 7.3 |
| 5 | 月 (moon) | 7.3 |
| **7** | **地 (earth)** | **7.4** |
| ... | ... | ... |
| 20 | 光 (light) | 8.3 |

**"地" is NOT the static geometric center. It ranks #7.**

### B: Reproducibility (φ, 3 trials)

| Trial | Drifts/20 | Attractor | Sources |
|:--|:--|:--|:--|
| 1 | 11 | 地 | 10 |
| 2 | 11 | 地 | 10 |
| 3 | 11 | 地 | 10 |

**100% reproducible. Identical results across trials.**

### C: Mother Body Control

| Mother Body | Drifts/20 | Attractor | Sources | Fertility |
|:--|:--|:--|:--|:--|
| φ | 11 | 地 | 10 | ★★★★ |
| π | 12 | 湿 | 11 | ★★★★ |
| Random 1 | 12 | 湿 | 11 | ★★★★ |
| Random 2 | 17 | 水 | 16 | ★★★★★ |
| Random 3 | 11 | 星 | 10 | ★★★★ |
| Random 4 | 11 | 水 | 10 | ★★★★ |
| **Random 5** | **4** | **动** | **3** | **★** |

---

## Verdicts on All Four Hypotheses

| Hypothesis | Verdict | Reason |
|:--|:--|:--|
| Encoding bias | ❌ Falsified | "地" ranks #7 statically; "火"/"冷" are more central yet don't attract. |
| φ-bias | ❌ Falsified | π and random mother bodies produce equally strong attractors. |
| Hamming clustering | ❌ Falsified | Most central nodes ("火", "冷") are NOT attractors. |
| Small-space collapse | ❌ Falsified | Random 5 produces only 4/20 drift — not all spaces collapse. |
| **Structural attractor** | **✅ Confirmed** | Dynamics (XOR/AND + solidification + energy) create attractor basins. Specific attractor depends on mother body, but "exists an attractor" does not. |

---

## Three-Layer Conclusion

| Layer | Question | Answer |
|:--|:--|:--|
| 1 | Does the system spontaneously form attractors? | **Yes.** φ, π, and random bodies all produce them. |
| 2 | Why *this specific* attractor? | Mother body encoding determines which bit-pattern becomes the basin. |
| 3 | Are all mother bodies equally fertile? | **No.** Random 5 (4/20) vs Random 2 (17/20) shows strong fertility variation across mother bodies. |

---

## Significance

1. Attractor mechanism is **endogenous dynamics**, not φ magic.
2. Mother body acts as "soil" — determines *where* the flower grows and *whether* anything grows at all.
3. Random 5's 4/20 is the most important number in the dataset — it proves ecological differentiation exists. Some mother bodies are fertile; others are barren. This is the first signal of **environmental selection**, which GPT identified as the system's key missing piece.

---

## Files

- Test scripts: `src/test_attractor.py`, `src/test_control.py`
- Raw output: see experiment run logs above
