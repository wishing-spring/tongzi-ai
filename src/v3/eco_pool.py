# -*- coding: utf-8 -*-
"""Eco Pool — where gua collide, give birth, solidify, get pruned.

Each eco pool has its own rules (birth rate, fit threshold, solidification,
anti-entropy). Multiple pools with different rules = ecological diversity.
"""

from typing import List
from .gua import Gua
from .constants import ID_MASK, CT_MASK
from .surge import surge_mask
from .antientropy import AntiEntropy

F0 = 48
FIT_MIN_DEFAULT = 6


class EcoPool:
    """Ecological pool. Each pool has independent energy/hit/solid state."""

    def __init__(self, name: str, *,
                 tau: int = 5,
                 fit_min: int = FIT_MIN_DEFAULT,
                 birth_rate: float = 1.0,
                 flow_back: bool = False,
                 density_max: int = 48,
                 stagnation_window: int = 5,
                 jitter_bits: int = 3):
        self.name = name
        self.tau = tau                    # age threshold for culling
        self.fit_min = fit_min            # minimum Hamming fit for collision
        self.birth_rate = birth_rate      # energy gained per tick
        self.flow_back = flow_back        # send children back to surge pool
        self.density_max = density_max    # max non-native active gua

        self.guas: List[Gua] = []
        self.births: List[Gua] = []       # pending flowback
        self.total_births = 0
        self.total_solid = 0
        self.tick_count = 0
        self.antientropy = AntiEntropy(stagnation_window, jitter_bits)

        # Pool-local state (does not mutate shared Gua objects)
        self._energy: dict[int, int] = {}  # id(g) → energy
        self._hits: dict[int, int] = {}    # id(g) → collision count
        self._solid: set = set()           # id(g) of solidified gua

    # --- private helpers ---
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
        """Pull gua from the surge pool into this eco pool."""
        existing = {id(g) for g in self.guas}
        for g in surge_pool.all():
            if len(self.guas) >= self.density_max * 5:
                break
            if id(g) not in existing:
                self._set_energy(g, 0)
                self.guas.append(g)
                existing.add(id(g))

    def tick(self, global_tick: int):
        """One heartbeat: accumulate energy, collide, birth, solidify, cull."""
        self.tick_count += 1
        self.births.clear()
        births_this: List[Gua] = []

        alive = [g for g in self.guas if not self._is_solid(g)]

        # 1. Energy accumulation
        en = int(12 * self.birth_rate)
        for g in alive:
            if self.birth_rate > 0:
                self._set_energy(g, self._energy_of(g) + en)

        if self.birth_rate <= 0:
            self._cull()
            return

        # 2. Collision — XOR + AND across the surge window
        active = [g for g in alive if self._energy_of(g) >= F0]
        locked = set()

        mask = surge_mask(global_tick)

        for i, a in enumerate(active):
            if self._is_solid(a):
                continue
            for j, b in enumerate(active):
                if i >= j or self._is_solid(b):
                    continue
                pk = (min(id(a), id(b)), max(id(a), id(b)))
                if pk in locked:
                    continue

                # Asymmetric fit: each direction checked independently
                fab = ((a.ct & mask) & ~(b.ct & mask)).bit_count()
                fba = ((b.ct & mask) & ~(a.ct & mask)).bit_count()
                if max(fab, fba) < self.fit_min:
                    continue

                self._set_energy(a, max(0, self._energy_of(a) - F0))
                self._set_energy(b, max(0, self._energy_of(b) - F0))
                self._inc_hit(a)
                self._inc_hit(b)
                locked.add(pk)

                # Birth — bare XOR/AND, surge does NOT contaminate children
                xc = (a.ct ^ b.ct) & CT_MASK
                ac = (a.ct & b.ct) & CT_MASK

                cx = Gua(value=(a.value & ID_MASK) | xc,
                         is_native=False, born_tick=global_tick)
                ca = Gua(value=(b.value & ID_MASK) | ac,
                         is_native=False, born_tick=global_tick)
                self._set_energy(cx, F0 // 2)
                self._set_energy(ca, F0 // 2)
                births_this.extend([cx, ca])

        # 3. Admit children
        for c in births_this:
            self.guas.append(c)
            self.total_births += 1
            if self.flow_back:
                self.births.append(c)

        # 4. Solidification — 3+ hits → irreversible memory
        for g in self.guas:
            if not self._is_solid(g) and self._hit_of(g) >= 3:
                self._make_solid(g)
                self.total_solid += 1

        # 5. Prune — remove barren non-native gua
        dead = [g for g in self.guas
                if not g.is_native and not self._is_solid(g)
                and self._hit_of(g) == 0
                and global_tick - g.born_tick > self.tau * 4]
        for g in dead:
            self.guas.remove(g)
            self._energy.pop(id(g), None)
            self._hits.pop(id(g), None)

        # 6. Density control
        self._cull()

        # 7. Anti-entropy — detect stagnation, inject φ-guided jitter
        if self.birth_rate > 0 and self.antientropy.check(self.total_births):
            jittered = 0
            # Priority 1: non-native, non-solid children (safest to jitter)
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
            # Priority 2: wake solidified gua (un-solidify + jitter)
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
            # Priority 3: native gua (last resort, minimal jitter)
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
        """Density control — remove low-energy non-native gua when crowded."""
        # Hard cap
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

        # Soft cap — remove lowest-energy non-native
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
        return (f"{self.name} {len(self.guas)} gua "
                f"alive={al} solid={sl} births={self.total_births}")
