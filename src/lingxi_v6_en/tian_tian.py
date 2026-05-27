# -*- coding: utf-8 -*-
"""Three-Realm Celestial Management — Heaven 7 Officials · Earth 3 Bureaus · zero-float"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from guayuan import MASK28, hamming, xor_reduce


class TianTian:
    """Three-Realm Celestial Court full-management suite"""

    def __init__(self, lingxi=None):
        self.lingxi = lingxi
        self.alerts: list[str] = []
        self.quarantine: set = set()

        # ── Heaven Court Phase ──
        self.season = 0          # 0-Spring 1-Summer 2-Autumn 3-Winter
        self.season_cycle = 250
        self.last_harvest = 0

        # ── Earth Court Phase ──
        self.death_log: list = []
        self.oblivion_cycle = 200

        # ── Stats ──
        self.eco_peak = [0, 0, 0, 0]
        self.wander_path: list = []
        self.tick = 0

    def tick_once(self):
        self.tick += 1
        if not self.lingxi:
            return

        # Jade Emperor · Oversee — four-directional patrol
        self._jade_emperor_patrol()

        # Queen Mother · Nurture — seasonal rhythm
        self._queen_mother_season()

        # Grand Supreme · Observe — periodic sampling
        self._taishang_sample()

        # Thunder Ministry · Emergency — punishment check
        self._leibu_check()

        # Purple Tenuity · Trajectory — wander path
        self._ziwei_trail()

        # Year Star · Rhythm — season cycle
        self._taisui_season()

        # Wealth Ministry · Dispatch — resource expansion
        self._caibu_expand()

        # Yama · Judgment — judge + warm-up grace
        self._yanluo_judge()

        # Impermanence · Reclaim — rate-limited removal
        self._wuchang_reclaim()

        # Meng Po · Cleanse — periodic ghost/ctx purge
        self._mengpo_clean()

    # ═══ Heaven Court 7 Officials ═══
    def _jade_emperor_patrol(self):
        """Jade Emperor · Overseer: four-directional guard check"""
        lx = self.lingxi
        if not lx.l2.pool:
            self.alerts.append(f"t{self.tick} empty pool")
            return
        if len(lx.l2.pool) < lx.l2.capacity * 0.1:
            self.alerts.append(f"t{self.tick} pool depleted")
        for i, pool in enumerate(lx.l2.pool[:4]):
            if hamming(pool, lx.packet.body) < 3:
                self.quarantine.add(i)

    def _queen_mother_season(self):
        """Queen Mother · Nurture: maturity boost + peach harvest"""
        lx = self.lingxi
        for g in list(lx.l2.pool):
            if hamming(g, lx.packet.body) < 4:
                lx.l2.pool.append(g ^ ((7 + self.tick % 7) & MASK28))

        if self.tick - self.last_harvest > 100:
            self.last_harvest = self.tick
            self._peach_harvest()

    def _peach_harvest(self):
        """Peach Harvest Assembly: solidify nearby clusters"""
        lx = self.lingxi
        body = lx.packet.body
        harvested = 0
        for pool_idx in range(4):
            for g, data in list(lx.tongzi.eco[pool_idx].items()):
                if hamming(g, body) < 6:
                    data['hits'] = min(data['hits'] + 2, 10)
                    data['solid'] = True
                    harvested += 1
        if harvested > 0:
            self.alerts.append(f"t{self.tick} harvest:{harvested}")

    def _taishang_sample(self):
        """Grand Supreme · Observe: periodic 50-tick snapshot"""
        if self.tick % 50 == 0:
            lx = self.lingxi
            sample = {
                'tick': self.tick,
                'l2_active': lx.l2.active_count(),
                'phi_connections': lx.phi.size(),
                'l3_hex': lx.l3.current_hex_name(),
                'dxz_level': lx.dxz.align(lx.l3.active_gua)[0],
            }
            self.alerts.append(f"t{self.tick} sample:{sample}")

    def _leibu_check(self):
        """Thunder Ministry · Emergency: punishment threshold + cooldown"""
        lx = self.lingxi
        yj = lx.yj
        L_val = yj.three_talents(lx.l2.pool) if lx.l2.pool else 0
        if L_val > 0.5 and yj.trigger_count >= 5:
            self.alerts.append(f"t{self.tick} ⚡THUNDER: L={L_val:.3f} count={yj.trigger_count}")
            yj.trigger_count = max(0, yj.trigger_count - 2)

    def _ziwei_trail(self):
        """Purple Tenuity · Trajectory: bagua path tracking"""
        lx = self.lingxi
        self.wander_path.append(lx.l3.current_hex_name())
        if len(self.wander_path) > 20:
            self.wander_path.pop(0)

    def _taisui_season(self):
        """Year Star · Rhythm: Spring→Summer→Autumn→Winter cycle"""
        phase = (self.tick // self.season_cycle) % 4
        if phase != self.season:
            old = ['Spring', 'Summer', 'Autumn', 'Winter'][self.season]
            new = ['Spring', 'Summer', 'Autumn', 'Winter'][phase]
            self.alerts.append(f"t{self.tick} season:{old}→{new}")
            self.season = phase

    def _caibu_expand(self):
        """Wealth Ministry · Dispatch: auto-expand 4096→8192"""
        if self.tick % 200 == 0 and self.lingxi.l2.capacity < 8192:
            lx = self.lingxi
            old_cap = lx.l2.capacity
            lx.l2.capacity = min(lx.l2.capacity * 2, 8192)
            self.alerts.append(f"t{self.tick} expand:{old_cap}→{lx.l2.capacity}")

    # ═══ Earth Court 3 Bureaus ═══
    def _yanluo_judge(self):
        """Yama · Judgment: score-based judgment + warm-up grace"""
        if self.tick < 50:
            return
        lx = self.lingxi
        for pool_idx in range(4):
            eco = lx.tongzi.eco[pool_idx]
            dead = []
            for g, data in eco.items():
                score = data.get('hits', 0)
                solid = data.get('solid', False)
                if not solid and score <= 1:
                    dead.append(g)
            self.death_log.extend(dead)
            for g in dead:
                del eco[g]

    def _wuchang_reclaim(self):
        """Impermanence · Reclaim: max 50 reclaims per tick"""
        deadline = len(self.death_log) - 50
        if deadline > 0:
            self.death_log = self.death_log[deadline:]

    def _mengpo_clean(self):
        """Meng Po · Cleanse: periodic ghost+ctx purge"""
        if self.tick % self.oblivion_cycle == 0 and self.tick > 0:
            lx = self.lingxi
            lx.packet.ghost = 0
            lx.packet.ctx = 0
            self.alerts.append(f"t{self.tick} mengpo:ghost+ctx clean")

    # ── Reports ──
    def summary(self) -> str:
        return (
            f"TianTian t{self.tick} season={['Spring','Summer','Autumn','Winter'][self.season]} "
            f"alerts={len(self.alerts)} last={self.alerts[-1][:60] if self.alerts else 'none'}"
        )


if __name__ == '__main__':
    # Standalone test (no lingxi)
    tt = TianTian()
    for _ in range(10):
        tt.tick_once()
        print(f"  t{tt.tick}: season={tt.season}")
