# Tongzi · Bit-Store Responder — A Thought Experiment

**41KB. Zero dependencies. No training. No Transformer. Not a product. A thought experiment in pure F₂ evolution.**

---

## What Is This?

A thought experiment: what if we built a text response system without any neural components?

No training data. No Transformer. No gradient descent. No attention. No word embeddings. No floating point.

Instead:
- **BitStore**: 16-bit F₂ vector space (65,536 possible states), Hamming-distance retrieval
- **Loom**: GF(2) 2D weaving engine — XOR diffusion + AND nonlinearity + S-box scramble + reference anchoring. Four-layer hybrid. Zero collapse.
- **Balancer**: 12 polarity flags (6 yang + 6 yin), auto-correcting
- **Responder**: Three-stage pipeline — ingest → cluster → respond

All constants derived from Euler's identity and the golden ratio, locked. The system runs on pure bitwise operations.

---

## Core Innovation: GF(2) 2D Weaving

The Loom is a **16-bit block cipher** built entirely in GF(2):

```
output_bit = XOR(selected bits) ^ AND(two specific bits) ^ ref_bit
```

Each layer applies this formula 16 times (once per output bit), followed by a 4-bit S-box substitution. After 18 layers:
- **Zero collapse**: every input maps to a unique fabric state (497/500 unique)
- **Avalanche effect**: flipping 1 input bit changes avg 8.3 output bits
- **Nonlinearity verified**: `out(a|b) ≠ out(a) ^ out(b)`

Three layers independently tested and verified to fail without the fourth:
| Missing | Result |
|:--|:--|
| XOR only | Collapse at 5 layers (5/5 collision) |
| XOR+S-box | Fixed-point convergence (100→1) |
| XOR+AND (no ref) | 29/200 unique at depth 8 |
| XOR+AND+S-box+ref | **200/200 at all depths** |

---

## Architecture

### Layer 0: Loom (GF(2) Weaver)
- 16-bit input → 18-layer 16×16 gate matrix → 16-bit fabric output
- XOR masks for linear diffusion, AND gates for nonlinear breaking
- Per-layer S-boxes (rotated + XOR-mixed for uniqueness)
- Reference anchoring: each layer XORs back one bit of original input
- `tongzi_loom.py`

### Layer 1: BitStore
- 16-bit integer vectors, stored in a dict
- ord-sum encoding: `sum(ord(c)) & 0xFFFF`
- Hamming distance for nearest-neighbor search
- Persistent state: `.tongzi_state.json` auto-saves/loads
- `tongzi_constants.py` + `tongzi_core.py`

### Layer 2: Balancer
- 12 polarity flags, 6 yang + 6 yin
- Auto-balance when gap ≥ 3
- Periodic marking of stale entries
- `tongzi_mao.py`

### Layer 3: Responder
- Three-stage pipeline: ingest → cluster → respond
- 9 hardcoded output strings
- Anomaly detection: silently store inputs too far from known vectors
- `tongzi_data.py`

---

## Scaling: Stacking vs Tiling

The fundamental difference between industry and Tongzi:

| | Stacking (Industry) | Tiling (Tongzi) |
|:--|:--|:--|
| **How** | Layer on layer (serial) | Side by side (parallel) |
| **Info flow** | One-way, layer→layer | All-way, all bits interact |
| **Entropy** | Halves per layer | Doubles per tile |
| **Limit** | ~5 layers (pure binary) | No theoretical limit |
| **Scaling** | Retrain from scratch | Change one constant: `VEC_DIM` |

[V5_TO_V6_PLAN.md](src/V5_TO_V6_PLAN.md) — one-constant upgrade path from 16-bit to 32-bit fabric.

---

## Quick Start

```bash
cd src && python tongzi.py
```

Requirements: Python 3.6+. Zero dependencies. Any device.

| Command | Purpose |
|:--|:--|
| Type text | Encode → ingest → respond |
| `/status` | View entries, active count, polarity gap |
| `/exit` | Quit |

---

## File Structure

```
├── src/
│   ├── tongzi_constants.py   # Locked constants
│   ├── tongzi_loom.py        # GF(2) 2D weaving engine
│   ├── tongzi_core.py        # BitStore: F₂ vector store
│   ├── tongzi_mao.py         # Balancer: polarity scheduling
│   ├── tongzi_data.py        # Responder: ingest→cluster→respond
│   ├── tongzi_seeds.py       # 60 seed vectors
│   ├── tongzi.py             # Interactive entry point
│   ├── water.py              # Cron watering script
│   ├── boundary_test.py      # Read-only boundary observer
│   └── V5_TO_V6_PLAN.md      # Scaling roadmap
├── README.md / README_CN.md
├── GF2_VS_BNN.md             # GF(2) weaving vs industrial BNN
├── ROADMAP.md                # Full comparison: float vs F₂
├── FAILURE_BOUNDARIES.md     # Honest assessment of limitations
├── LICENSE                   # MIT
└── docs/                     # Theory notes (Chinese)
```

---

## Iron Laws

1. No modification of locked constants
2. No manual response logic
3. No third-party NLP/semantic/pretrained modules
4. No floating-point, matrix multiplication, or gradient descent
5. No grammar rules or conversation templates
6. Feed only seed concepts — never chat corpora
7. No manual cluster manipulation
8. No fourth layer beyond the three-layer architecture
9. No splitting emotion/grammar into separate modules
10. Keep the open-source declaration in every source file header

---

## License

MIT

---

*A thought experiment. Not a chatbot. Not an attempt to beat benchmarks. Just F₂ bits and a question.*
