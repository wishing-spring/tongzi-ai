# -*- coding: utf-8 -*-
"""Shared Pool v8.1 — unit clusters · prefix skeleton · suffix drift · wave propagation"""
import os, sys, time, random
from .guayuan import MASK28, hamming, gua_hash, xor_reduce, random_gua


class StarEntity:
    """A pool unit = a character/word entity with bit-vector"""
    __slots__ = ('name', 'gua', 'energy', 'state', 'phase',
                 'prefix_gua', 'suffix_gua', 'constellation', 'time_stamp')

    def __init__(self, name: str, gua: int, constellation: str = ''):
        self.name = name
        self.gua = gua
        self.energy = 0.0
        self.state = 'dormant'
        self.phase = 0.0
        self.prefix_gua = gua_hash(name[0]) if name else 0
        self.suffix_gua = gua
        self.constellation = constellation
        self.time_stamp = 0


class Constellation:
    """A cluster of related units"""
    __slots__ = ('name', 'stars', 'neighbors', 'total_energy')

    def __init__(self, name: str):
        self.name = name
        self.stars: set[str] = set()
        self.neighbors: dict[str, float] = {}
        self.total_energy = 0.0


class SharedPool:
    """World layer: single entity pool shared by all layers"""

    DORMANT_THRESHOLD = 0.0
    ACTIVE_THRESHOLD = 0.25
    FLOWING_THRESHOLD = 0.65

    YIN_BIAS = 0.0
    YANG_BIAS = 0.0

    def __init__(self):
        self.stars: dict[str, StarEntity] = {}
        self.constellations: dict[str, Constellation] = {}
        self.tick = 0
        self.cooccur: dict[str, dict[str, int]] = {}
        self.seed()

    def seed(self):
        """Seed clusters by radical/semantic category"""
        constellation_map = {
            '天象':  '日月星辰气云雾雨雪风雷天阳光蓝',
            '地形':  '山石土水泥沙金木火田面',
            '人身':  '人手足眼口心血肉骨皮耳舌头吃',
            '生物':  '树花草鸟鱼虫兽叶',
            '运动':  '走动飞落升流变转震停开合起到吹',
            '心理':  '喜怒哀乐爱恨惧欲思忘惊安',
            '社会':  '家国王民父子友敌战和争',
            '属性':  '大小长短高低快慢好坏美丑真假新旧刚柔轻重太',
            '时空':  '时空前后左右上下中外远近到',
            '逻辑':  '一二三多加减等非因果若则与或为什么是的结',
            '物理':  '力质量重力速度惯性压强温度摩擦反射冰冷',
            '化学':  '溶液金属化合氧化反应元素分子原子',
            '生概':  '细胞组织器官生态生死病愈',
        }

        for con_name, chars in constellation_map.items():
            cons = Constellation(con_name)
            for ch in chars:
                gua = gua_hash(ch)
                star = StarEntity(ch, gua, con_name)
                self.stars[ch] = star
                cons.stars.add(ch)
            self.constellations[con_name] = cons

        extra = '梦醒问答说听看读写算季节昼夜年月男女老幼'
        for ch in extra:
            if ch not in self.stars:
                con = self._guess_constellation(ch)
                star = StarEntity(ch, gua_hash(ch), con)
                self.stars[ch] = star
                if con in self.constellations:
                    self.constellations[con].stars.add(ch)

        self._build_bridges()

    def _guess_constellation(self, ch: str) -> str:
        """Guess unit cluster by semantics"""
        nature = {'梦':'心理','醒':'心理','问':'社会','答':'社会',
                  '说':'社会','听':'人身','看':'人身','读':'社会',
                  '写':'社会','算':'逻辑','季节':'时空','昼夜':'天象',
                  '年':'时空','月':'天象','男':'人身','女':'人身',
                  '老':'属性','幼':'属性','病':'生概','愈':'生概'}
        return nature.get(ch, '属性')

    def _build_bridges(self):
        """Build inter-cluster bridges via semantic adjacency"""
        bridge_map = {
            '天象':  ['地形', '物理'],
            '地形':  ['天象', '物理', '生物'],
            '人身':  ['生物', '心理', '运动'],
            '生物':  ['地形', '人身', '生概'],
            '运动':  ['物理', '人身', '时空'],
            '心理':  ['人身', '社会'],
            '社会':  ['心理', '人身', '时空'],
            '属性':  ['时空', '物理', '心理'],
            '时空':  ['运动', '物理', '属性'],
            '逻辑':  ['物理', '属性'],
            '物理':  ['运动', '地形', '天象', '时空', '属性'],
            '化学':  ['物理', '生概'],
            '生概':  ['生物', '化学'],
        }
        for con_name, neighbors in bridge_map.items():
            if con_name in self.constellations:
                cons = self.constellations[con_name]
                for nb in neighbors:
                    if nb in self.constellations:
                        total_d = 0
                        pairs_n = 0
                        for s1 in cons.stars:
                            g1 = self.stars[s1].gua
                            for s2 in self.constellations[nb].stars:
                                g2 = self.stars[s2].gua
                                total_d += hamming(g1, g2)
                                pairs_n += 1
                        avg_d = total_d / max(pairs_n, 1)
                        cons.neighbors[nb] = max(0.1, 1.0 - avg_d / 28.0)

    def activate(self, text: str, energy_boost: float = 0.6) -> set:
        """Input text → activate units + record co-occurrence"""
        activated = set()
        chars = [ch for ch in text if ch in self.stars]
        for ch in chars:
            star = self.stars[ch]
            star.energy = min(1.0, star.energy + energy_boost)
            star.time_stamp = self.tick
            star.state = self._calc_state(star.energy)
            activated.add(ch)

        for i, a in enumerate(chars):
            if a not in self.cooccur:
                self.cooccur[a] = {}
            for j, b in enumerate(chars):
                if i != j:
                    self.cooccur[a][b] = self.cooccur[a].get(b, 0) + 1

        return activated

    def semantic_neighbors(self, char: str, top_n: int = 10) -> list[tuple[str, int]]:
        """Query semantic neighbors: chars most frequently co-occurring"""
        if char not in self.cooccur:
            return []
        neighbors = sorted(self.cooccur[char].items(), key=lambda x: x[1], reverse=True)
        return neighbors[:top_n]

    def semantic_path(self, char_a: str, char_b: str) -> list[str]:
        """Shortest semantic path between two chars via co-occurrence"""
        if char_a not in self.cooccur or char_b not in self.cooccur:
            return []

        if char_b in self.cooccur[char_a]:
            return [char_a, char_b]

        candidates = set()
        for mid in self.cooccur[char_a]:
            if mid in self.cooccur and char_b in self.cooccur.get(mid, {}):
                candidates.add(mid)

        if candidates:
            best = max(candidates,
                      key=lambda m: self.cooccur[char_a].get(m, 0) + self.cooccur[m].get(char_b, 0))
            return [char_a, best, char_b]

        return []

    def semantic_field(self, chars: list[str]) -> dict[str, list]:
        """Multi-char semantic field: neighbors + intersection"""
        fields = {}
        for ch in chars:
            fields[ch] = self.semantic_neighbors(ch, 5)

        if len(chars) >= 2:
            common = set(self.cooccur.get(chars[0], {}).keys())
            for ch in chars[1:]:
                common &= set(self.cooccur.get(ch, {}).keys())
            fields['_common'] = list(common)[:10]

        return fields

    def _calc_state(self, energy: float) -> str:
        threshold = self.ACTIVE_THRESHOLD + self.YIN_BIAS - self.YANG_BIAS
        if energy <= self.DORMANT_THRESHOLD:
            return 'dormant'
        elif energy < threshold:
            return 'dormant'
        elif energy < self.FLOWING_THRESHOLD:
            return 'active'
        else:
            return 'flowing'

    def tick_world(self, heartbeat_gua: int = 0):
        """Single world-frame evolution: wave propagation + suffix drift"""
        self.tick += 1

        # ① Wave propagation: active units → same cluster → adjacent clusters
        active = self.get_active()
        wave_hits: dict[str, float] = {}

        for star_name in active:
            star = self.stars[star_name]
            con_name = star.constellation
            if con_name not in self.constellations:
                continue
            cons = self.constellations[con_name]

            wave_strength = star.energy * 0.3
            for sibling in cons.stars:
                if sibling != star_name:
                    dist = hamming(star.gua, self.stars[sibling].gua)
                    decay = max(0.05, 1.0 - dist / 28.0)
                    wave_hits[sibling] = wave_hits.get(sibling, 0) + wave_strength * decay

            for nb_name, bridge_strength in cons.neighbors.items():
                if nb_name in self.constellations:
                    nb_cons = self.constellations[nb_name]
                    for nb_star in nb_cons.stars:
                        dist = hamming(star.gua, self.stars[nb_star].gua)
                        decay = max(0.02, 1.0 - dist / 28.0)
                        wave_hits[nb_star] = wave_hits.get(nb_star, 0) + \
                            wave_strength * bridge_strength * decay * 0.3

        for star_name, incoming in wave_hits.items():
            if star_name in self.stars:
                s = self.stars[star_name]
                s.energy = min(1.0, s.energy + incoming)
                if incoming > 0.05:
                    s.time_stamp = self.tick

        # ② Suffix drift: modulated by heartbeat
        if heartbeat_gua:
            for star_name in self.get_hot(30):
                star = self.stars[star_name]
                shift = heartbeat_gua ^ (star.gua >> 7)
                star.suffix_gua = (star.suffix_gua ^ (shift & 0xFFF)) & MASK28
                star.phase = (star.phase + (star.suffix_gua & 0xF) * 0.01) % 6.283

        # ③ Decay: long-inactive units
        for star in self.stars.values():
            if star.time_stamp < self.tick - 5:
                star.energy = max(0.0, star.energy - 0.08)
            star.state = self._calc_state(star.energy)

        # ④ Cluster total energy update
        for cons in self.constellations.values():
            cons.total_energy = sum(
                self.stars[s].energy for s in cons.stars
                if s in self.stars
            )

        # ⑤ Semantic gravity: co-occurrence → energy exchange (every 5 frames)
        if self.tick % 5 == 0 and self.cooccur:
            for a, neighbors in self.cooccur.items():
                if a not in self.stars:
                    continue
                total_co = sum(neighbors.values())
                for b, count in neighbors.items():
                    if b not in self.stars:
                        continue
                    strength = count / max(total_co, 1) * 0.05
                    ea = self.stars[a].energy
                    eb = self.stars[b].energy
                    if ea > eb:
                        self.stars[b].energy = min(1.0, eb + strength)
                    else:
                        self.stars[a].energy = min(1.0, ea + strength)

    def get_active(self) -> set:
        return {name for name, s in self.stars.items()
                if s.state in ('active', 'flowing')}

    def get_hot(self, n: int = 10) -> list:
        return sorted(self.stars, key=lambda k: self.stars[k].energy, reverse=True)[:n]

    def get_constellation_energy(self, star_name: str) -> float:
        """Get total energy of the cluster a unit belongs to"""
        star = self.stars.get(star_name)
        if not star or star.constellation not in self.constellations:
            return 0.0
        return self.constellations[star.constellation].total_energy

    def get_star(self, name: str):
        return self.stars.get(name)

    def has_star(self, name: str) -> bool:
        return name in self.stars

    def wave_frontier(self, star_name: str, hops: int = 2) -> set:
        """Get active units within N hops from source"""
        star = self.stars.get(star_name)
        if not star:
            return set()
        con_name = star.constellation
        if con_name not in self.constellations:
            return set()

        frontier = set()
        cons = self.constellations[con_name]

        for s in cons.stars:
            if s in self.stars and self.stars[s].state in ('active', 'flowing'):
                frontier.add(s)

        if hops > 1:
            for nb_name in cons.neighbors:
                if nb_name in self.constellations:
                    for s in self.constellations[nb_name].stars:
                        if s in self.stars and self.stars[s].state in ('active', 'flowing'):
                            frontier.add(s)

        return frontier

    def dampen(self, factor: float = 0.3):
        """Dampen pool energy to prevent sequential contamination"""
        for con in self.constellations.values():
            con.total_energy *= factor
        for star in self.stars.values():
            star.energy *= factor

    def snapshot(self) -> dict:
        active = self.get_active()
        hot = self.get_hot(8)
        return {
            'tick': self.tick,
            'total_stars': len(self.stars),
            'total_constellations': len(self.constellations),
            'active': len(active),
            'hot': hot,
            'constellation_energy': {
                name: round(cons.total_energy, 2)
                for name, cons in sorted(
                    self.constellations.items(),
                    key=lambda x: x[1].total_energy, reverse=True
                )[:8]
            },
            'yin_bias': round(self.YIN_BIAS, 2),
            'yang_bias': round(self.YANG_BIAS, 2),
        }
