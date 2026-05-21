# Boundary Report — Tongzi v0.5

Run `python src/boundary_test.py` to reproduce.
Read-only. No state mutation.

## 1. Emotion differentiation: 1/6

| Input | Response |
|:------|:---------|
| hello | …… |
| joy | …… |
| delight | …… |
| anger | …… |
| sorrow | …… |
| grief | …… |

**Verdict**: No emotion differentiation. All 6 inputs produce the same output.

## 2. Polarity: none

| Polarity | Inputs | Responses |
|:---------|:-------|:----------|
| Yang | sun, light, day | …… |
| Yin | night, abyss, winter | …… |

**Verdict**: Yin-yang flags are all zero at cold start. No polarity signal.

## 3. Capacity: 200-entry limit

`MAX_ENTRIES = 200`. Purge triggers in `put()` at capacity.

## 4. Encoding: ord-sum

`sum(ord(c)) & 0xFFFF`. No semantic clustering. "hello" and "world" may or may not be near each other — pure accident of codepoint sums.

## 5. Output: 9 hardcoded strings

`心生暖意。` `心绪沉郁。` `安好。` `知晓。` `暖意生。` `沉郁在。` `嗯。` `好。` `……`

Selection is a hand-written if-else tree keyed on:
- Frequency tier (0/1/2)
- Cluster presence (yang/yin aura names)
- Balancer gap (yang-yin count)

## 6. Anomaly: no crash

Symbols, numbers, empty strings, whitespace — all handled. No error output.

## 7. Clusters: ~15 at boot

60 seeds + 15 ingest = ~75 entries, ~15 distinct cluster labels.

## Summary

| Dimension | Status |
|:----------|:-------|
| Stability | No crash |
| Encoding | ord-sum, no semantics |
| Output diversity | 9 strings |
| Emotion | None |
| Polarity | Cold-start zeros |
| Capacity | 200 hard cap |
