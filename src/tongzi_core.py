"""
童子核心 v0.5 · 出厂版：位运算底层工具层
========================================
铁律对齐：壳不过三·永不矩阵·爻必活·纯二元本位
常量对齐：tongzi_constants.py（已锁定）
"""
from tongzi_constants import *
from typing import Optional
import json, os

class TongziCore:
    """童子原生AI 核心底层工具层"""

    def __init__(self):
        self.data = {}        # tag -> vec_val
        self.active = {}      # tag -> last_used_tick
        self.tick = 0
        self.hits = {}        # tag -> 累计命中次数
        self.potency = {}     # tag -> 势能层级(0浅蓄/1中凝/2沉敛)

    # ========== 静态纯位运算 ==========

    @staticmethod
    def xor(a: int, b: int) -> int:
        return a ^ b

    @staticmethod
    def popcount(v: int) -> int:
        return v.bit_count()

    @staticmethod
    def hamming(a: int, b: int) -> int:
        return TongziCore.popcount(a ^ b)

    @staticmethod
    def shift_left(v: int, step: int = 1) -> int:
        return ((v << step) | (v >> (VEC_DIM - step))) & FULL_MASK

    @staticmethod
    def shift_right(v: int, step: int = 1) -> int:
        return ((v >> step) | (v << (VEC_DIM - step))) & FULL_MASK

    # ========== 文本编码 ==========

    def encode_text(self, text: str) -> int:
        seed = sum(ord(c) for c in text)
        return seed & FULL_MASK

    # ========== 向量仓储 ==========

    def add(self, tag: str, text: str):
        """存入向量"""
        if len(self.data) >= MAX_POOL:
            self.clean_dormant()
        vec = self.encode_text(text)
        self.data[tag] = vec
        self.active[tag] = self.tick
        self.hits[tag] = 0
        self.potency[tag] = 0

    def get(self, tag: str) -> Optional[int]:
        """读取向量，刷新活跃度并更新势能"""
        if tag in self.data:
            self.active[tag] = self.tick
            self.hits[tag] = self.hits.get(tag, 0) + 1
            # 势能升级
            h = self.hits[tag]
            p = self.potency.get(tag, 0)
            if p < 1 and h >= POTENCY_SHALLOW:
                self.potency[tag] = 1
            elif p < 2 and h >= POTENCY_MEDIUM:
                self.potency[tag] = 2
            return self.data[tag]
        return None

    @property
    def size(self) -> int:
        return len(self.data)

    @property
    def active_count(self) -> int:
        return sum(1 for t in self.active if self.tick - self.active[t] <= DORMANT_TICK)

    def find_similar(self, target_vec: int, threshold: int = HAMMING_NEAR) -> list[str]:
        """按汉明距离查找相似向量"""
        res = []
        for t, v in self.data.items():
            if self.hamming(target_vec, v) <= threshold:
                self.active[t] = self.tick
                self.hits[t] = self.hits.get(t, 0) + 1
                res.append(t)
        return res

    def find_aura(self, target_vec: int) -> list[str]:
        """找同气场向量（dH≤AURA_HOMOGENIZE_DIST）"""
        return self.find_similar(target_vec, threshold=AURA_HOMOGENIZE_DIST)

    def find_foreign(self, target_vec: int, threshold: int = HAMMING_FOREIGN) -> list[str]:
        """查找异类向量"""
        res = []
        for t, v in self.data.items():
            if self.hamming(target_vec, v) >= threshold:
                self.active[t] = self.tick
                res.append(t)
        return res

    def is_silent(self, vec: int) -> bool:
        """判断向量是否异常（距离所有已知向量都太远→静默收纳）"""
        if not self.data:
            return False
        min_d = min(self.hamming(vec, v) for v in self.data.values())
        return min_d >= SILENT_DIST_THRESHOLD

    # ========== 时序代谢 ==========

    def time_tick(self):
        self.tick += 1

    def clean_dormant(self):
        """清理长期低活跃度休眠向量"""
        del_list = [t for t, last in self.active.items()
                    if self.tick - last > PURGE_CYCLE_TICK]
        for t in del_list:
            self.data.pop(t, None)
            self.active.pop(t, None)
            self.potency.pop(t, None)
            self.hits.pop(t, None)

    # ========== 闲置归元（自保机制） ==========

    def return_to_source(self):
        """闲置归元：将低活跃低势能向量归元释放。
        不删除，而是将其从活跃仓储移入静藏区（标记为归元态）。
        归元后的向量不再参与聚类检索，但仍保留在data中以备后续唤醒。
        """
        归元数 = 0
        for t in list(self.data.keys()):
            idle = self.tick - self.active.get(t, 0)
            pot = self.potency.get(t, 0)
            # 闲置超过半周期 + 浅蓄势能 → 归元
            if idle > PURGE_CYCLE_TICK + HALF_CYCLE and pot == 0:
                self.active[t] = self.tick - PURGE_CYCLE_TICK * 2  # 标记为极旧
                self.potency[t] = -1  # -1 = 归元态
                归元数 += 1
        return 归元数

    def is_returned(self, tag: str) -> bool:
        return self.potency.get(tag, 0) == -1

    # ========== 淤积分流 ==========

    def decongest(self):
        """仓储超过淤积阈值→自动分流清理"""
        if self.size < CONGESTION_THRESHOLD:
            return 0
        # 先归元
        n = self.return_to_source()
        # 再清理
        self.clean_dormant()
        return n

    def status(self) -> dict:
        return {
            'total': self.size,
            'active': self.active_count,
            'tick': self.tick,
            'returned': sum(1 for p in self.potency.values() if p == -1),
            'deep': sum(1 for p in self.potency.values() if p >= 2),
        }

    # ========== 持久化 ==========

    def save_state(self, filepath: str) -> None:
        """保存核心状态到JSON"""
        state = {
            'data': self.data,
            'active': self.active,
            'hits': self.hits,
            'potency': self.potency,
            'tick': self.tick,
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def load_state(self, filepath: str) -> bool:
        """从JSON恢复核心状态。失败返回False，首次启动正常。"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                state = json.load(f)
            self.data = {k: int(v) for k, v in state['data'].items()}
            self.active = {k: int(v) for k, v in state['active'].items()}
            self.hits = {k: int(v) for k, v in state['hits'].items()}
            self.potency = {k: int(v) for k, v in state['potency'].items()}
            self.tick = int(state['tick'])
            return True
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            return False
