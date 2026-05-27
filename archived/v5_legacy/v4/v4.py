# -*- coding: utf-8 -*-
"""V4 scheduler: F₂ body x v4.3 self-model. Unified tick loop."""

import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from v3.constants import CT_MASK, phi_slice
from v3.encode import encode
from v3.gua import Gua
from v3.express import express
from v3.surge_pool import SurgePool
from v3.eco_pool import EcoPool

from .tianyuan import TianYuan, default_user_tianyuan, default_ai_tianyuan
from .spine import Spine
from .fold import RigidFlexFold, compute_yinyang_freq
from .output import V4Response
from .gravity import Gravity, is_forbidden
from .speak import speak
from .causal import CausalState, CausalProbe, StreamCollector

from dataclasses import dataclass, field
from typing import List, Optional
from collections import Counter


@dataclass
class LingxiV4:
    surge: SurgePool = field(default_factory=SurgePool)
    eco_pools: List[EcoPool] = field(default_factory=list)
    global_tick: int = 0

    user_tianyuan: TianYuan = field(default_factory=default_user_tianyuan)
    ai_tianyuan: TianYuan = field(default_factory=default_ai_tianyuan)
    user_spine: Spine = field(default_factory=Spine)
    ai_spine: Spine = field(default_factory=Spine)
    fold: RigidFlexFold = field(default_factory=RigidFlexFold)
    gravity: Gravity = field(default_factory=Gravity)
    causal: CausalState = field(default_factory=CausalState)
    probe: CausalProbe = field(default_factory=CausalProbe)
    streams: StreamCollector = field(default_factory=StreamCollector)

    char_history: List[int] = field(default_factory=list)
    response_history: List[int] = field(default_factory=list)
    natives: List[Gua] = field(default_factory=list)

    def feed(self, text: str):
        self.surge.ingest(text)
        self.natives = [g for g in self.surge.all() if g.is_native]

    def add_pool(self, pool: EcoPool):
        self.eco_pools.append(pool)

    def tick(self):
        self.global_tick += 1
        yinyang_freq = compute_yinyang_freq()

        for pool in self.eco_pools:
            pool.pull(self.surge, self.global_tick)
            pool.tick(self.global_tick)
            for c in pool.births:
                self.surge.accept(c)
            pool.births.clear()

        if self.global_tick % 10 == 0:
            if self.char_history:
                avg_ct = self._char_avg()
                self.user_tianyuan.evolve(avg_ct, self.global_tick, rate=0.03)
                self.ai_tianyuan.evolve(avg_ct, self.global_tick, rate=0.05)
                self.user_spine.record(self.user_tianyuan.ct, suit=0)
                self.ai_spine.record(self.ai_tianyuan.ct, suit=1)

            self.fold.fold(self.ai_tianyuan.ct, self.ai_spine, yinyang_freq, self.global_tick)

    def _char_avg(self) -> int:
        if not self.char_history:
            return 0
        result = 0
        for i in range(28):
            ones = sum(1 for ct in self.char_history if (ct >> i) & 1)
            if ones > len(self.char_history) / 2:
                result |= (1 << i)
        return result & CT_MASK

    def chat(self, text: str, ticks_per_round: int = 300) -> tuple:
        self.feed(text)
        for ch in text:
            self.char_history.append(encode(ch, 0))

        old_births = sum(p.total_births for p in self.eco_pools)
        for _ in range(ticks_per_round):
            self.tick()

        new_births = sum(p.total_births for p in self.eco_pools)

        # build response
        resp = V4Response()
        resp.input_text = text

        all_solid = []
        for pool in self.eco_pools:
            all_solid.extend([g for g in pool.guas if pool._is_solid(g)])
        for pool in self.eco_pools:
            all_solid.extend(g for g in pool.guas if pool._is_solid(g))
        # deduplicate by ct
        seen = set()
        unique_solid = []
        for g in all_solid:
            if g.ct not in seen:
                seen.add(g.ct)
                unique_solid.append(g)

        native_list = [g for g in self.surge.all() if g.is_native]
        if unique_solid and native_list:
            best = min(unique_solid, key=lambda g: self._dist_to_natives(g, native_list))
            resp.nearest_char = express(best, native_list)
            resp.hamming_dist = min(
                (g.ct ^ best.ct).bit_count() for g in native_list
            )
        else:
            resp.nearest_char = '?'
            resp.hamming_dist = 0

        resp.user_tianyuan_ct = self.user_tianyuan.ct
        resp.ai_tianyuan_ct = self.ai_tianyuan.ct
        resp.user_spine_points = self.user_spine.count
        resp.ai_spine_points = self.ai_spine.count
        resp.user_inertia_bits = self.user_spine.recent_inertia(5).bit_count()
        resp.ai_delta_bits = (self.ai_tianyuan.ct ^ self.user_tianyuan.ct).bit_count()

        resp.fold_deviation = self.fold.deviation
        resp.fold_trend = self.fold.fold_trend()
        resp.past_rigid_ct = self.fold.past_rigid_ct
        resp.future_main_ct = self.fold.future_main_ct
        resp.generated_now_ct = self.fold.generated_now_ct
        resp.fold_gap_hamming = (self.fold.generated_now_ct ^ self.ai_tianyuan.ct).bit_count()

        resp.hamming_to_good = self.gravity.distance_to_good(resp.ai_tianyuan_ct)
        resp.good_quadrant = ""
        resp.forbidden = is_forbidden(resp.ai_tianyuan_ct)

        # gravity pull
        pulled = self.gravity.pull(self.ai_tianyuan.ct, self.global_tick)
        resp.gravity_pull_applied = (self.ai_tianyuan.ct ^ pulled).bit_count()

        # causal: five streams
        rule_drift = self.user_spine.recent_inertia(5)
        char_avg = self._char_avg()
        experience = self.ai_tianyuan.ct
        fold_gen = self.fold.generated_now_ct
        gravity_target = self.gravity.target_ct

        self.causal.simulate(rule_drift, char_avg, experience, fold_gen,
                             gravity_target, self.global_tick)
        resp.causal_tension = self.causal.causal_tension
        resp.causal_confidence = self.causal.causal_confidence
        resp.causal_state_ct = self.causal.causal_state

        self.streams.collect(rule_drift=rule_drift, char_avg=char_avg,
                             experience=experience, fold_generated=fold_gen,
                             gravity_target=gravity_target)
        resp.stream_sources = dict(self.streams.sources)
        for a, b in [("rule_drift", "char_avg"), ("fold_generated", "gravity_target"),
                     ("experience", "char_avg")]:
            resp.stream_similarity[f"{a}/{b}"] = self.streams.similarity(a, b)

        # yinyang
        freq = compute_yinyang_freq()
        resp.yinyang_freq = freq
        resp.yinyang_state = "day" if freq > 0.5 else "night"

        resp.surge_size = len(self.surge.all())
        resp.native_count = len([g for g in self.surge.all() if g.is_native])

        resp.pools_summary = [p.stats() for p in self.eco_pools]
        resp.total_births = sum(p.total_births for p in self.eco_pools)
        resp.total_solid = sum(1 for p in self.eco_pools for g in p.guas if p._is_solid(g))

        # attractor names
        attractor_counter = Counter()
        for g in unique_solid:
            name = express(g, native_list)
            attractor_counter[name] += 1
        resp.attractors = [f"{name}({cnt})" for name, cnt in attractor_counter.most_common(10)]

        # text reply
        reply = speak(text, resp.attractors, resp.hamming_to_good,
                      resp.good_quadrant, resp.fold_trend,
                      resp.fold_deviation, resp.causal_tension,
                      resp.yinyang_state)

        self.response_history.append(self.ai_tianyuan.ct)
        return reply, resp

    def _dist_to_natives(self, g, natives):
        return min((g.ct ^ n.ct).bit_count() for n in natives) if natives else 99

    def status(self) -> str:
        lines = [
            f"=== V4 Status tick={self.global_tick} ===",
            f"user tianyuan: 0x{self.user_tianyuan.ct:07x} spine={self.user_spine.count}",
            f"AI tianyuan:   0x{self.ai_tianyuan.ct:07x} spine={self.ai_spine.count}",
            f"fold dev={self.fold.deviation:.3f} trend={self.fold.fold_trend()}",
            f"gravity dist={self.gravity.distance_to_good(self.ai_tianyuan.ct)}",
            f"causal conf={self.causal.causal_confidence:.3f} tension={self.causal.causal_tension:.3f}",
            f"surge={self.surge.stats()}",
        ]
        for p in self.eco_pools:
            lines.append(p.stats())
        return '\n'.join(lines)

    def save(self, path: str) -> bool:
        try:
            data = {
                'tick': self.global_tick,
                'user_tianyuan_ct': self.user_tianyuan.ct,
                'ai_tianyuan_ct': self.ai_tianyuan.ct,
                'user_spine': [(p.ts, p.ct, p.suit) for p in self.user_spine.points],
                'ai_spine': [(p.ts, p.ct, p.suit) for p in self.ai_spine.points],
            }
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False

    def load(self, path: str) -> bool:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.global_tick = data['tick']
            self.user_tianyuan.ct = data['user_tianyuan_ct']
            self.ai_tianyuan.ct = data['ai_tianyuan_ct']
            for ts, ct, suit in data.get('user_spine', []):
                self.user_spine.record(ct=ct, suit=suit, ts=ts)
            for ts, ct, suit in data.get('ai_spine', []):
                self.ai_spine.record(ct=ct, suit=suit, ts=ts)
            return True
        except Exception:
            return False
