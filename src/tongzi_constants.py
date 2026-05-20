"""
童子 v0.5 · global constants (locked)
======================================
Source: Euler identity → discrete mapping
  e^(iπ)+1=0  → primary rhythm
  φ=(1+√5)/2  → ratio rules

ALL CONSTANTS LOCKED. Do not modify.
"""
# ============================================================
# 1. Vector space (fixed)
# ============================================================
VEC_DIM = 16                     # 16-bit F₂ space
FULL_MASK = (1 << VEC_DIM) - 1   # 0xFFFF

# ============================================================
# 2. Rhythm (discretized from e, π, φ)
# ============================================================
CYCLE_LENGTH = 7          # main cycle (ticks)
HALF_CYCLE_LENGTH = 3     # half-cycle
QUARTER_CYCLE_LENGTH = 2  # quarter-cycle

GROWTH_INTERVAL = 3       # growth pulse every N ticks
DECAY_INTERVAL = 5        # decay check every N ticks

# ============================================================
# 3. Balance window (derived from φ ≈ 1.618)
# ============================================================
BALANCE_THRESHOLD = 2     # max yang-yin gap
BALANCE_WARN = 1          # warning gap

# ============================================================
# 4. Similarity thresholds (Hamming distance in F₂^16)
# ============================================================
SIMILARITY_TIGHT = 2      # dH ≤ 2: same cluster
SIMILARITY_NEAR = 4       # dH ≤ 4: neighbor
SIMILARITY_FAR = 7        # dH ≥ 7: distant
SIMILARITY_ALIEN = 11     # dH ≥ 11: alien

# ============================================================
# 5. Frequency tiers (hit count thresholds)
# ============================================================
FREQ_TIER1 = 3            # ≥3 hits: tier 1
FREQ_TIER2 = 10           # ≥10 hits: tier 2
FREQ_TIER3 = 30           # ≥30 hits: tier 3

# ============================================================
# 6. Clustering
# ============================================================
CLUSTER_DISTANCE = 2      # dH ≤ N: same cluster
REPEL_DISTANCE = 7        # dH ≥ N: repel

# ============================================================
# 7. Lifecycle (entry aging)
# ============================================================
STALE_AFTER = 2           # unused for N ticks → stale
REST_TICKS = 5            # rest cycle length
PURGE_AFTER = 8           # unused for N ticks → purge

# ============================================================
# 8. Pool capacity
# ============================================================
MAX_ENTRIES = 200         # max vector pool size
REST_AT = 100             # trigger rest at N entries
MAX_BATCH = 10            # max entries per batch

# ============================================================
# 9. Self-protection
# ============================================================
AUTO_BALANCE_AT = 3       # force balance at gap ≥ N
ANOMALY_DISTANCE = 12     # dH ≥ N → silent store
ANOMALY_RESPONSE = "……"   # output for anomaly
COMPACT_AT = 150          # compact at N entries

# ============================================================
# 10. Seed vectors
# ============================================================
MIN_SEEDS = 60            # minimum seed count
SEED_CATEGORIES = [
    "天地", "动静", "虚实", "明暗",
    "冷暖", "刚柔", "曲直", "离合",
    "喜怒", "哀乐", "远近", "昼夜",
]

# ============================================================
# 11. Forbidden operations (iron laws)
# ============================================================
FORBIDDEN_OPS = [
    "矩阵乘法", "梯度下降", "浮点运算",
    "词嵌入", "注意力机制", "自回归解码",
]
FORBIDDEN_DEPS = [
    "第三方分词", "语义接口", "预训练权重",
    "对话框架", "话术模板", "语法引擎",
]

# ============================================================
# Self-check
# ============================================================
def verify_constants():
    assert 0 < VEC_DIM <= 32
    assert SIMILARITY_TIGHT < SIMILARITY_NEAR < SIMILARITY_FAR < SIMILARITY_ALIEN <= VEC_DIM
    assert STALE_AFTER < REST_TICKS < PURGE_AFTER
    assert BALANCE_THRESHOLD < 6
    assert MAX_ENTRIES > 0 and REST_AT > 0
    return True

if __name__ == "__main__":
    verify_constants()
    print("All constants verified. Locked.")
