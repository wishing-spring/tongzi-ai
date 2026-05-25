# 审阅邀请草稿

## 1. Dave Ackley — via Mastodon @livcomp@hachyderm.io 或 livingcomputation.org

```
Hi Dave,

I built a tiny AI底层 experiment that shares spirit with your robust-first
computing work. It uses pure F₂ space (GF(2) 28-bit vectors), zero floats,
zero matrices, zero gradients. Input: 20 Chinese characters → XOR/AND
collision engine → emergent attractor structures.

It's not trying to beat LLMs. It's asking: can simple discrete collision
rules in F₂ space produce non-trivial structure?

Running it takes one command: python demo.py (zero dependencies).

https://github.com/wishing-spring/tongzi-ai

I'd be grateful if you could glance at the core engine (src/v3/) and tell
me if this is nonsense or if there's something worth pursuing.

The REVIEWER_GUIDE.md honestly documents known limitations.

Thank you for your time.
```

## 2. Bert Chan (Chakazul) — via Twitter @BertChakovsky 或 GitHub

```
Hi Bert,

Lenia is a huge inspiration. Simple rules → complex life-like patterns.

I'm trying something similar but in pure F₂ space: 20 Chinese characters
encoded as 28-bit vectors, then XOR/AND collision in a discrete pool with
a sliding window (涌動) mechanism. No floating point. No neural nets.

The attractors that emerge are different for different inputs — structure
from nothing but bit collisions.

One command to run: python demo.py (zero deps)
https://github.com/wishing-spring/tongzi-ai

Would love your honest take on whether the F₂ collision engine has
fundamental issues I'm missing. REVIEWER_GUIDE.md is honest about limits.

Thanks for considering.
```

## 3. Ross Gayler (rgayler) — via GitHub

```
Hi Ross,

Your VSA/HDC work with XOR binding in high-dimensional binary spaces is the
closest existing paradigm to what I'm experimenting with.

My project Tongzi uses 28-bit F₂ vectors with XOR/AND collision + a sliding
window mechanism (not just static binding). Small scale (80 seeds → 2,000
active nodes → 400k children over 300 ticks), but emergent attractor
structures appear that differentiate inputs.

Zero floats, zero gradients, zero matrix multiplication. Pure bit ops.

https://github.com/wishing-spring/tongzi-ai
python demo.py runs with zero dependencies.

I'd be grateful for your eyes on the collision engine (src/v3/). Is this
approach fundamentally broken, or is there something worth exploring?

REVIEWER_GUIDE.md honestly documents the architecture limits.

Thank you.
```
