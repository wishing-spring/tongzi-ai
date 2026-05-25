# -*- coding: utf-8 -*-
"""生态池 — 碰撞生子固化剪枝。不同规则，不同生态。"""

from typing import List
from .gua import Gua
from .constants import ID_MASK, CT_MASK
from .surge import surge_mask
from .antientropy import AntiEntropy

F0 = 48            # 降低门槛让子卦更快参与
FIT_MIN_DEFAULT = 6


class EcoPool:
    """生态池。每池独立能量/碰撞/固化状态。"""

    def __init__(self, name: str, *,
                 tau: int = 5,
                 fit_min: int = FIT_MIN_DEFAULT,
                 birth_rate: float = 1.0,
                 flow_back: bool = False,
                 density_max: int = 48,
                 stagnation_window: int = 5,
                 jitter_bits: int = 3):
        self.name = name
        self.tau = tau
        self.fit_min = fit_min
        self.birth_rate = birth_rate
        self.flow_back = flow_back
        self.density_max = density_max

        self.guas: List[Gua] = []
        self.births: List[Gua] = []
        self.total_births = 0
        self.total_solid = 0
        self.tick_count = 0
        self.antientropy = AntiEntropy(stagnation_window, jitter_bits)

        # 池本地状态 (不污染共享卦元)
        self._energy: dict[int, int] = {}   # id(g) → energy
        self._hits: dict[int, int] = {}     # id(g) → hit_count
        self._solid: set = set()            # id(g) of solidified

    def _energy_of(self, g: Gua) -> int:
        return self._energy.get(id(g), 0)
    def _set_energy(self, g: Gua, v: int):
        self._energy[id(g)] = v
    def _hit_of(self, g: Gua) -> int:
        return self._hits.get(id(g), 0)
    def _inc_hit(self, g: Gua):
        gid = id(g)
        self._hits[gid] = self._hits.get(gid, 0) + 1
    def _is_solid(self, g: Gua) -> bool:
        return id(g) in self._solid
    def _make_solid(self, g: Gua):
        self._solid.add(id(g))

    def pull(self, surge_pool, global_tick: int):
        existing = {id(g) for g in self.guas}
        for g in surge_pool.all():
            if len(self.guas) >= self.density_max * 5:
                break
            if id(g) not in existing:
                self._set_energy(g, 0)
                self.guas.append(g)
                existing.add(id(g))

    def tick(self, global_tick: int):
        self.tick_count += 1
        self.births.clear()
        births_this: List[Gua] = []

        alive = [g for g in self.guas if not self._is_solid(g)]

        # 1. 频率累积
        en = int(12 * self.birth_rate)
        for g in alive:
            if self.birth_rate > 0:
                self._set_energy(g, self._energy_of(g) + en)

        if self.birth_rate <= 0:
            self._cull()
            return

        # 2. 碰撞 — 涌動只作用于一方(非对称偏转)
        active = [g for g in alive if self._energy_of(g) >= F0]
        locked = set()

        for i, a in enumerate(active):
            if self._is_solid(a):
                continue
            for j, b in enumerate(active):
                if i >= j or self._is_solid(b):
                    continue
                pk = (id(a), id(b)) if id(a) < id(b) else (id(b), id(a))
                if pk in locked:
                    continue

                # 涌動窗口: 只匹配涌動相选中的比特段
                mask = surge_mask(global_tick)
                fab = ((a.ct & mask) & ~(b.ct & mask)).bit_count()
                fba = ((b.ct & mask) & ~(a.ct & mask)).bit_count()
                if max(fab, fba) < self.fit_min:
                    continue

                self._set_energy(a, max(0, self._energy_of(a) - F0))
                self._set_energy(b, max(0, self._energy_of(b) - F0))
                self._inc_hit(a)
                self._inc_hit(b)
                locked.add(pk)

                # 生子 — 裸XOR,涌動不污染子卦
                xc = (a.ct ^ b.ct) & CT_MASK
                ac = (a.ct & b.ct) & CT_MASK

                cx = Gua(value=(a.value & ID_MASK) | xc,
                         is_native=False, born_tick=global_tick)
                ca = Gua(value=(b.value & ID_MASK) | ac,
                         is_native=False, born_tick=global_tick)
                self._set_energy(cx, F0 // 2)
                self._set_energy(ca, F0 // 2)
                births_this.extend([cx, ca])

        # 3. 子卦入池
        for c in births_this:
            self.guas.append(c)
            self.total_births += 1
            if self.flow_back:
                self.births.append(c)

        # 4. 固化
        for g in self.guas:
            if not self._is_solid(g) and self._hit_of(g) >= 3:
                self._make_solid(g)
                self.total_solid += 1

        # 5. 剪枝 (只剪无生子)
        dead = [g for g in self.guas
                if not g.is_native and not self._is_solid(g)
                and self._hit_of(g) == 0
                and global_tick - g.born_tick > self.tau * 4]
        for g in dead:
            self.guas.remove(g)
            self._energy.pop(id(g), None)
            self._hits.pop(id(g), None)

        # 6. 密度
        self._cull()

        # 7. 反熵 — 僵化检测 + φ扰动注入
        if self.birth_rate > 0 and self.antientropy.check(self.total_births):
            jittered = 0
            # 优先: 子卦非固化 → 创建新卦(不改原值,避免key冲突)
            for g in self.guas:
                if not g.is_native and not self._is_solid(g):
                    new_ct = self.antientropy.jitter(g.ct, global_tick)
                    ng = Gua(value=(g.value & ID_MASK) | new_ct,
                             is_native=False, born_tick=global_tick)
                    self.guas.append(ng)
                    self._set_energy(ng, F0)
                    jittered += 1
                    if jittered >= 5:
                        break
            # 其次: 固化卦(唤醒)
            if jittered == 0:
                for g in self.guas:
                    if self._is_solid(g):
                        self._solid.discard(id(g))
                        new_ct = self.antientropy.jitter(g.ct, global_tick)
                        ng = Gua(value=(g.value & ID_MASK) | new_ct,
                                 is_native=False, born_tick=global_tick)
                        self.guas.append(ng)
                        self._set_energy(ng, F0)
                        jittered += 1
                        if jittered >= 3:
                            break
            # 最后: 原生卦(微调)
            if jittered == 0:
                from random import sample
                targets = [g for g in self.guas if g.is_native]
                for g in sample(targets, min(3, len(targets))):
                    new_ct = self.antientropy.jitter(g.ct, global_tick)
                    ng = Gua(value=(g.value & ID_MASK) | new_ct,
                             is_native=False, born_tick=global_tick)
                    self.guas.append(ng)
                    self._set_energy(ng, F0)
                    jittered += 1

    def _cull(self):
        # 总卦数上限
        while len(self.guas) > self.density_max * 8:
            victim = None
            for g in self.guas:
                if not g.is_native and not self._is_solid(g):
                    victim = g
                    break
            if victim is None:
                break
            self.guas.remove(victim)
            self._energy.pop(id(victim), None)
            self._hits.pop(id(victim), None)

        ns = [g for g in self.guas
              if not g.is_native and not self._is_solid(g)]
        if len(ns) > self.density_max:
            vics = sorted(ns, key=lambda g: self._energy_of(g))
            kill = len(ns) - self.density_max
            for g in vics[:kill]:
                self.guas.remove(g)
                self._energy.pop(id(g), None)
                self._hits.pop(id(g), None)

    def stats(self) -> str:
        al = sum(1 for g in self.guas if not self._is_solid(g))
        sl = sum(1 for g in self.guas if self._is_solid(g))
        return (f"{self.name} {len(self.guas)}卦 "
                f"alive={al} solid={sl} births={self.total_births}")
