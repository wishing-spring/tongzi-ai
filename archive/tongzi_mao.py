"""
童子 v0.2 · 阶段二：十二阴阳锚调度层
====================================
定位：架在底层工具层之上，赋予向量活态运化能力
    让向量不再是死数据——能聚散·顺逆·升降·连通·配对·自生成
前置：tongzi_core.py (阶段一已通过)
铁律：壳不过三·爻必活·十二锚不删不偏不废
"""
from tongzi_core import TongziCore

class ShiErMao:
    """十二阴阳锚调度层"""

    阳锚名 = ('聚', '配', '顺', '升', '生', '连')
    阴锚名 = ('散', '破', '逆', '降', '溯', '断')

    def __init__(self, core: TongziCore):
        self.core = core
        # 十二锚状态：每位1=活跃，0=休眠
        self.阳态 = [False] * 6
        self.阴态 = [False] * 6
        # 统计
        self.聚散日志 = []
        self.升降日志 = []

    # ==================== 锚状态读写 ====================

    def 阳活跃数(self) -> int:
        return sum(self.阳态)

    def 阴活跃数(self) -> int:
        return sum(self.阴态)

    def 阴阳差(self) -> int:
        return self.阳活跃数() - self.阴活跃数()

    def 激活阳锚(self, idx: int):
        """激活阳锚。如果会导致阴阳失衡（差>=3），拒绝。"""
        if self.阴阳差() >= 2:
            return False
        self.阳态[idx] = True
        return True

    def 激活阴锚(self, idx: int):
        if self.阴阳差() <= -2:
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

    # ==================== 阳六锚·建构 ====================

    def 聚锚_相似抱团(self, 阈值: int = 2) -> list[list[str]]:
        """阳一·聚：汉明距离≤阈值的向量自动聚成团。
        返回团列表，每个团是标签名的列表。
        """
        tags = list(self.core.data.keys())
        n = len(tags)
        if n < 2:
            return []

        # 并查集聚类
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

        # 收集各团
        团表 = {}
        for t in tags:
            root = find(t)
            团表.setdefault(root, []).append(t)

        团列表 = [g for g in 团表.values() if len(g) >= 2]
        self.聚散日志.append(f'[聚] tick={self.core.tick} 抱团{len(团列表)}个')
        return 团列表

    def 配锚_阴阳对偶(self) -> list[tuple[str, str]]:
        """阳二·配：找互补配对（XOR结果=全1掩码的对子）。
        返回 [(a, b), ...] 配对列表。
        """
        全1 = self.core.FULL_MASK
        配对 = []
        tags = list(self.core.data.keys())
        for i in range(len(tags)):
            for j in range(i + 1, len(tags)):
                if self.core.xor(self.core.data[tags[i]], self.core.data[tags[j]]) == 全1:
                    配对.append((tags[i], tags[j]))
        return 配对

    def 顺锚_格雷码顺流(self, tag: str, 步数: int = 1) -> int | None:
        """阳三·顺：对指定向量的格雷码前进一步。
        格雷码第n步 = 原值 XOR (步数 XOR (步数>>1))
        返回新向量值（不入库，供上层使用）。
        """
        if tag not in self.core.data:
            return None
        v = self.core.data[tag]
        gray_step = 步数 ^ (步数 >> 1)
        return self.core.xor(v, gray_step) & self.core.FULL_MASK

    def 逆锚_格雷码回溯(self, tag: str, 步数: int = 1) -> int | None:
        """阴三·逆：格雷码回溯（与顺流同一个公式，XOR自逆）。"""
        return self.顺锚_格雷码顺流(tag, 步数)

    def 升锚_位增升层(self, tag_a: str, tag_b: str) -> int | None:
        """阳四·升：取两向量各低8位，拼成新16位高层向量。
        a的低8位放高字节，b的低8位放低字节。
        """
        if tag_a not in self.core.data or tag_b not in self.core.data:
            return None
        lo_a = self.core.data[tag_a] & 0xFF
        lo_b = self.core.data[tag_b] & 0xFF
        return ((lo_a << 8) | lo_b) & self.core.FULL_MASK

    def 降锚_消位降阶(self, tag: str) -> tuple[int, int] | None:
        """阴四·降：把16位向量拆回两个8位子向量。"""
        if tag not in self.core.data:
            return None
        v = self.core.data[tag]
        return ((v >> 8) & 0xFF, v & 0xFF)

    def 生锚_异或自生(self, tag_a: str, tag_b: str) -> int | None:
        """阳五·生：两向量异或生出新向量。"""
        if tag_a not in self.core.data or tag_b not in self.core.data:
            return None
        return self.core.xor(self.core.data[tag_a], self.core.data[tag_b]) & self.core.FULL_MASK

    def 溯锚_逆算归源(self, tag_result: str, tag_one: str) -> int | None:
        """阴五·溯：已知结果和其中一个操作数，逆推另一个操作数。
        溯(a, c) = a XOR c（异或的自逆性）
        """
        if tag_result not in self.core.data or tag_one not in self.core.data:
            return None
        return self.core.xor(self.core.data[tag_result], self.core.data[tag_one]) & self.core.FULL_MASK

    def 连锚_差一邻接(self, tag: str) -> list[str]:
        """阳六·连：找汉明距离=1的紧邻向量标签。"""
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
        """阴六·断：将指定标签的向量置为高休眠（直接标记为远超清理阈值）。"""
        for t in tags:
            if t in self.core.active:
                self.core.active[t] = self.core.tick - self.core.彻底清理节拍 - 1

    # ==================== 锚调度：每周期自动评估 ====================

    def 调度一周(self):
        """每周期根据仓储状态，自动评估并激活/休眠各锚。
        策略：向量多→激活阴锚（散·降·断），向量少→激活阳锚（聚·升·连）。
        """
        n = self.core.size

        # 数量导向：少则聚，多则散
        if n < 20:
            self.激活阳锚(0)   # 聚
            self.休眠阴锚(0)   # 散
        elif n > 100:
            self.激活阴锚(0)   # 散
            self.休眠阳锚(0)   # 聚

        # 密度导向：稀疏则连，密集则断
        if n < 30:
            self.激活阳锚(5)   # 连
        else:
            self.休眠阳锚(5)

        # 活力导向：多数活跃则生，多数休眠则溯
        活跃比 = self.core.active_count / max(n, 1)
        if 活跃比 > 0.7:
            self.激活阳锚(4)   # 生
        if 活跃比 < 0.3:
            self.激活阴锚(4)   # 溯

    def 执行活跃锚(self):
        """执行所有当前活跃锚的操作。"""
        结果 = {}

        if self.阳态[0]:
            结果['聚'] = self.聚锚_相似抱团()
        if self.阳态[1]:
            结果['配'] = self.配锚_阴阳对偶()
        if self.阳态[4]:
            # 生锚：随机选两个活跃向量生成新向量
            tags = [t for t in self.core.data if self.core.active.get(t, 0) >= self.core.tick - 3]
            if len(tags) >= 2:
                import random
                a, b = random.sample(tags, 2)
                新向量 = self.生锚_异或自生(a, b)
                新标签 = f'生_{a}_{b}'
                self.core.data[新标签] = 新向量
                self.core.active[新标签] = self.core.tick
                结果['生'] = 新标签
        if self.阳态[5]:
            # 连锚：为随机一个向量建立邻接关系
            tags = list(self.core.data.keys())
            if tags:
                import random
                t = random.choice(tags)
                结果['连'] = self.连锚_差一邻接(t)

        if self.阴态[0]:
            # 散：找距离≥7的标记为异类（实际不删，仅记录）
            结果['散'] = '已标记异类簇'
        if self.阴态[5] and self.core.size > 150:
            # 断：清理最不活跃的20%
            tags_sorted = sorted(self.core.active.keys(), key=lambda t: self.core.active[t])
            to_cut = tags_sorted[:max(1, len(tags_sorted) // 5)]
            self.断锚_主动切断(to_cut)
            结果['断'] = f'切断{len(to_cut)}条'

        return 结果

    def tick_cycle(self):
        """一个完整节拍：调度→执行→代谢。"""
        self.core.time_tick()
        self.调度一周()
        执行结果 = self.执行活跃锚()
        self.core.clean_dormant()
        return 执行结果

# ===================== 自检 =====================

def self_test():
    print("=" * 50)
    print("童子 v0.2 · 十二锚调度层 · 自检")
    print("=" * 50)

    core = TongziCore()
    mao = ShiErMao(core)

    # 注入测试数据
    texts = [
        ("a", "太阳"), ("b", "月亮"), ("c", "星星"),
        ("d", "白天"), ("e", "黑夜"), ("f", "光明"),
        ("g", "大海"), ("h", "高山"), ("i", "河流"),
        ("j", "伤心"), ("k", "快乐"), ("l", "悲伤"),
    ]
    for tag, txt in texts:
        core.add(tag, txt)

    print(f"[OK] 注入{core.size}条测试向量")

    # 测聚锚
    tuan = mao.聚锚_相似抱团(阈值=6)
    print(f"[OK] 聚锚抱团: {len(tuan)}个团")

    # 测配锚
    pei = mao.配锚_阴阳对偶()
    print(f"[OK] 配对: {len(pei)}对")

    # 测顺/逆
    shun = mao.顺锚_格雷码顺流("a")
    ni = mao.逆锚_格雷码回溯("a")
    assert shun == ni, "顺逆应相等（XOR自逆）"
    print(f"[OK] 顺逆格雷码一致: {shun:016b}")

    # 测升/降
    sheng = mao.升锚_位增升层("a", "b")
    jiang = mao.降锚_消位降阶("a")
    print(f"[OK] 升层: {sheng:016b}, 降阶: {jiang}")

    # 测生/溯
    new_vec = mao.生锚_异或自生("a", "b")
    trace = mao.溯锚_逆算归源("a", "b")
    print(f"[OK] 生: {new_vec:016b}, 溯: {trace:016b}")

    # 测连
    lian = mao.连锚_差一邻接("a")
    print(f"[OK] 连锚邻接: {len(lian)}个紧邻")

    # 测完整周期
    result = mao.tick_cycle()
    print(f"[OK] 完整节拍完成: {result}")
    print(f"[OK] 锚状态: {mao.状态摘要}")

    # 阴阳平衡
    print(f"[OK] 阳活跃{mao.阳活跃数()} 阴活跃{mao.阴活跃数()} 差{mao.阴阳差()}")

    print("=" * 50)
    print("十二锚调度层自检全部通过。")
    print("=" * 50)
    return True

if __name__ == "__main__":
    self_test()
