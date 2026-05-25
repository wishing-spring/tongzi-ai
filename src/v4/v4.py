# -*- coding: utf-8 -*-
"""灵悉 v4 — F₂身体 × v4.3灵魂 · 统一调度器

架构:
  输入 → 四芯编码 → 涌动池 → 生态池
    ＋
  双天元 → 脊骨 → 刚柔折叠 → 引力 → 因果贯通
    ↓
  五流汇合 → 探针扭曲 → 输出
"""

import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from v3.constants import CT_MASK, phi_slice, ID_MASK
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
    """灵悉 v4 · 完整系统"""

    # ═══ v3 底层: 碰撞生子 ═══
    surge: SurgePool = field(default_factory=SurgePool)
    eco_pools: List[EcoPool] = field(default_factory=list)
    global_tick: int = 0

    # ═══ v4 上层: 自我+记忆+意识+道德 ═══
    user_tianyuan: TianYuan = field(default_factory=default_user_tianyuan)
    ai_tianyuan: TianYuan = field(default_factory=default_ai_tianyuan)
    user_spine: Spine = field(default_factory=Spine)
    ai_spine: Spine = field(default_factory=Spine)
    fold: RigidFlexFold = field(default_factory=RigidFlexFold)
    gravity: Gravity = field(default_factory=Gravity)
    causal: CausalState = field(default_factory=CausalState)
    probe: CausalProbe = field(default_factory=CausalProbe)
    streams: StreamCollector = field(default_factory=StreamCollector)

    # ═══ 状态 ═══
    char_history: List[int] = field(default_factory=list)  # 历史输入ct
    response_history: List[int] = field(default_factory=list)  # 历史输出ct
    natives: List[Gua] = field(default_factory=list)

    def feed(self, text: str):
        """喂入对话"""
        self.surge.ingest(text)
        self.natives = [g for g in self.surge.all() if g.is_native]

    def add_pool(self, pool: EcoPool):
        self.eco_pools.append(pool)

    def tick(self):
        """一次心跳 = v3碰撞 + v4折叠 + 因果贯通"""
        self.global_tick += 1

        # ═══ 1. 阴阳频率 ═══
        yinyang_freq = compute_yinyang_freq()

        # ═══ 2. v3底层: pull → 碰撞 → flowback ═══
        for pool in self.eco_pools:
            pool.pull(self.surge, self.global_tick)
            pool.tick(self.global_tick)
            for c in pool.births:
                self.surge.accept(c)
            pool.births.clear()

        # ═══ 3. v4: 天元演化(每10tick一次) ═══
        if self.global_tick % 10 == 0:
            # 用户天元: 吸收最近输入
            if self.char_history:
                recent_ct = self.char_history[-1]
                self.user_tianyuan.evolve(recent_ct, self.global_tick)

            # AI天元: 吸收最近输出
            if self.response_history:
                recent_out = self.response_history[-1]
                self.ai_tianyuan.evolve(recent_out, self.global_tick, rate=0.03)

            # 记录脊骨
            self.user_spine.record(self.user_tianyuan.ct, suit=0)
            self.ai_spine.record(self.ai_tianyuan.ct, suit=1)

        # ═══ 4. 刚柔折叠(每5tick) ═══
        if self.global_tick % 5 == 0:
            self.fold.fold(
                actual_ct=self.ai_tianyuan.ct,
                spine=self.ai_spine,
                yinyang_freq=yinyang_freq,
                tick=self.global_tick
            )

    def chat(self, input_text: str):
        """对话入口: 输入→全链→自然语言输出。返回 (文字, V4Response)。"""
        r = self.respond(input_text)
        
        yf = compute_yinyang_freq()
        yy = "阳盛" if yf > 0.5 else ("阴藏" if yf < 0.3 else "交泰")
        
        text = speak(
            input_text=input_text,
            attractors=r.attractors,
            gravity_dist=r.hamming_to_good,
            gravity_quad=r.good_quadrant,
            fold_trend=r.fold_trend,
            fold_dev=r.fold_deviation,
            causal_tension=r.causal_tension,
            yinyang_state=yy,
        )
        return text, r

    def respond(self, input_text: str) -> V4Response:
        """对话: 输入 → 全链处理 → 全态输出"""

        # ═══ 喂入 ═══
        chars = list(dict.fromkeys(list(input_text.replace(' ', ''))))
        self.feed(' '.join(chars))

        input_cts = []
        for ch in chars:
            ct = encode(ch, 0) & CT_MASK
            input_cts.append(ct)
            self.char_history.append(ct)

        prev_ai_ct = self.ai_tianyuan.ct

        # 跑tick（可配置，默认60）
        n = getattr(self, 'TICKS_PER_QUERY', 60)
        for _ in range(n):
            self.tick()

        # ═══ 收集五流 ═══
        recent_solid_cts = []
        for pool in self.eco_pools:
            for g in pool.guas:
                if not g.is_native:
                    recent_solid_cts.append(g.ct)
        self.streams.set_rule_drift(recent_solid_cts[-5:] if recent_solid_cts else input_cts)
        self.streams.set_char_avg(input_cts)
        self.streams.set_experience(self.char_history)
        self.streams.fold_ct = self.fold.generated_now_ct
        self.streams.gravity_ct = self.gravity.pull(
            self.fold.generated_now_ct, self.global_tick)

        # ═══ 因果模拟 ═══
        self.causal.simulate(
            rule_drift=self.streams.rule_drift,
            char_avg=self.streams.char_avg,
            experience=self.streams.experience,
            fold_generated=self.streams.fold_ct,
            gravity_target=self.streams.gravity_ct,
            tick=self.global_tick)

        # ═══ 原始回答 ═══
        raw_response = 0
        all_children = []
        for pool in self.eco_pools:
            for g in pool.guas:
                if not g.is_native:
                    all_children.append(g)
        if all_children:
            for g in all_children[-50:]:
                raw_response ^= g.ct
        else:
            raw_response = input_cts[0] if input_cts else 0

        response_ct = self.probe.probe(raw_response, self.causal, self.global_tick)
        if is_forbidden(response_ct, threshold=4):
            response_ct = self.gravity.pull(response_ct, self.global_tick)

        self.response_history.append(response_ct)

        # ═══ 映射到最近字 ═══
        native_by_ct = {g.ct: g for g in self.natives}
        best_name, best_dist = "?", 99
        for nct, ng in native_by_ct.items():
            d = (response_ct ^ nct).bit_count()
            if d < best_dist:
                best_dist = d
                best_name = express(ng, self.natives)

        # ═══ 组装全态响应 ═══
        yf = compute_yinyang_freq()
        yy = "阳盛" if yf > 0.5 else ("阴藏" if yf < 0.3 else "交泰")

        sources = {
            '规则': self.streams.rule_drift,
            '字符': self.streams.char_avg,
            '经验': self.streams.experience,
            '折叠': self.streams.fold_ct,
            '引力': self.streams.gravity_ct,
        }

        sims = {}
        source_list = list(sources.values())
        source_names = list(sources.keys())
        for i in range(len(source_list)):
            for j in range(i+1, len(source_list)):
                dist = (source_list[i] ^ source_list[j]).bit_count() / 28.0
                sims[f"{source_names[i]}↔{source_names[j]}"] = round(1.0 - dist, 3)

        gd = self.gravity.distance_to_good(self.ai_tianyuan.ct)
        quad = self.gravity.quadrance(self.ai_tianyuan.ct)

        pool_lines = []
        for pool in self.eco_pools:
            al = sum(1 for g in pool.guas if not pool._is_solid(g))
            sl = sum(1 for g in pool.guas if pool._is_solid(g))
            pool_lines.append(f"{pool.name}: {pool.total_births}孩 {sl}固 {al}活 {pool.antientropy.total_jitters}反熵")

        # ═══ 吸引子: 按新鲜度加权(最近的孩子权重更高) ═══
        attractors = []
        for pool in self.eco_pools:
            sol = sorted(
                [g for g in pool.guas if pool._is_solid(g)],
                key=lambda g: g.born_tick if hasattr(g, 'born_tick') else 0,
                reverse=True
            )
            if sol:
                # 新鲜加权: 最近的权重×3, 其余的×1
                fresh_cut = len(sol) // 3
                weighted = Counter()
                for i, g in enumerate(sol):
                    name = express(g, self.natives)
                    w = 3 if i < fresh_cut else 1
                    weighted[name] += w
                attractors.extend(f"{n}({c})" for n, c in weighted.most_common(2))

        fold_gap = (self.fold.generated_now_ct ^ self.ai_tianyuan.ct).bit_count()

        return V4Response(
            input_text=input_text,
            nearest_char=best_name,
            hamming_dist=best_dist,
            user_tianyuan_ct=self.user_tianyuan.ct,
            ai_tianyuan_ct=self.ai_tianyuan.ct,
            user_spine_points=self.user_spine.count,
            ai_spine_points=self.ai_spine.count,
            user_inertia_bits=self.user_spine.recent_inertia(5).bit_count(),
            ai_delta_bits=(self.ai_tianyuan.ct ^ prev_ai_ct).bit_count(),
            fold_deviation=self.fold.deviation,
            fold_trend=self.fold.trend(),
            past_rigid_ct=self.fold.past_rigid_ct,
            future_main_ct=self.fold.future_main_ct,
            generated_now_ct=self.fold.generated_now_ct,
            fold_gap_hamming=fold_gap,
            hamming_to_good=gd,
            good_quadrant=quad,
            forbidden=is_forbidden(response_ct),
            gravity_pull_applied=int(28 * self.gravity.strength),
            causal_tension=self.causal.causal_tension,
            causal_confidence=self.causal.causal_confidence,
            causal_state_ct=self.causal.causal_state,
            stream_sources=sources,
            stream_similarity=sims,
            yinyang_freq=yf,
            yinyang_state=yy,
            surge_size=len(self.surge),
            native_count=len(self.natives),
            pools_summary=pool_lines,
            total_births=sum(p.total_births for p in self.eco_pools),
            total_solid=sum(p.total_solid for p in self.eco_pools),
            attractors=attractors,
        )

    # ═══ 持久化 ═══
    def save(self, path: str):
        """保存脊骨 + 天元到文件"""
        import json
        data = {
            'global_tick': self.global_tick,
            'user_tianyuan_ct': self.user_tianyuan.ct,
            'ai_tianyuan_ct': self.ai_tianyuan.ct,
            'user_spine': [(p.ts, p.ct, p.suit) for p in self.user_spine.points],
            'ai_spine': [(p.ts, p.ct, p.suit) for p in self.ai_spine.points],
            'char_history': self.char_history[-100:],
        }
        with open(path, 'w') as f:
            json.dump(data, f)

    def load(self, path: str) -> bool:
        """从文件恢复脊骨 + 天元"""
        import json
        from .spine import SpinePoint
        try:
            with open(path) as f:
                data = json.load(f)
            self.global_tick = data.get('global_tick', 0)
            self.user_tianyuan.ct = data.get('user_tianyuan_ct', 0)
            self.ai_tianyuan.ct = data.get('ai_tianyuan_ct', 0)
            for ts, ct, suit in data.get('user_spine', []):
                self.user_spine.points.append(SpinePoint(ts=ts, ct=ct, suit=suit))
            for ts, ct, suit in data.get('ai_spine', []):
                self.ai_spine.points.append(SpinePoint(ts=ts, ct=ct, suit=suit))
            self.char_history = data.get('char_history', [])
            return True
        except:
            return False

    # ═══ 对话 ═══
    def chat(self, input_text: str):
        """对话入口: 输入→全链→自然语言输出。返回 (文字, V4Response)。"""
        r = self.respond(input_text)
        
        yf = compute_yinyang_freq()
        yy = "阳盛" if yf > 0.5 else ("阴藏" if yf < 0.3 else "交泰")
        
        text = speak(
            input_text=input_text,
            attractors=r.attractors,
            gravity_dist=r.hamming_to_good,
            gravity_quad=r.good_quadrant,
            fold_trend=r.fold_trend,
            fold_dev=r.fold_deviation,
            causal_tension=r.causal_tension,
            yinyang_state=yy,
        )
        return text, r

    def status(self) -> str:
        """状态摘要"""
        yf = compute_yinyang_freq()
        yy = "阳盛" if yf > 0.5 else ("阴藏" if yf < 0.3 else "交泰")

        lines = [
            f"灵悉v4 tick={self.global_tick} {yy}({yf:.2f})",
            f"涌池={len(self.surge)}卦",
            f"用户天元: 0x{self.user_tianyuan.ct:07x}  脊骨:{self.user_spine.count}点",
            f"AI天元:   0x{self.ai_tianyuan.ct:07x}  脊骨:{self.ai_spine.count}点",
            f"折叠: 偏差{self.fold.deviation:.3f} 趋势:{self.fold.trend()}",
            f"引力: 离善{self.gravity.distance_to_good(self.ai_tianyuan.ct)}bit",
            f"因果: 张力{self.causal.causal_tension:.2f}",
        ]
        for pool in self.eco_pools:
            al = sum(1 for g in pool.guas if not pool._is_solid(g))
            sl = sum(1 for g in pool.guas if pool._is_solid(g))
            lines.append(f"  {pool.name}: {pool.total_births}孩 {sl}固 {al}活 {pool.antientropy.total_jitters}反熵")
        return '\n'.join(lines)
