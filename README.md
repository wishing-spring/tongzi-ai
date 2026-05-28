# Tongzi (童子) v8.3

**A Zero-Gradient Symbolic Reasoning System**

---

## What This Is

Tongzi is a symbolic reduction and rule-based reasoning system operating on F₂ (binary field) vectors. Its technical classification: a Discrete Symbolic Reducer — a rule-driven inference system, not a statistical learning or neural network system.

All operations are limited to XOR, Hamming distance, and bit_count. No floating-point arithmetic, matrix multiplication, gradient computation, word embeddings, or external knowledge bases are used. ~172 KB of code, 13 core modules, Python 3.8+ standard library only. Zero additional dependencies.

---

## Core Constraints

| Constraint | Description |
|:--|:--|
| Zero floats | All computation in integer domain |
| Zero matrices | No matrix multiplication |
| Zero gradients | No backpropagation or parameter optimization |
| Zero embeddings | No pretrained word vectors |
| Zero dependencies | Python 3.8 standard library only |

---

## Architecture

Seven layers, bottom to top:

### 1. Vector Layer (guayuan.py)

28-bit binary vectors form the system's fundamental data structure. All information — input characters, rules, vector clusters, memory — is represented and operated on as 28-bit vectors.

Character-to-vector mapping uses radical Gray encoding: Unicode radical ordering builds Gray codes so that characters sharing radicals are close in Hamming space. Example: characters under the "水" (water) radical (江, 河, 海, 湖) have an average pairwise Hamming distance of ~0.76.

Core operations: XOR, Hamming distance, bit_count.

### 2. Oscillation Scheduler (yinyang.py)

Fixed-interval oscillation signal drives periodic updates to the world state layer. Each tick triggers vector collisions, energy flow, and state transitions.

### 3. World State Layer (shared_pool.py)

Shared vector pool. Current scale: 195 active vectors, 13 vector clusters (grouped by radical and co-occurrence), 414 co-occurrence edges (character-to-character associations built automatically from dialogue).

### 4. Rule Layer (rule_tree.py)

106 rules across 16 categories. Rule matching uses direct substring matching: if an input character appears in a rule's refs list, the rule fires.

Self-growth support: when a collision pattern recurs ≥3 times, the system automatically crystallizes it into a new rule under the HARVESTED category.

### 5. Inference Layer (bagua_core.py)

64-cell inference grid. After rule matching, the system performs shortest-path traversal through the cell network, producing a cell-path sequence as the inference chain.

### 6. Cognitive Boundary Layer (tongzi_experience.py)

Cognitive boundary filter. Defines the cognitive scope of a 10-year-old child: 7 allowed domains (play, nature, animals, drawing, food, family, curiosity) and 4 blocked domains (violence, social dismissiveness, negative emotions, adult content — recognized but not affirmatively answered).

Positioned mid-chain: full-perspective inference (64-cell unconstrained traversal) → cognitive boundary filter (retains only what a 10-year-old can comprehend) → constrained-perspective inference (further traversal from the filtered scope).

### 7. Output Layer (child_window.py / live_child.py)

Converts cell-path and inference chain data into natural language output. Two modes: Tkinter GUI window and terminal interactive. Output voice is uniformly that of a 10-year-old child.

---

## Quick Start

```bash
pip install .                                         # zero additional dependencies
python -c "import lingxi; lingxi.demo()"              # run 3 evidence experiments
python -c "import lingxi; lingxi.start()"             # interactive session
```

---

## File Layout

```
lingxi/
  __init__.py           Entry: start(), demo()
  guayuan.py            28-bit binary vector core
  yinyang.py            Oscillation scheduler
  shared_pool.py        World state shared pool
  rule_tree.py          Rule tree (106 rules)
  semantic_anchors.py   64-cell mapping
  bagua_core.py         Inference grid engine
  bagua_layer.py        Rotating inference grid
  tongzi_experience.py  Cognitive boundary filter & experience pool
  lingxi_fusion.py      Full-layer orchestration
  child_window.py       Tkinter GUI
  live_child.py         Terminal interactive
  demo_evidence.py      Evidence experiments
  trace.py              Execution trace / audit
```

---

## Three Evidence Experiments

**Experiment 1: Refusal.** Blocked-domain input → ANNIHILATE, no affirmative response.

**Experiment 2: Separation.** Same-radical, different-meaning characters → distinct rule paths.

**Experiment 3: Self-Growth.** Repeatedly submit similar input → collision crystallization, new rule auto-generated.

---

## Known Limitations

**Substring matching does not imply semantic understanding.** Rule firing is based on keyword string matching. "打" hits a rule because the character is in its refs list — the system does not distinguish "打水" (fetch water) from "打架" (fight).

**Output layer is template-bridged.** The inference chain produces cell-path data, which is converted to natural language through hand-written templates. Output is not directly generated from vector operations.

**Single-character matching lacks context differentiation.** "好" in "你好" (hello), "好累" (so tired), and "好天气" (nice weather) triggers the same rule. Multi-character context is not analyzed.

**Experimental scale.** 106 rules, 195 vectors, 13 clusters — insufficient to cover broad semantic scenarios.

**No standard NLP benchmarks.** The system does not use probability distributions; BLEU, ROUGE, and similar metrics are not applicable.

---

## Technical Characteristics

- Fully auditable: every step (character → rule → cell → energy → output) is traceable
- Autonomous evolution engine: world state evolves continuously during idle, not dependent on user input
- Rule self-growth: collision patterns recurring ≥3 times auto-crystallize into new rules
- Ctrl+C auto-saves current state
- Radical Gray encoding provides Unicode-structure-based initial bit-space distribution for characters

---

## Positioning

Not a: large language model, neural network, probabilistic generative model, word embedding system.

Technically adjacent to: discrete dynamical systems, symbolic reduction over F₂, artificial life simulation, auditable inference engines.

---

## License

MIT
