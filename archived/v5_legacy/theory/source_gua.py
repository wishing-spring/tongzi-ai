# -*- coding: utf-8 -*-
"""源卦 — 零爻空生成器 · 二进展开 · 标识符前缀"""


class Yao:
    __slots__ = ('bit',)
    def __init__(self, b: int): self.bit = b & 1
    def __repr__(self): return '⚊' if self.bit else '⚋'


class Gua:
    __slots__ = ('bits',)
    def __init__(self, bits):
        self.bits = tuple(b & 1 for b in bits)
    def __repr__(self):
        return ''.join('⚊' if b else '⚋' for b in self.bits)
    def __hash__(self): return hash(self.bits)
    def __eq__(self, o): return self.bits == o.bits
    def __len__(self): return len(self.bits)
    def as_int(self):
        v = 0
        for b in self.bits: v = (v << 1) | b
        return v


class SourceGua:
    """源卦 — 零爻生成器。id_bits 长度的唯一标识符 + 二进展开。"""

    def __init__(self, id_bits: int = 4, source_id: int = 0):
        self.id_bits = id_bits
        self.id = source_id & ((1 << id_bits) - 1)
        self._pools = {}       # layer -> list[Gua]
        self._consumed = {}    # layer -> set of consumed gua bits
        self._id_prefix = tuple((self.id >> (id_bits - 1 - i)) & 1
                                for i in range(id_bits))

    def generate_layer(self, k: int):
        """生成第k层（k爻展开体 + id_bits 标识符 = 共 id_bits+k 爻）"""
        if k in self._pools:
            return
        total = 1 << k
        pool = []
        for i in range(total):
            expansion = tuple((i >> (k - 1 - j)) & 1 for j in range(k))
            full = self._id_prefix + expansion
            pool.append(Gua(full))
        self._pools[k] = pool

    def draw(self, k: int) -> Gua:
        """取出一卦。自动生成相同替身补回。"""
        if k not in self._pools:
            self.generate_layer(k)
        g = self._pools[k].pop(0)
        twin = Gua(g.bits)
        self._pools[k].append(twin)
        return g

    def pool_size(self, k: int) -> int:
        return len(self._pools.get(k, []))

    def expand(self, gua: Gua) -> tuple:
        """给一卦加一爻，产出两个子卦（阴/阳）。"""
        return Gua(gua.bits + (0,)), Gua(gua.bits + (1,))

    def shrink(self, gua: Gua) -> Gua:
        """去掉最后一爻。"""
        if len(gua.bits) <= self.id_bits:
            return gua
        return Gua(gua.bits[:-1])

    def all_layers(self) -> dict:
        return {k: len(v) for k, v in self._pools.items()}


# ── 实验 ──
if __name__ == '__main__':
    print("=== 单源卦展开 ===")
    s = SourceGua(id_bits=4, source_id=0)
    for L in [1, 2, 3]:
        s.generate_layer(L)
        print(f"层{L} ({s.pool_size(L)}卦):")
        for i in range(min(4, s.pool_size(L))):
            print(f"  {s._pools[L][i]}")
        if s.pool_size(L) > 4:
            print(f"  ... 共{s.pool_size(L)}卦")

    print("\n=== 消耗补充 ===")
    for _ in range(3):
        g = s.draw(2)
        print(f"取 {g}  池剩余 {s.pool_size(2)}")

    print("\n=== 两源卦碰撞 ===")
    s1 = SourceGua(4, 0)
    s2 = SourceGua(4, 3)
    g1 = s1.draw(3)
    g2 = s2.draw(3)
    print(f"源卦0: {g1}")
    print(f"源卦3: {g2}")
    print(f"XOR  : {''.join('⚊' if (g1.bits[i] ^ g2.bits[i]) else '⚋' for i in range(len(g1.bits)))}")
    xored = tuple(g1.bits[i] ^ g2.bits[i] for i in range(len(g1.bits)))
    print(f"非零: {any(xored)}")

    print("\n=== 5源卦 各产10层 ===")
    sources = [SourceGua(4, i) for i in range(5)]
    for s in sources:
        for L in range(1, 11):
            s.generate_layer(L)
    print(f"\n=== 爻增减 ===")
    s = SourceGua(4, 0)
    g = s.draw(2)
    print(f"基卦(层2): {g}")
    c0, c1 = s.expand(g)
    print(f"加一爻阴:  {c0}")
    print(f"加一爻阳:  {c1}")
    back = s.shrink(c1)
    print(f"减一爻:    {back}  (还原: {back.bits == g.bits})")

    # 连续扩张
    print(f"\n=== 连续扩张: 层1 → 层5 ===")
    s = SourceGua(4, 5)
    g = s.draw(1)
    for L in range(1, 6):
        print(f"  层{L}: {g}")
        if L < 5:
            _, g = s.expand(g)  # 取阳子继续
    print(f"  终点层5: {g}")
