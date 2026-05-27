# -*- coding: utf-8 -*-
"""货柜 — 三卦元组装 + 灵犀全层融合"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from guayuan import MASK28, gua_hash


class GuaPacket:
    """货柜: body·ghost·ctx 三卦元"""

    def __init__(self, body: int = 0):
        self.body = body & MASK28          # 实数层
        self.ghost = body & MASK28          # 虚数层
        self.ctx = 0                        # 上下文层
        self.prev_body = 0

    def update(self, new_body: int, src_text: str = "", tgt_text: str = ""):
        """新输入 → 更新货柜"""
        self.prev_body = self.body
        self.body = new_body & MASK28
        self.ghost ^= (self.body ^ self.prev_body) & MASK28
        if src_text:
            self.ctx ^= gua_hash(src_text)
        if tgt_text:
            self.ctx ^= gua_hash(tgt_text)

    def all(self) -> tuple:
        return (self.body, self.ghost, self.ctx)

    def inject_ghost(self, gua: int):
        """YongJiu补全信息注入虚数层"""
        self.ghost ^= gua & MASK28


class LingxiFusion:
    """灵犀全层融合: L1→L2→Φ→L3→定心→YongJiu→货柜"""

    def __init__(self, l1_capacity: int = 128, l2_capacity: int = 1024):
        from l1_yinyang import YinYangPool
        from l2_world import WorldPool
        from l4_phi import PhiField
        from l3_bagua import BaguaRing
        from l5_dingxin_yongjiu import DingXinZhuizi, YongJiu

        self.l1 = YinYangPool(l1_capacity)
        self.l2 = WorldPool(l2_capacity)
        self.phi = PhiField()
        self.l3 = BaguaRing()
        self.dxz = DingXinZhuizi()
        self.yj = YongJiu()
        self.packet = GuaPacket()
        self.tick = 0
        self.history: list[dict] = []

    def receive(self, attractor: int, text: str = "") -> dict:
        """
        全链路一帧:
          attractor(童子产出) → L1→L2→Φ→L3→定心→YongJiu→货柜
        返回: 全层状态
        """
        self.tick += 1
        has_input = (len(text) > 0)

        # ── L1 阴阳 ──
        yin_inject = self.l1.tick_once()

        # ── L2 世界 ──
        l2_state = self.l2.tick_once(yin_inject=yin_inject,
                                     has_input=has_input)

        # ── Φ场 脉络 ──
        active_guas = self.l2.get_active_guas()
        if has_input and len(active_guas) >= 2:
            # 共同激活: 货柜body卦元与激活卦元的组合
            pairs = [(self.packet.body, g) for g in active_guas[:8]]
            self.phi.reinforce(pairs)
        self.phi.decay()

        # 脉络查询: 从attractor出发
        phi_ctx = self.phi.query_path(attractor, max_hops=2)

        # ── L3 八卦 ──
        if self.tick == 1:
            self.l3.set_from_attractor(attractor)
        l3_state = self.l3.tick_once(phi_ctx=phi_ctx, attractor=attractor)

        # ── 定心坠子 ──
        level, _ = self.dxz.align(self.l3.active_gua)
        if has_input:
            self.dxz.update_user(attractor)

        # ── YongJiu ──
        yj_state = self.yj.tick_once(attractor, self.l2.pool)

        # YongJiu补全
        if yj_state['completion']:
            self.packet.inject_ghost(yj_state['completion'])
            self.l3.force_jump(yj_state['completion'])

        # ── 货柜更新 ──
        self.packet.update(self.l3.active_gua, src_text=text)

        state = {
            'tick': self.tick,
            'l1_coherence': self.l1.coherence(),
            'l1_bias': self.l1.bias(),
            'l2_active': l2_state['active'],
            'l2_flowing': l2_state['flowing'],
            'l2_dormant': l2_state['dormant'],
            'l2_dreaming': l2_state['dreaming'],
            'phi_size': self.phi.size(),
            'phi_total_w': self.phi.total_weight(),
            'l3_hex': l3_state['name'],
            'l3_trigram': l3_state['trigram'],
            'l3_lightning': l3_state['lightning'],
            'dxz_level': level,
            'dxz_user': hex(self.dxz.user_tianyuan),
            'yj_split': yj_state['split'],
            'yj_L': yj_state['L'],
            'yj_triggered': yj_state['triggered'],
            'yj_quench': yj_state['quench'],
            'packet_body': hex(self.packet.body),
            'packet_ghost': hex(self.packet.ghost),
        }
        self.history.append(state)
        return state

    def report(self) -> str:
        """系统报告"""
        if not self.history:
            return "无历史"
        s = self.history[-1]
        return (
            f"t={s['tick']} | L1:{s['l1_bias']}({s['l1_coherence']:.2f}) "
            f"L2:活{s['l2_active']}流{s['l2_flowing']}眠{s['l2_dormant']}"
            f"{'💤' if s['l2_dreaming'] else ''} "
            f"| Φ:{s['phi_size']}连 "
            f"| L3:{s['l3_hex']}({s['l3_trigram']}) "
            f"| 定心:{s['dxz_level']} "
            f"| YJ:s={s['yj_split']} L={s['yj_L']:.2f}"
            f"{'🔥' if s['yj_triggered'] else ''}"
            f"{'❄️' if s['yj_quench'] else ''}"
        )


if __name__ == '__main__':
    lx = LingxiFusion(l1_capacity=64, l2_capacity=128)
    print("灵犀全层融合就绪\n")

    attractors = [0x1234567, 0x89ABCDE, 0xFEDCBA98765 & MASK28]
    for i, a in enumerate(attractors):
        st = lx.receive(a, text=f"输入{i+1}")
        print(f"[{i+1}] {lx.report()}")
