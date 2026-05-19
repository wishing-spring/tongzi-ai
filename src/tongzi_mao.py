"""
童子 v0.5 · 出厂版：十二阴阳锚调度层
====================================
铁律对齐：十二锚不删不偏不废·阴阳差≤AUTO_BALANCE_THRESHOLD
常量对齐：tongzi_constants.py（已锁定）
"""
from tongzi_core import TongziCore
from tongzi_constants import *

class ShiErMao:
    """十二阴阳锚调度层"""

    阳锚名 = ('聚', '配', '顺', '升', '生', '连')
    阴锚名 = ('散', '破', '逆', '降', '溯', '断')

    def __init__(self, core: TongziCore):
        self.core = core
        self.阳态 = [False] * 6
        self.阴态 = [False] * 6
        self.聚散日志 = []
        self.升降日志 = []

    # ========== 锚状态 ==========

    def 阳活跃数(self) -> int:
        return sum(self.阳态)

    def 阴活跃数(self) -> int:
        return sum(self.阴态)

    def 阴阳差(self) -> int:
        return self.阳活跃数() - self.阴活跃数()

    def 激活阳锚(self, idx: int) -> bool:
        if self.阴阳差() >= YIN_YANG_MAX_DIFF:
            return False
        self.阳态[idx] = True
        return True

    def 激活阴锚(self, idx: int) -> bool:
        if self.阴阳差() <= -YIN_YANG_MAX_DIFF:
            return False
        self.阴态[idx] = True
        return True

    def 休眠阳锚(self, idx: int):
        self.阳态[idx] = False

    def 休眠阴锚(self, idx: int):
        self.阴态[idx] = False

    @property
    def 状态摘要(self) -> dict:
        return {
            '阳': ''.join('1' if s else '0' for s in self.阳态),
            '阴': ''.join('1' if s else '0' for s in self.阴态),
            '阴阳差': self.阴阳差(),
        }

    # ========== 阴阳自调（自保机制） ==========

    def auto_balance(self):
        """阴阳失衡自调：
        阳过盛→激活阴锚（散·断·降），休眠阳锚
        阴过盛→激活阳锚（聚·连·升），休眠阴锚
        """
        diff = self.阴阳差()
        if abs(diff) < AUTO_BALANCE_THRESHOLD:
            return False  # 无需调整

        if diff > 0:  # 阳盛
            # 关掉最不活跃的阳锚
            for i in [4, 5, 3, 2, 1, 0]:  # 生连升顺配聚 优先关外层
                if self.阳态[i]:
                    self.休眠阳锚(i)
                    diff -= 1
                    if diff < AUTO_BALANCE_THRESHOLD:
                        break
            # 激活阴锚
            for i in [0, 5, 3]:  # 散断降
                if not self.阴态[i] and self.阴阳差() >= AUTO_BALANCE_THRESHOLD:
                    self.激活阴锚(i)
        else:  # 阴盛
            for i in [4, 5, 3, 2, 1, 0]:
                if self.阴态[i]:
                    self.休眠阴锚(i)
                    diff += 1
                    if abs(diff) < AUTO_BALANCE_THRESHOLD:
                        break
            for i in [0, 5, 3]:
                if not self.阳态[i] and self.阴阳差() <= -AUTO_BALANCE_THRESHOLD:
                    self.激活阳锚(i)

        return True

    # ========== 阳六锚 ==========

    def 聚锚_相似抱团(self, 阈值: int = HAMMING_CLUSTER) -> list[list[str]]:
        tags = list(self.core.data.keys())
        n = len(tags)
        if n < 2:
            return []
        parent = {t: t for t in tags}
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        def union(x, y):
            rx, ry = find(x), find(y)
            if rx != ry:
                parent[rx] = ry
        for i in range(n):
            for j in range(i + 1, n):
                d = self.core.hamming(self.core.data[tags[i]], self.core.data[tags[j]])
                if d <= 阈值:
                    union(tags[i], tags[j])
                    self.core.active[tags[i]] = self.core.tick
                    self.core.active[tags[j]] = self.core.tick
        团表 = {}
        for t in tags:
            root = find(t)
            团表.setdefault(root, []).append(t)
        团列表 = [g for g in 团表.values() if len(g) >= 2]
        self.聚散日志.append(f'[聚] t={self.core.tick} 团{len(团列表)}')
        return 团列表

    def 配锚_阴阳对偶(self) -> list[tuple[str, str]]:
        全1 = FULL_MASK
        配对 = []
        tags = list(self.core.data.keys())
        for i in range(len(tags)):
            for j in range(i + 1, len(tags)):
                if self.core.xor(self.core.data[tags[i]], self.core.data[tags[j]]) == 全1:
                    配对.append((tags[i], tags[j]))
        return 配对

    def 顺锚_格雷码顺流(self, tag: str, 步数: int = 1) -> int | None:
        if tag not in self.core.data:
            return None
        v = self.core.data[tag]
        gray_step = 步数 ^ (步数 >> 1)
        return self.core.xor(v, gray_step) & FULL_MASK

    def 逆锚_格雷码回溯(self, tag: str, 步数: int = 1) -> int | None:
        return self.顺锚_格雷码顺流(tag, 步数)

    def 升锚_位增升层(self, tag_a: str, tag_b: str) -> int | None:
        if tag_a not in self.core.data or tag_b not in self.core.data:
            return None
        lo_a = self.core.data[tag_a] & 0xFF
        lo_b = self.core.data[tag_b] & 0xFF
        return ((lo_a << 8) | lo_b) & FULL_MASK

    def 降锚_消位降阶(self, tag: str) -> tuple[int, int] | None:
        if tag not in self.core.data:
            return None
        v = self.core.data[tag]
        return ((v >> 8) & 0xFF, v & 0xFF)

    def 生锚_异或自生(self, tag_a: str, tag_b: str) -> int | None:
        if tag_a not in self.core.data or tag_b not in self.core.data:
            return None
        return self.core.xor(self.core.data[tag_a], self.core.data[tag_b]) & FULL_MASK

    def 溯锚_逆算归源(self, tag_result: str, tag_one: str) -> int | None:
        if tag_result not in self.core.data or tag_one not in self.core.data:
            return None
        return self.core.xor(self.core.data[tag_result], self.core.data[tag_one]) & FULL_MASK

    def 连锚_差一邻接(self, tag: str) -> list[str]:
        if tag not in self.core.data:
            return []
        邻 = []
        v = self.core.data[tag]
        for t, tv in self.core.data.items():
            if t != tag and self.core.hamming(v, tv) == 1:
                邻.append(t)
                self.core.active[t] = self.core.tick
        return 邻

    def 断锚_主动切断(self, tags: list[str]):
        for t in tags:
            if t in self.core.active:
                self.core.active[t] = self.core.tick - PURGE_CYCLE_TICK - HALF_CYCLE

    # ========== 调度 ==========

    def 调度一周(self):
        n = self.core.size

        if n < 20:
            self.激活阳锚(0)
            self.休眠阴锚(0)
        elif n > 100:
            self.激活阴锚(0)
            self.休眠阳锚(0)

        if n < 30:
            self.激活阳锚(5)
        else:
            self.休眠阳锚(5)

        活跃比 = self.core.active_count / max(n, 1)
        if 活跃比 > 0.7:
            self.激活阳锚(4)
        if 活跃比 < 0.3:
            self.激活阴锚(4)

        # 阴阳自调
        self.auto_balance()

    def 执行活跃锚(self):
        结果 = {}
        if self.阳态[0]:
            结果['聚'] = self.聚锚_相似抱团()
        if self.阳态[1]:
            结果['配'] = self.配锚_阴阳对偶()
        if self.阳态[4]:
            tags = [t for t in self.core.data if self.core.active.get(t, 0) >= self.core.tick - GROWTH_TICK]
            if len(tags) >= 2:
                import random
                a, b = random.sample(tags, 2)
                新向量 = self.生锚_异或自生(a, b)
                新标签 = f'生_{a}_{b}'
                self.core.data[新标签] = 新向量
                self.core.active[新标签] = self.core.tick
                self.core.potency[新标签] = 0
                结果['生'] = 新标签
        if self.阳态[5]:
            tags = list(self.core.data.keys())
            if tags:
                import random
                t = random.choice(tags)
                结果['连'] = self.连锚_差一邻接(t)
        if self.阴态[5] and self.core.size > CONGESTION_THRESHOLD - 50:
            tags_sorted = sorted(self.core.active.keys(), key=lambda t: self.core.active[t])
            to_cut = tags_sorted[:max(1, len(tags_sorted) // 5)]
            self.断锚_主动切断(to_cut)
            结果['断'] = f'切断{len(to_cut)}'
        return 结果

    def tick_cycle(self):
        self.core.time_tick()
        self.调度一周()
        执行结果 = self.执行活跃锚()
        self.core.clean_dormant()
        # 定期归元
        if self.core.tick % RHYTHM_CYCLE == 0:
            self.core.return_to_source()
        # 淤积分流
        if self.core.tick % (RHYTHM_CYCLE * 3) == 0:
            self.core.decongest()
        return 执行结果
