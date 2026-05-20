# Tongzi · Bit-Store Responder — A Thought Experiment

**41KB. Zero dependencies. No training. No Transformer. Not a product. A thought experiment in pure F₂ evolution.**

---

## What Is This?

A thought experiment: what if we built a text response system without any neural components?

No training data. No Transformer. No gradient descent. No attention. No word embeddings. No floating point.

Instead:
- **BitStore**: 16-bit F₂ vector space (65,536 possible states), Hamming-distance retrieval
- **Balancer**: 12 polarity flags (6 yang + 6 yin), auto-correcting
- **Responder**: Three-stage pipeline — ingest → cluster → respond

All constants derived from Euler's identity and the golden ratio, locked. The system runs on pure bitwise operations.

---

## Architecture

### Layer 1: BitStore
- 16-bit integer vectors, stored in a dict
- ord-sum encoding: `sum(ord(c)) & 0xFFFF`
- Hamming distance for nearest-neighbor search
- `tongzi_constants.py` + `tongzi_core.py`

### Layer 2: Balancer
- 12 polarity flags, 6 yang (gather/pair/flow/rise/generate/link) + 6 yin (scatter/break/reverse/descend/trace/cut)
- Auto-balance when gap ≥ 3
- Periodic marking of stale entries
- `tongzi_mao.py`

### Layer 3: Responder
- Three-stage pipeline: ingest input → cluster similar vectors → select response
- 9 hardcoded output strings, chosen by frequency tier + cluster presence + polarity gap
- Anomaly detection: silently store inputs too far from all known vectors
- `tongzi_data.py`

---

## Quick Start

```bash
python tongzi.py
```

Requirements: Python 3.6+. Zero dependencies. Any device.

| Command | Purpose |
|:--|:--|
| Type text | Encode → ingest → respond |
| `/status` | View entries, active count, clusters, polarity gap |
| `/exit` | Quit |

---

## Current Baseline

9 possible responses, chosen by an if-else tree.

60 seed vectors, 12 polarity categories, 15 cluster labels.

Test script: `python src/boundary_test.py`

---

## File Structure

```
├── src/
│   ├── tongzi_constants.py   # Locked constants
│   ├── tongzi_core.py        # BitStore: F₂ vector store
│   ├── tongzi_mao.py         # Balancer: polarity scheduling
│   ├── tongzi_data.py        # Responder: ingest→cluster→respond
│   ├── tongzi_seeds.py       # 60 seed vectors
│   ├── tongzi.py             # Interactive entry point
│   ├── water.py              # Cron watering script
│   └── boundary_test.py      # Read-only boundary observer
├── README.md
├── FAILURE_BOUNDARIES.md     # Honest assessment of limitations
├── LICENSE                   # MIT
└── docs/                     # Theory notes (Chinese)
```

---

## Iron Laws

1. No modification of locked constants
2. No manual response logic injected into the store
3. No third-party NLP/semantic/pretrained modules
4. No floating-point, matrix multiplication, or gradient descent
5. No grammar rules or conversation templates
6. Feed only seed concepts — never chat corpora
7. No manual cluster manipulation
8. No fourth layer beyond the three-layer architecture
9. No splitting emotion/grammar into separately tuned modules
10. Keep the open-source declaration in every source file header

---

## License

MIT

---

*A thought experiment. Not a chatbot. Not an attempt to beat benchmarks. Just F₂ bits and a question.*
