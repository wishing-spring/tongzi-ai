# -*- coding: utf-8 -*-
"""
池子 · 卦元生态空间  v1.6

v1.3 精神回归:
  - 卦元碰撞中自身变化
  - 咬合生子 (XOR + AND 双链)
  - 子卦可融回池中
  - 环 (orbit 旋转)
  - 势 Ψ = log₂(1 + 碰撞次数)

无 tick, 无 decay, 无随机, 无时钟。
纯碰撞驱动 — 碰了才变, 不碰不动。
"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi_kernel import Gua, form, _fit
from tools.axioms import hamming


class Pool:
    """卦元生态池。

    卦元在这里存活、碰撞、变化、生子。

    三条核心规则:
      1. 碰撞: 两卦 XOR → 双方都变
      2. 咬合生子: 凸凹互补 → XOR子 + AND子
      3. 环:   卦元绕池旋转, 逐位演化

    没有时钟, 没有衰变。
    """

    def __init__(self, name: str = ""):
        self.name = name
        self._guas: list[Gua] = []
        self._children: list[Gua] = []
        self._hits: dict[int, int] = {}  # id(gua) → 碰撞次数

    # ============================================================
    # 进出
    # ============================================================

    def drop(self, g: Gua):
        """投入一个卦元。"""
        self._guas.append(g)

    def drop_many(self, guas: list[Gua]):
        """批量投入。"""
        self._guas.extend(guas)

    def remove(self, g: Gua):
        """移除卦元。"""
        self._guas.remove(g)

    # ============================================================
    # 势  Ψ = log₂(1 + 碰撞次数)
    # ============================================================

    def potential(self, g: Gua) -> int:
        """Ψ: 卦元的活跃度。碰撞越多, 势越大。"""
        c = self._hits.get(id(g), 0)
        if c == 0:
            return 0
        return c.bit_length()  # floor(log₂(1+c))

    # ============================================================
    # 碰撞 — 卦元自身变化
    # ============================================================

    def collide_pair(self, a: Gua, b: Gua):
        """两卦碰撞: 互换低位, 双方都变。

        不再 ID 管理 — 卦元就是卦元。
        碰撞计数 +1。
        """
        # 互换低8位
        a_lo = a.value & 0xFF
        b_lo = b.value & 0xFF
        a.value = (a.value & 0xFF00) | b_lo
        b.value = (b.value & 0xFF00) | a_lo

        # 碰撞计数
        self._hits[id(a)] = self._hits.get(id(a), 0) + 1
        self._hits[id(b)] = self._hits.get(id(b), 0) + 1

    # ============================================================
    # 咬合生子 — 凸凹互补
    # ============================================================

    def try_mate(self, a: Gua, b: Gua) -> list[Gua] | None:
        """尝试咬合生子。

        若 a 凸 ∧ b 凹 (或反过来):
          产子: XOR 子 (差异链) + AND 子 (共识沉淀)

        返回子卦列表, 不咬合返回 None。
        """
        if _fit(a, b) or _fit(b, a):
            xor_val = a.value ^ b.value
            and_val = a.value & b.value

            children = []
            if xor_val:
                children.append(Gua(xor_val))
            if and_val and and_val != xor_val:
                children.append(Gua(and_val))
            return children
        return None

    # ============================================================
    # 池内演化 — 全对全碰撞 + 生子
    # ============================================================

    def evolve(self, max_guas: int = 512):
        """一次池内演化:

        1. 所有卦两两碰撞 (O(N²))
        2. 咬合对产子
        3. 子卦入池
        4. 池太大则裁剪 (势最低的先移除)
        """
        n = len(self._guas)
        if n < 2:
            return {'碰撞': 0, '生子': 0, '池大小': n}

        new_children = []
        collide_count = 0
        mate_count = 0

        for i in range(n):
            for j in range(i + 1, n):
                a, b = self._guas[i], self._guas[j]

                self.collide_pair(a, b)
                collide_count += 1

                kids = self.try_mate(a, b)
                if kids:
                    new_children.extend(kids)
                    mate_count += len(kids)

        self._guas.extend(new_children)

        # 裁剪: 超过上限, 移除低势卦
        if len(self._guas) > max_guas:
            ranked = [(self.potential(g), g) for g in self._guas]
            ranked.sort(key=lambda x: x[0])
            self._guas = [g for _, g in ranked[-max_guas:]]

        return {'碰撞': collide_count, '生子': mate_count, '池大小': len(self._guas)}

    # ============================================================
    # 子卦融合 — 子卦 XOR 回父卦
    # ============================================================

    def fuse_children(self):
        """子卦融合: 每个子卦 XOR 进最近父卦。

        子卦不被删除, 但它的值融入了父卦。
        融合后子卦不变 (可多父)。
        """
        # 简化: 所有新子卦 XOR 进池中随机老卦
        if not self._children:
            return

        for child in self._children:
            target = self._guas[child.value % len(self._guas)]
            target.value ^= child.value
            self._hits[id(target)] = self._hits.get(id(target), 0) + 1

    # ============================================================
    # 环 — 卦元绕池旋转
    # ============================================================

    def ring(self, g: Gua, steps: int = 8) -> list[Gua]:
        """卦元绕池旋转: 左旋 → 跟池中卦 XOR → 演化。

        每步:
          1. 左旋 1 位
          2. 跟池中指定卦 XOR
        """
        ring_guas = []
        cur = g.value

        for step in range(steps):
            # 左旋
            cur = ((cur << 1) | (cur >> 15)) & 0xFFFF

            # 跟池中第 step 个卦 XOR
            if self._guas:
                idx = step % len(self._guas)
                cur ^= self._guas[idx].value

            ring_guas.append(Gua(cur))

        return ring_guas

    # ============================================================
    # 查询
    # ============================================================

    def find(self, target: Gua) -> list[Gua]:
        """找池中跟 target 咬合的卦元。"""
        return [g for g in self._guas if _fit(target, g)]

    def nearest(self, target: Gua, k: int = 3) -> list[tuple[Gua, int]]:
        """找池中汉明距离最近的 k 个卦。"""
        dists = [(g, hamming(target.value, g.value)) for g in self._guas]
        dists.sort(key=lambda x: x[1])
        return dists[:k]

    # ============================================================
    # 统计
    # ============================================================

    def stats(self) -> dict:
        """池子状态。"""
        if not self._guas:
            return {'总数': 0}
        potentials = [self.potential(g) for g in self._guas]
        hit_counts = [self._hits.get(id(g), 0) for g in self._guas]
        return {
            '总数': len(self._guas),
            'Ψ平均': sum(potentials) / max(1, len(potentials)),
            'Ψ最大': max(potentials),
            '总碰撞': sum(hit_counts),
            '最活跃': max(hit_counts),
        }

    def __len__(self):
        return len(self._guas)

    def __repr__(self):
        return f"Pool('{self.name}', {len(self._guas)}卦)"


# ============================================================
# 演示
# ============================================================
if __name__ == '__main__':
    from tools.encode import text_to_seed
    from tongzi_kernel import phi_slice

    pool = Pool("生态池")

    # 投鱼
    fish = "道法自然天地玄黄"
    print(f"「投鱼」{fish}")
    for ch in fish:
        v = phi_slice(text_to_seed(ch), 8)
        pool.drop(Gua(v))

    print(f"\n池: {pool}")
    for g in pool._guas:
        print(f"  {form(g)}")

    # 演化一轮
    print(f"\n「演化」")
    result = pool.evolve()
    print(f"  碰撞 {result['碰撞']} 次, 生子 {result['生子']} 个")
    print(f"  池: {pool}")

    # 环
    print(f"\n「环」道绕池")
    ring_g = pool.ring(Gua(phi_slice(text_to_seed("道"), 8)), steps=4)
    for i, rg in enumerate(ring_g):
        print(f"  [{i}] {form(rg)}")

    # 状态
    print(f"\n「状态」{pool.stats()}")

    # 近邻
    print(f"\n「近邻」找离'道'最近的")
    target = Gua(phi_slice(text_to_seed("道"), 8))
    for g, d in pool.nearest(target, 3):
        print(f"  {form(g)} 差{d}位")
