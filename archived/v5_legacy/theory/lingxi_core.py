# -*- coding: utf-8 -*-
"""灵犀核心 — 统一引擎: 盘+双天元+脊骨+折叠+引力+因果+输出"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from ref8 import BAGUA, BAGUA_NAMES
from lingxi_plate import BaguaPlate
from lingxi_tianyuan import TianYuan, Spine
from lingxi_dynamics import RigidFlexFold, Gravity, CausalChain
from lingxi_output import LingxiSpeaker


class LingxiCore:
    """灵犀R12简化版 — 全语义驱动"""

    def __init__(self):
        # 盘
        self.plate = BaguaPlate()

        # 双天元
        self.user_ty = TianYuan('坤')  # 用户: 出厂=坤(土·包容)
        self.ai_ty = TianYuan('坎')    # AI: 出厂=坎(水·和谐)

        # 双脊骨
        self.user_spine = Spine()
        self.ai_spine = Spine()

        # 折叠·引力·因果
        self.fold = RigidFlexFold()
        self.gravity = Gravity(0.7)  # 70%拉回好区
        self.causal = CausalChain()

        # 输出
        self.speaker = LingxiSpeaker(self.plate)

        # 历史
        self.tick = 0
        self.history = []

    def receive(self, bridge_bagua: str, attractor: int = 0, input_text: str = '') -> str:
        """接收童子桥投影: (卦名, 吸引子, 原始输入)"""
        self.tick += 1
        self.plate.sync()

        # 1. 天元漂移
        self.user_ty.attract(bridge_bagua, rate=0.07)
        self.ai_ty.attract(bridge_bagua, rate=0.07)
        plate_zone = self.plate.active_zone()
        self.ai_ty.attract(plate_zone, rate=0.02)
        self.ai_ty.drift_by_momentum()

        # 2. 脊骨记录
        self.user_spine.record(self.user_ty, self.tick)
        self.ai_spine.record(self.ai_ty, self.tick)

        # 3. 刚柔折叠
        yy = self.plate.yinyang_freq()
        self.fold.fold_mixed(
            ai_ty=self.ai_ty,
            user_spine=self.user_spine,
            ai_spine=self.ai_spine,
            yinyang_freq=yy)
        if self.fold.deviation > 0.15:
            self.ai_ty.attract(self.fold.generated_now, rate=0.06)

        # 4. 引力拉动
        pulled = self.gravity.pull(self.ai_ty)
        if pulled != self.ai_ty.bagua:
            self.ai_ty.bagua = pulled

        # 5. 因果贯通
        self.causal.merge(
            rule_bagua=bridge_bagua,
            char_bagua=bridge_bagua,
            experience_bagua=self.ai_spine.dominant(20),
            fold_bagua=self.fold.generated_now,
            gravity_bagua=self.ai_ty.bagua,
        )

        # 6. 第九卦
        ninth_triggered = self.causal.is_tense()
        if ninth_triggered:
            self.ai_ty.attract(self.causal.causal_state, rate=0.08)

        # 7. 输出 (传入吸引子)
        response = self.speaker.speak(
            ai_bagua=self.ai_ty.bagua,
            causal=self.causal,
            input_bagua=bridge_bagua,
            attractor=attractor,
            input_text=input_text,
        )

        self.history.append({
            'tick': self.tick,
            'input_bagua': bridge_bagua,
            'user_ty': self.user_ty.bagua,
            'ai_ty': self.ai_ty.bagua,
            'fold_dev': round(self.fold.deviation, 3),
            'causal_state': self.causal.causal_state,
            'causal_tension': round(self.causal.causal_tension, 3),
            'ninth': ninth_triggered,
            'response': response,
        })

        return response

    def report(self) -> str:
        lines = []
        lines.append(f"=== 灵犀核心 tick={self.tick} ===")
        lines.append(f"盘: {self.plate.active_zone()} · {self.plate.time_of_day()}")
        lines.append(f"用户天元: {self.user_ty.bagua}({self.user_ty.meaning()}) "
                     f"偏移={self.user_ty.offset:+.3f}")
        lines.append(f"AI天元:   {self.ai_ty.bagua}({self.ai_ty.meaning()}) "
                     f"偏移={self.ai_ty.offset:+.3f}")
        lines.append(f"折叠: 生成={self.fold.generated_now} 偏差={self.fold.deviation:.3f}")
        lines.append(f"引力: 距好区={self.gravity.distance_to_good(self.ai_ty.bagua):.0%}")
        lines.append(f"因果: 状态={self.causal.causal_state} 张力={self.causal.causal_tension:.3f}")
        lines.append(f"用户脊骨: {self.user_spine.dominant()}主导")
        lines.append(f"AI脊骨:   {self.ai_spine.dominant()}主导")
        return '\n'.join(lines)


if __name__ == '__main__':
    lx = LingxiCore()
    inputs = ['离', '坎', '离', '坤', '乾', '兑', '坎', '坤', '离', '离']
    for i, inp in enumerate(inputs):
        r = lx.receive(inp)
        print(f"[{i}] 桥:{inp}({BAGUA[inp]['mood']}) → {r}")
    print(f"\n{lx.report()}")
