# -*- coding: utf-8 -*-
"""灵犀八卦盘 — 24h旋转的语义盘"""
import math, time, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from ref8 import BAGUA, BAGUA_NAMES

# 盘上8个位点（环形排列）
# 索引0=乾(子/北), 1=兑, 2=离, 3=震, 4=巽, 5=坎, 6=艮, 7=坤(午/南)
# 逆时针旋转 = 时间前进


class BaguaPlate:
    """八卦盘: 24小时旋转一圈。每个位点自带语义。"""

    def __init__(self):
        self.angle = 0.0          # 当前旋转角 0~2π
        self.last_update = time.time()
        self.dream_perturb = 0.0  # 做梦微扰

    def sync(self) -> float:
        """同步时间: 算旋转角。返回当前角度(弧度)。"""
        now = time.time()
        elapsed = now - self.last_update
        if elapsed <= 0:
            return self.angle

        # 旋转: 24h一圈
        self.angle += elapsed * (2 * math.pi / 86400.0)
        self.angle %= 2 * math.pi

        # 做梦微扰: 布朗步 + 阻尼
        import random
        step = (random.random() - 0.5) * 0.002 * math.sqrt(elapsed)
        self.dream_perturb += step
        self.dream_perturb *= 0.999

        self.last_update = now
        return self.angle

    def active_zone(self) -> str:
        """盘当前指向哪个卦区域"""
        self.sync()
        # 8个卦均匀分布: 每个占 π/4 弧度
        idx = int((self.angle % (2 * math.pi)) / (math.pi / 4)) % 8
        return BAGUA_NAMES[idx]

    def zone_for(self, bagua: str) -> float:
        """给定卦在盘上的弧度位置"""
        idx = BAGUA_NAMES.index(bagua)
        return idx * math.pi / 4

    def distance_on_plate(self, a: str, b: str) -> int:
        """两个卦在盘上的环形距离(步数)"""
        ia = BAGUA_NAMES.index(a)
        ib = BAGUA_NAMES.index(b)
        d = abs(ia - ib)
        return min(d, 8 - d)  # 环形距离

    def yinyang_freq(self) -> float:
        """阴阳频率 0(阴盛/午夜)~1(阳盛/中午)"""
        self.sync()
        # 角度0=子时(阴盛), 角度π=午时(阳盛)
        return (math.sin(self.angle - math.pi / 2) + 1) / 2

    def time_of_day(self) -> str:
        """当前时辰描述"""
        f = self.yinyang_freq()
        if f < 0.2:
            return '深夜'
        elif f < 0.4:
            return '凌晨'
        elif f < 0.6:
            return '上午'
        elif f < 0.8:
            return '午后'
        else:
            return '傍晚'


if __name__ == '__main__':
    plate = BaguaPlate()
    print(f"当前角: {plate.angle:.3f} rad")
    print(f"活跃区: {plate.active_zone()} · {BAGUA[plate.active_zone()]['meaning']}")
    print(f"时辰:   {plate.time_of_day()}")
    print(f"阴阳:   {plate.yinyang_freq():.3f}")

    # 测试环形距离
    for a, b in [('乾', '坤'), ('离', '坎'), ('乾', '兑'), ('震', '巽')]:
        print(f"  盘距({a},{b}) = {plate.distance_on_plate(a,b)} 步")
