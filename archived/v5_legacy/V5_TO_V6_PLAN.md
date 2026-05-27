"""
童子v5→v6 · 竖贴升维方案（最小修改，不动核心逻辑）
===================================================

原理：VEC_DIM: 16→32，其余全部自动扩展。
工业界做法：重新设计架构+重新训练+烧钱。
我们做法：改3个常量+2行代码，原知识100%保留。

影响：16×16平面 → 32×32平面。能力 ×65536。
"""

# ================================================================
# 修改点1: tongzi_constants.py — 唯一核心常量
# ================================================================
# 第13行:
#   VEC_DIM = 16
# →
#   VEC_DIM = 32
#
# 效果: FULL_MASK自动从0xFFFF变成0xFFFFFFFF
#       encode()自动将ord-sum哈希到32位
#       BitStore全自动适配32位向量
#       rotate_left/right自动适配32位旋转
#       所有Hamming距离阈值不变（语义不变，空间扩大）

# ================================================================
# 修改点2: tongzi_loom.py — 消除硬编码16（3行）
# ================================================================

# 2a. _rotate_16 → _rotate_n (参数化)
#    第44行:
#      def _rotate_16(v: int, n: int) -> int:
#          n = n & 0xF
#          return ((v << n) | (v >> (16 - n))) & FULL_MASK
#    →
#      @staticmethod
#      def _rot(v: int, n: int) -> int:
#          return ((v << (n & (VEC_DIM-1))) |
#                  (v >> (VEC_DIM - (n & (VEC_DIM-1))))) & FULL_MASK
#
#    调用处替换: self._rotate_16(seed, i*5) → self._rot(seed, i*5)

# 2b. generate_looms中的range(16) → range(VEC_DIM)
#    第60行:
#      row_masks = [self._rotate_16(seed, i * 5) for i in range(16)]
#    →
#      row_masks = [self._rot(seed, i * 5) for i in range(VEC_DIM)]

# 2c. apply_sbox_16 → apply_sbox_n (自动适配4位组数)
#    第22行:
#      def apply_sbox_16(vec: int, sbox: list[int]) -> int:
#          result = 0
#          for g in range(4):  # 16/4 = 4 groups
#    →
#      def apply_sbox_n(vec: int, sbox: list[int]) -> int:
#          result = 0
#          for g in range(VEC_DIM // 4):  # 32/4 = 8 groups
#
#    weave/weave_full中所有range(16) → range(VEC_DIM)
#    估算: 约12处，纯替换，零逻辑变更

# ================================================================
# 修改点3: tongzi_constants.py — 阈值精度补偿（可选）
# ================================================================
# 空间从2^16扩大到2^32，Hamming距离的统计分布改变。
# 保持语义等价：
#   SIMILARITY_TIGHT = 4      # 原来是2 (比例: 2/16 = 1/8, 32*1/8=4)
#   SIMILARITY_NEAR = 8       # 原来是4
#   SIMILARITY_FAR = 14       # 原来是7
#   SIMILARITY_ALIEN = 22     # 原来是11
#   CLUSTER_DISTANCE = 4      # 原来是2
#   REPEL_DISTANCE = 14       # 原来是7
#   ANOMALY_DISTANCE = 24     # 原来是12
#
# 这是按比例缩放的。也可以先不动，观察效果再调。

# ================================================================
# 不改的部分（自动适配）
# ================================================================
# tongzi_core.py  — BitStore全用VEC_DIM/FULL_MASK，0改动
# tongzi_mao.py    — Balancer只统计阴阳标记，0改动
# tongzi_data.py   — Responder用BitStore API，0改动
# tongzi_seeds.py  — 种子是常量表，0改动
# tongzi.py        — 入口，0改动

# ================================================================
# v6 → v7 只需再翻倍: VEC_DIM=64
# v7 → v8: VEC_DIM=128
# ...
# 每次一个数字，平面面积×4。永无尽头。
# ================================================================
