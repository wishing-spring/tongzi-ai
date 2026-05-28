# Lingxi v8.3 — Discrete Structure Reducer

**Zero training. Zero gradient. Bit-level auditable. Pure F₂ operations.**

A 28-bit artificial life system with child persona (age 10), self-growth,
dreaming engine, personality filter, and semantic co-occurrence learning.

## Quick Start

```python
import lingxi
lingxi.demo()   # run evidence experiments
lingxi.start()  # interactive session (GUI if available)
```

Or from the command line:

```bash
pip install .        # zero external dependencies
python -c "import lingxi; lingxi.demo()"
```

## Architecture

| Layer | Component | Operations |
|:------|:----------|:-----------|
| Bit-Vector | `guayuan` | 28-bit XOR, Hamming distance, radical-Gray encoding |
| Oscillation | `yinyang` | Yin-yang heartbeat drives world-layer evolution |
| World | `shared_pool` | 195 active stars, 13 clusters, 414 co-occurrence edges |
| Rules | `rule_tree` | 106 rules, direct substring matching, self-growth via crystallization |
| Inference | `bagua_core` | 64-cell think-chain engine with shortest-path reasoning |
| Personality | `tongzi_experience` | 10-year-old filter: 7 allow / 4 block rules |
| Output | `child_window` / `live_child` | Tkinter GUI or terminal interactive mode |

## Evidence Experiments

Three controlled experiments demonstrating system properties:

1. **Refuse-to-Answer**: forbidden input reduces to ANNIHILATE
2. **Separation**: similar characters map to distinct rule paths
3. **Self-Growth**: repeated collision triggers rule crystallization

```bash
python demo_evidence.py
```

## System Properties

| Property | Value |
|:---------|:------|
| Vector width | 28 bits |
| Operations | XOR, Hamming, bit_count |
| Floating-point | None (zero) |
| Gradients | None (zero) |
| Word embeddings | None (zero) |
| External knowledge | None (zero) |
| Dependencies | Python 3.8+ standard library only |
| Active entities | 195 stars, 13 clusters, 106 rules |
| Personality | 10-year-old child, 7 allow / 4 block |

## Files

```
lingxi/
  __init__.py           Package entry: start(), demo()
  guayuan.py            Bit-vector core (28-bit XOR/Hamming)
  yinyang.py            Yin-yang oscillation engine
  shared_pool.py        Shared world-layer pool
  rule_tree.py          Rule match tree (106 rules)
  semantic_anchors.py   Per-unit cell mapping (0-63)
  bagua_core.py         Inference think-chain engine
  bagua_layer.py        Rotating inference grid
  tongzi_experience.py  Child experience pool + personality filter
  lingxi_fusion.py      Full-layer orchestration core
  child_window.py       Tkinter GUI interface
  live_child.py         Terminal interactive mode
  demo_evidence.py      Evidence experiments
  trace.py              Execution trace / audit
```

## License

MIT
