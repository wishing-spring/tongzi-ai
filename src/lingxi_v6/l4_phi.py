# -*- coding: utf-8 -*-
"""Φ场 脉络连接场 — 卦元连接矩阵 · Hebbian · BFS查询 · 零浮点"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from guayuan import MASK28, hamming


class PhiField:
    """卦元连接矩阵: (卦元_a, 卦元_b) → weight [0,28]"""

    def __init__(self, max_weight: int = 28, connect_threshold: int = 12,
                 decay_ticks: int = 50, hebbian_delta: int = 1):
        self.connections: dict[tuple, int] = {}  # (a,b) → weight, a<b
        self.max_weight = max_weight
        self.connect_th = connect_threshold
        self.decay_ticks = decay_ticks
        self.hebbian_delta = hebbian_delta
        self._last_active: dict[tuple, int] = {}  # (a,b) → last_tick_seen
        self.tick = 0

    def _key(self, a: int, b: int) -> tuple:
        return (a, b) if a < b else (b, a)

    # ── Hebbian学习 ──
    def reinforce(self, active_pairs: list[tuple]):
        """共同激活的卦元对 → Hebbian增强"""
        self.tick += 1
        for a, b in active_pairs:
            k = self._key(a, b)
            if k in self.connections:
                w = min(self.max_weight, self.connections[k] + self.hebbian_delta)
                self.connections[k] = w
            elif hamming(a, b) <= self.connect_th:
                self.connections[k] = 1
            self._last_active[k] = self.tick

    def decay(self):
        """连续未激活 → weight-1"""
        remove_keys = []
        for k, w in list(self.connections.items()):
            last = self._last_active.get(k, 0)
            if self.tick - last > self.decay_ticks:
                if w <= 1:
                    remove_keys.append(k)
                else:
                    self.connections[k] = w - 1
        for k in remove_keys:
            del self.connections[k]
            self._last_active.pop(k, None)

    # ── 脉络查询 ──
    def query(self, src: int, max_hops: int = 3) -> list[tuple[int, int]]:
        """BFS: 从src出发，沿weight排序，返回 (卦元, 累积weight) 列表"""
        visited = {src}
        result = []
        frontier = [(src, 0)]  # (卦元, hop)

        for hop in range(max_hops):
            next_frontier = []
            for node, _ in frontier:
                neighbors = self._neighbors_of(node)
                # 按weight降序
                neighbors.sort(key=lambda x: x[1], reverse=True)
                for nb, w in neighbors:
                    if nb not in visited:
                        visited.add(nb)
                        result.append((nb, w))
                        next_frontier.append((nb, hop + 1))
            frontier = next_frontier
        return result

    def query_path(self, src: int, max_hops: int = 3) -> int:
        """查询路径 → XOR累积卦元 (送L3的上下文信号)"""
        result = self.query(src, max_hops)
        ctx = src
        for g, w in result:
            ctx ^= g
        return ctx & MASK28

    def _neighbors_of(self, gua: int) -> list[tuple[int, int]]:
        """找gua的所有邻居及其weight"""
        neighbors = []
        for (a, b), w in self.connections.items():
            if a == gua:
                neighbors.append((b, w))
            elif b == gua:
                neighbors.append((a, w))
        return neighbors

    # ── 统计 ──
    def size(self) -> int:
        return len(self.connections)

    def total_weight(self) -> int:
        return sum(self.connections.values())

    def hardest_connections(self, n: int = 5) -> list:
        """最强连接top N"""
        return sorted(self.connections.items(), key=lambda x: x[1], reverse=True)[:n]


if __name__ == '__main__':
    phi = PhiField(max_weight=28, connect_threshold=12)

    # 模拟L2送来的共同激活对
    active = [(0x1234567, 0x2345678), (0x1234567, 0x3456789),
              (0x2345678, 0x4567890), (0x3456789, 0x5678901)]

    for _ in range(5):
        phi.reinforce(active)
        phi.decay()
        print(f"  tick{phi.tick}: {phi.size()}连接 total_w={phi.total_weight()}")

    ctx = phi.query_path(0x1234567, max_hops=2)
    print(f"\n查询 0x1234567 → ctx=0x{ctx:07X}")
    print(f"最强连接: {phi.hardest_connections(3)}")
