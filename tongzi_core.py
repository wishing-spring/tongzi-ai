"""
童子核心 v0.1 · 阶段一：纯位运算底层工具层（整合终版）
====================================================
铁律对齐：壳不过三·永不矩阵·爻必活·纯二元本位
规范对齐：童子_本源法典_v1.0.md / 童子_编码规范_v1.0.md
来源整合：铜须架构 + 豆包接口精简
"""
from typing import Optional

class TongziCore:
    """童子原生AI 核心底层工具层
    锁定16维二元向量，仅提供原生位运算+向量管理+自清代谢
    """
    VEC_DIM = 16
    FULL_MASK = (1 << VEC_DIM) - 1
    MAX_POOL = 200
    SLEEP_TICK = 3

    def __init__(self):
        self.data = {}        # tag -> vec_val
        self.active = {}      # tag -> last_used_tick
        self.tick = 0

    # ========== 静态纯位运算（唯四类） ==========

    @staticmethod
    def xor(a: int, b: int) -> int:
        """异或 a XOR b"""
        return a ^ b

    @staticmethod
    def popcount(v: int) -> int:
        """位统计：1的个数"""
        return v.bit_count()

    @staticmethod
    def hamming(a: int, b: int) -> int:
        """汉明距离：不同位的数量"""
        return TongziCore.popcount(a ^ b)

    @staticmethod
    def shift_left(v: int, step: int = 1) -> int:
        """循环左移，保持16位"""
        return ((v << step) | (v >> (TongziCore.VEC_DIM - step))) & TongziCore.FULL_MASK

    @staticmethod
    def shift_right(v: int, step: int = 1) -> int:
        """循环右移，保持16位"""
        return ((v >> step) | (v << (TongziCore.VEC_DIM - step))) & TongziCore.FULL_MASK

    # ========== 文本编码 ==========

    def encode_text(self, text: str) -> int:
        """文本→16位向量（固定规则，后期可用标注数据替换）"""
        seed = sum(ord(c) for c in text)
        return seed & self.FULL_MASK

    # ========== 向量仓储 ==========

    def add(self, tag: str, text: str):
        """存入向量并初始化活跃度"""
        if len(self.data) >= self.MAX_POOL:
            self.clean_dormant()
        vec = self.encode_text(text)
        self.data[tag] = vec
        self.active[tag] = self.tick

    def get(self, tag: str) -> Optional[int]:
        """读取向量，读取即刷新活跃度"""
        if tag in self.data:
            self.active[tag] = self.tick
            return self.data[tag]
        return None

    @property
    def size(self) -> int:
        return len(self.data)

    @property
    def active_count(self) -> int:
        return sum(1 for t in self.active if self.tick - self.active[t] <= self.SLEEP_TICK)

    def find_similar(self, target_vec: int, threshold: int = 4) -> list[str]:
        """按汉明距离查找相似向量标签列表"""
        res = []
        for t, v in self.data.items():
            if self.hamming(target_vec, v) <= threshold:
                self.active[t] = self.tick  # 命中刷新活跃度
                res.append(t)
        return res

    def find_foreign(self, target_vec: int, threshold: int = 7) -> list[str]:
        """查找汉明距离≥阈值的异类向量（阴锚斥离用）"""
        res = []
        for t, v in self.data.items():
            if self.hamming(target_vec, v) >= threshold:
                self.active[t] = self.tick
                res.append(t)
        return res

    # ========== 时序代谢·文火自清 ==========

    def time_tick(self):
        """全局时序步进，模拟丹体温养"""
        self.tick += 1

    def clean_dormant(self):
        """清理长期低活跃度休眠向量，代谢排浊"""
        del_list = [t for t, last in self.active.items()
                    if self.tick - last > self.SLEEP_TICK]
        for t in del_list:
            self.data.pop(t, None)
            self.active.pop(t, None)

    def status(self) -> dict:
        """仓储状态摘要"""
        return {
            'total': self.size,
            'active': self.active_count,
            'tick': self.tick,
        }

# ===================== 三问标准自检 =====================

def self_test():
    print("=" * 50)
    print("童子核心 v0.1 · 三问自检")
    print("=" * 50)
    core = TongziCore()

    # 一问：纯二元本位运算校验
    a = 0b1100110011001100
    b = 0b1010101010101010
    assert core.xor(a, b) == 0b0110011001100110, "异或运算校验失败"
    print("[OK] XOR 纯位运算通过")

    assert core.hamming(0b11110000, 0b00001111) == 8, "汉明距离判定错误"
    assert core.hamming(0b11111111, 0b11111111) == 0, "同向量距离不为0"
    print("[OK] 汉明距离计算通过")

    assert core.popcount(0b10101010) == 4, "位计数统计错误"
    print("[OK] Popcount 位统计通过")

    # 二问：文本编码规则可复现校验
    v1 = core.encode_text("你好")
    v2 = core.encode_text("你好")
    assert v1 == v2, "相同文本编码不一致"
    print(f"[OK] 编码可复现: '你好' -> {v1:016b}")

    v3 = core.encode_text("你好吗？")
    v4 = core.encode_text("太好了！")
    assert v3 != v4, "不同文本出现编码碰撞"
    dist = core.hamming(v3, v4)
    print(f"[OK] 异文本区分正常，汉明距离: {dist}")

    # 三问：仓储入库+检索+代谢基础正常
    core.add("s1", "今天天气真好")
    core.add("s2", "我好难过")
    core.add("s3", "你是谁")
    assert core.size == 3, "向量入库数量异常"
    print(f"[OK] 向量入库正常，当前存量: {core.size}")

    target = core.encode_text("今天天气真好")
    similar_list = core.find_similar(target)
    print(f"[OK] 相似检索完成，匹配条目数: {len(similar_list)}")

    # 代谢测试
    core.time_tick()
    core.clean_dormant()
    assert core.size == 3, "新入库向量不应被清理"
    print("[OK] 代谢自清正常，新向量未被误清")

    # 休眠清理测试
    for _ in range(core.SLEEP_TICK + 2):
        core.time_tick()
    core.clean_dormant()
    print(f"[OK] 休眠清理完成，存量: {core.size} (活跃: {core.active_count})")

    print("=" * 50)
    print("三问自检全部通过。阶段一底层工具层就绪。")
    print("=" * 50)
    return True


if __name__ == "__main__":
    self_test()
