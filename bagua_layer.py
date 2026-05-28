# -*- coding: utf-8 -*-
"""Inference Layer v8.0 — rotating base grid · projection on user focal anchor · shortest path = reasoning"""
import os, sys, time
from .guayuan import MASK28, hamming, gua_hash, xor_reduce
from .shared_pool import SharedPool

BAGUA_NAMES = ['乾', '兑', '离', '震', '巽', '坎', '艮', '坤']

# ═══════════════════════════════════════
# grand grid clock
# ═══════════════════════════════════════

class GrandBaguaPlate:
    """Grand inference grid: rotates with time, multi-layer nested cycles"""

    LAYERS = {
        '两仪': 2, '三才': 3, '四象': 4, '五行': 5,
        '六合': 6, '七星': 7, '八卦': 8, '九宫': 9,
        '十方': 10, '元辰': 12, '节气': 24,
        '天干': 10, '地支': 12, '甲子': 60,
    }

    def __init__(self):
        self.refs: list[int] = []  # 64-cell reference codes
        self.tick = 0
        self.time_stamps: list[list[int]] = [[] for _ in range(64)]  # time stamp per cell
        self._build_plate()

    def _build_plate(self):
        for upper in range(8):
            for lower in range(8):
                ref = (upper << 25) | (lower << 22)
                fill = upper ^ lower
                for i in range(8):
                    fill = ((fill << 3) ^ (fill * 7)) & 0x3FFFFF
                ref |= fill & 0x3FFFFF
                self.refs.append(ref & MASK28)

    def tick_clock(self) -> dict:
        """Advance grand grid clock + leave time stamps"""
        self.tick += 1
        now = time.localtime()
        idx = self.tick % 64

        # time stamp: record time on current cell
        self.time_stamps[idx].append(self.tick)
        if len(self.time_stamps[idx]) > 100:
            self.time_stamps[idx] = self.time_stamps[idx][-50:]

        # positions across all nested layers
        positions = {name: self.tick % period
                     for name, period in self.LAYERS.items()}

        # grid vector = base ref XOR time encoding
        plate_gua = self.refs[idx]
        plate_gua ^= (now.tm_hour << 20)
        plate_gua ^= (now.tm_yday << 8)
        plate_gua &= MASK28

        hex_name = f"{BAGUA_NAMES[idx // 8]}{BAGUA_NAMES[idx % 8]}"

        return {
            'tick': self.tick,
            'idx': idx,
            'hex': hex_name,
            'trigram': BAGUA_NAMES[idx // 8],
            'plate_gua': plate_gua,
            'positions': positions,
            'stamp_count': len(self.time_stamps[idx]),
        }

    def get_time_mark(self, idx: int) -> int:
        """Get time stamp intensity for a cell"""
        return len(self.time_stamps[idx])


# ═══════════════════════════════════════
# projection work grid — unfolded on user profile as focal anchor
# ═══════════════════════════════════════

class ProjectedBagua:
    """临时投射盘：将世界层活跃字团映射到八卦位"""

    def __init__(self):
        self.projection: list[list[str]] = [[] for _ in range(8)]  # 8 single cells
        self.tianyuan_gua: int = 0  # focal anchor (user profile vector)
        self.tianyuan_pos: int = 0  # focal anchor cell index

    def project(self, pool: SharedPool, user_gua: int) -> dict:
        """
        以user_gua为天元，将世界层活跃字团映射到8卦位。
        映射规则：
        - 天元卦位=user_gua映射到的八卦索引
        - 活跃字团按(Hamming距离/8)散布到不同卦位
        - 同类字团倾向聚集在邻近卦位
        """
        self.tianyuan_gua = user_gua
        self.tianyuan_pos = user_gua % 8  # focal anchor projected cell
        self.projection = [[] for _ in range(8)]

        active = pool.get_active()

        for name in active:
            star = pool.get_star(name)
            if not star:
                continue
            # 活跃字团的卦元与天元的Hamming距离决定卦位偏移
            dist = hamming(star.gua, user_gua)
            # 偏移：距离/4（28位最多28，/4后0-7）
            offset = min(7, dist // 4)
            pos = (self.tianyuan_pos + offset) % 8
            self.projection[pos].append(name)

        # 同卦位内按能量排序
        for i in range(8):
            self.projection[i].sort(
                key=lambda n: pool.get_star(n).energy if pool.has_star(n) else 0,
                reverse=True
            )

        return self._report()

    def _report(self) -> dict:
        return {
            'tianyuan_pos': self.tianyuan_pos,
            'tianyuan_gua_hex': hex(self.tianyuan_gua),
            'positions': {BAGUA_NAMES[i]: self.projection[i] for i in range(8)},
            'total_projected': sum(len(p) for p in self.projection),
        }


# ═══════════════════════════════════════
# shortest path = reasoning
# ═══════════════════════════════════════

class LightningPath:
    """闪电路径：在投射空间中跨字团跳跃 = 思维链"""

    def __init__(self, max_jumps: int = 5):
        self.max_jumps = max_jumps
        self.path: list[tuple] = []  # [(from_pos, from_word, to_pos, to_word), ...]

    def strike(self, projection: ProjectedBagua, pool: SharedPool) -> list[dict]:
        """
        闪电：从投射盘中跳跃。
        - 从天元卦位出发
        - 每跳选择邻近卦位中能量最高的字团
        - 形成一条思路链
        """
        self.path = []
        pos = projection.tianyuan_pos
        visited = set()

        for _ in range(self.max_jumps):
            # 当前卦位中选一个未访问的字团
            candidates = [(n, pool.get_star(n).energy)
                         for n in projection.projection[pos]
                         if n not in visited and pool.has_star(n)]
            if not candidates:
                # 跳到邻位
                pos = (pos + 1) % 8
                continue

            # 选能量最高的
            candidates.sort(key=lambda x: x[1], reverse=True)
            word = candidates[0][0]
            visited.add(word)

            # 下一跳方向：按字团间连接确定
            star = pool.get_star(word)
            next_pos = pos
            if star and star.constellation:
                con_name = star.constellation
                if con_name in pool.constellations:
                    cons = pool.constellations[con_name]
                    # 跳到邻接星座
                    if cons.neighbors:
                        nb_name = max(cons.neighbors, key=cons.neighbors.get)
                        if nb_name in pool.constellations:
                            # 取邻接星座中能量最高的星
                            nb_stars = [(s, pool.get_star(s).energy)
                                       for s in pool.constellations[nb_name].stars
                                       if pool.has_star(s)]
                            if nb_stars:
                                nb_stars.sort(key=lambda x: x[1], reverse=True)
                                best_nb = nb_stars[0][0]
                                nb_dist = hamming(pool.get_star(best_nb).gua,
                                                 projection.tianyuan_gua)
                                next_pos = (projection.tianyuan_pos + min(7, nb_dist // 4)) % 8

            self.path.append({
                'from_pos': BAGUA_NAMES[pos],
                'word': word,
                'energy': round(pool.get_star(word).energy, 2),
            })

            pos = next_pos if next_pos != pos else (pos + 1) % 8

        return self.path


# ═══════════════════════════════════════
# 八卦主控
# ═══════════════════════════════════════

class BaguaMaster:
    """八卦层主控：大底盘 + 投射盘 + 闪电路径"""

    def __init__(self):
        self.plate = GrandBaguaPlate()
        self.projected = ProjectedBagua()
        self.lightning = LightningPath(max_jumps=5)

    def tick(self, pool: SharedPool, user_gua: int) -> dict:
        """一帧八卦推演"""
        # ① 大底盘走时
        clock = self.plate.tick_clock()

        # ② 投射盘展开
        projection = self.projected.project(pool, user_gua)

        # ③ 闪电路径
        path = self.lightning.strike(self.projected, pool)

        return {
            'clock': clock,
            'projection': projection,
            'lightning': path,
        }
