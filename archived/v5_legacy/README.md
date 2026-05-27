# Tongzi · F₂ Collision Engine

**An alternative AI substrate built on pure F₂ space (GF(2) XOR/AND collisions).**

Not an LLM. Not a neural network. Not a token predictor.

Zero floats · Zero matrices · Zero gradients · Zero embeddings · Zero attention · Zero external deps

---

## Quick Start

```bash
git clone https://github.com/wishing-spring/tongzi-ai.git
cd tongzi-ai
python demo.py
```

`pip install nothing`.

---

## Core Mechanism

```
Chinese chars → 4-suit pinball encode → 80 × 28-bit F₂ vectors
  ↓
Surge Pool (XOR/AND collision + sliding window + anti-entropy jitter)
  ↓
Eco Pool (birth → solidify → attractor emergence)
```

300 ticks, ~380k XOR/AND collisions. 20 chars → 20 distinguishable attractor clusters.

---

## Code

```
src/
├── v3/           F₂ Collision Engine (zero deps)
│   ├── encode.py       Four-suit pinball encoding
│   ├── constants.py    φ mother body, bit masks
│   ├── gua.py          Gua (F₂ point)
│   ├── surge.py        Surge sliding window
│   ├── surge_pool.py   Eternal pool
│   ├── eco_pool.py     Eco pool + anti-entropy
│   └── express.py      Nearest-neighbor expression
└── v4/           Self-model layer (tianyuan, spine, fold, gravity, causal)
```

| Iron Rules |
|:--|
| Zero floats · Zero matrix multiplication · Zero gradient descent |
| Zero embeddings · Zero attention · Zero autoregression |
| Zero external dependencies · Pure Python · Pure bitwise operations |

---

## Honest Disclosure

**F₂ collisions produce 28-bit vectors and attractor distributions.**

The mapping from bit vectors to natural language currently uses a template bridge (`speak.py`). This is not F₂-native generation. We document this honestly — we don't pretend F₂ produces Chinese text.

What's real: without any floating point, matrices, or gradients, F₂ collision dynamics produce distinguishable input-to-attractor mappings.

---

## Experiments

[experiments/](experiments/) — v1 attractor verification, v2 32-bit expansion, density parameter scans

---

## Version History

| Tag | Milestone |
|:--|:--|
| v0.5 | Loom weaver + Balancer + Responder |
| v1.2 | Four axioms + φ mother + 8 operations + attractor verification |
| v2.3 | 32-bit pinball encoding + tri-axis TMR + radical checkpoint |
| **v3.0** | **Surge eternal pool + eco birth pools + anti-entropy** |
| **v4.0** | **Dual tianyuan · spine memory · fold · gravity · causal probe** |

Older docs → [archive/](archive/)

---

MIT © 2026 [wishing-spring](https://github.com/wishing-spring)
