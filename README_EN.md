# TongLing v6.0 — F₂ GuaYuan Discrete Dynamical System

A discrete dynamical system operating entirely in F₂ (GF(2)). No floating-point, no matrices, no gradients, no word embeddings. 28-bit GuaYuan serve as the universal atomic carrier, with five-layer dynamics and a three-realm governance layer implemented through XOR collisions, Hamming-distance transitions, and bit-count operations.

**Input → Tongzi F₂ Collision → Attractor → Lingxi Five Layers → 657-word F₂ Native Output**

## Architecture

```
Input text → [Tongzi F₂ Pool] XOR collision · Four eco-pools · Chain-linked encoding
                 ↓ attractor (28-bit GuaYuan)
          [Lingxi Five Layers]
          L1 Yin-Yang   (128-gua mutual exchange · coherence)
          L2 World Pool (1024 gua · three-state · dreaming · diffusion)
          Φ-field        (Hebbian connections · BFS · decay)
          L3 Bagua Ring  (64 reference codes · Hamming transitions · Lightning chain)
          L5 DingXin     (5-value gating · dual persona)
          L5 YongJiu     (free gua probe · three-talent detection · dual-well · field quench)
                 ↓
          [Container] body · ghost · ctx (three-gua packet)
                 ↓
          [Word World] 657-word F₂ hash · XOR chain-jump → output
                 
          [Three-Realm Governance] 7 Heaven officers · 3 Underworld officers
          JadeEmperor/Overseer  QueenMother/Vitality  Laojun/Observer
          Thunder/Emergency  Ziwei/Trajectory  Taisui/Rhythm  Wealth/Dispatch
          Yama/Verdict  Wuchang/Reclaim  Mengpo/Cleanup
```

## Quick Start

```bash
cd src/lingxi_v6
python demo.py      # Six-step full-pipeline demo + persistence
python chat.py       # Interactive dialogue (type '天庭' for governance view)
```

**Requires**: Python 3.8+ (standard library only, zero external dependencies)

## Core Properties

| Property | Implementation |
|:--|:--|
| Algebraic domain | F₂ (GF(2)), 28-bit closed space |
| Carrier | 28-bit GuaYuan — Tongzi sees bit collisions, Lingxi sees trigram affinity |
| Encoding | Chain-linked hashing (连环咬合) |
| Collision | XOR bitwise, mask dynamics |
| Distance | Hamming distance (bit_count) |
| Learning | Hebbian connection reinforcement (Φ-field) |
| Memory | Long-term (cumulative XOR) + Short-term (last 5 rounds) + Logical skeleton (8 relations) |
| Governance | Three-tier co-governance · Seasonal cycles · Cooldown anti-oscillation · Non-action anchor |
| Numerics | Zero float · Zero matrix · Zero gradient · Zero embedding · Zero external knowledge |

## Key Metrics

- 1500-tick continuous run, no collapse
- Eco-pool solidification rate: 100% (hits ≥ 3)
- YongJiu trigger rate: ~33%, quench rate: ~11%
- Φ-field connections: 39 → 229 → 164 (growth then stabilization)
- Seasonal cycle: Spring→Summer→Autumn→Winter, every 250 ticks

## Known Limitations

1. **Non-semantic output** — F₂-native word-chain output produces character sequences (e.g., "wall·river·north·dry·descent·origin"), not natural language. This is a physical constraint of the F₂ domain: XOR + Hamming cannot generate new semantic compositions.

2. **No incremental learning** — Φ-field Hebbian mechanism only reinforces co-occurrence connections. Structural complexity growth rate approaches zero beyond ~1000 ticks.

3. **Empirical parameters** — All thresholds (L_threshold=0.35, harvest_cycle=100, season=250) are empirically tuned, not theoretically derived.

4. **Limited word space** — 657-word F₂ hash space. XOR chain-jumps on low-cardinality vocabularies risk attractor collapse.

5. **Non-general system** — Currently a closed-domain dynamical prototype with no external data or API integration. Cannot substitute for LLMs or serve production tasks.

## Files

```
src/lingxi_v6/
├── guayuan.py              # GuaYuan infrastructure (28-bit · XOR · Hamming · hash)
├── tongzi_f2.py            # Tongzi F₂ closed collision pool (surge · 4 eco-pools)
├── l1_yinyang.py           # L1 Yin-Yang pair-pool (exchange · coherence)
├── l2_world.py             # L2 World lexicon pool (3-state · dreaming · diffusion)
├── l3_bagua.py             # L3 Bagua ring (64 ref · Hamming transitions · Lightning)
├── l4_phi.py               # Φ-field plexus (Hebbian · BFS · decay)
├── l5_dingxin_yongjiu.py   # DingXin (5-value gating) + YongJiu (free probe)
├── lingxi_fusion.py        # Container · full-layer fusion · persistence
├── word_world.py           # F₂ native word world (657-word hash · XOR chain-jump)
├── tian_tian.py            # Three-Realm governance (10 officers)
├── demo.py                 # Full-pipeline demo (6 steps · save/load)
├── chat.py                 # Interactive dialogue
└── __init__.py
```

## License

MIT License
