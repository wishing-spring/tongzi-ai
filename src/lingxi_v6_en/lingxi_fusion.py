# -*- coding: utf-8 -*-
"""Container — Three-GuaYuan assembly + Lingxi full-layer fusion"""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from guayuan import MASK28, gua_hash


class GuaPacket:
    """Container: body · ghost · ctx three-gua packet"""

    def __init__(self, body: int = 0):
        self.body = body & MASK28
        self.ghost = body & MASK28
        self.ctx = 0
        self.prev_body = 0

    def update(self, new_body: int, src_text: str = "", tgt_text: str = ""):
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
        """YongJiu completion injection → ghost layer"""
        self.ghost ^= gua & MASK28


class LingxiFusion:
    """Full-layer fusion: L1→L2→Φ→L3→DingXin→YongJiu→Container"""

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
        """Full-pipeline frame: attractor → L1→L2→Φ→L3→DingXin→YongJiu→Container"""
        self.tick += 1
        has_input = (len(text) > 0)

        yin_inject = self.l1.tick_once()
        l2_state = self.l2.tick_once(yin_inject=yin_inject, has_input=has_input)

        active_guas = self.l2.get_active_guas()
        if has_input and len(active_guas) >= 2:
            pairs = [(self.packet.body, g) for g in active_guas[:8]]
            self.phi.reinforce(pairs)
        self.phi.decay()

        phi_ctx = self.phi.query_path(attractor, max_hops=2)

        if self.tick == 1:
            self.l3.set_from_attractor(attractor)
        l3_state = self.l3.tick_once(phi_ctx=phi_ctx, attractor=attractor)

        level, _ = self.dxz.align(self.l3.active_gua)
        if has_input:
            self.dxz.update_user(attractor)

        yj_state = self.yj.tick_once(attractor, self.l2.pool)
        if yj_state['completion']:
            self.packet.inject_ghost(yj_state['completion'])
            self.l3.force_jump(yj_state['completion'])

        self.packet.update(self.l3.active_gua, src_text=text)

        state = {
            'tick': self.tick,
            'l1_coherence': self.l1.coherence(), 'l1_bias': self.l1.bias(),
            'l2_active': l2_state['active'], 'l2_flowing': l2_state['flowing'],
            'l2_dormant': l2_state['dormant'], 'l2_dreaming': l2_state['dreaming'],
            'phi_size': self.phi.size(), 'phi_total_w': self.phi.total_weight(),
            'l3_hex': l3_state['name'], 'l3_trigram': l3_state['trigram'],
            'l3_lightning': l3_state['lightning'],
            'dxz_level': level, 'dxz_user': hex(self.dxz.user_tianyuan),
            'yj_split': yj_state['split'], 'yj_L': yj_state['L'],
            'yj_triggered': yj_state['triggered'], 'yj_quench': yj_state['quench'],
            'packet_body': hex(self.packet.body), 'packet_ghost': hex(self.packet.ghost),
        }
        self.history.append(state)
        return state

    def report(self) -> str:
        if not self.history:
            return "no history"
        s = self.history[-1]
        return (
            f"t={s['tick']} | L1:{s['l1_bias']}({s['l1_coherence']:.2f}) "
            f"L2:a{s['l2_active']}f{s['l2_flowing']}d{s['l2_dormant']}"
            f"{'💤' if s['l2_dreaming'] else ''} "
            f"| Φ:{s['phi_size']}c "
            f"| L3:{s['l3_hex']}({s['l3_trigram']}) "
            f"| DX:{s['dxz_level']} "
            f"| YJ:s={s['yj_split']} L={s['yj_L']:.2f}"
            f"{'🔥' if s['yj_triggered'] else ''}"
            f"{'❄️' if s['yj_quench'] else ''}"
        )


# ── Persistence (monkey-patched) ──
def save_fusion(self, path: str):
    state = {
        'tick': self.tick,
        'l1_yin': self.l1.yin, 'l1_yang': self.l1.yang, 'l1_tick': self.l1.tick,
        'l2_pool': self.l2.pool, 'l2_tick': self.l2.tick, 'l2_idle': self.l2.idle_ticks,
        'phi_conn': {f"{a},{b}": w for (a,b), w in self.phi.connections.items()},
        'phi_last': {f"{a},{b}": t for (a,b), t in self.phi._last_active.items()},
        'phi_tick': self.phi.tick,
        'l3_idx': self.l3.active_idx, 'l3_gua': self.l3.active_gua,
        'l3_tick': self.l3.tick, 'l3_path': self.l3.lightning_path,
        'dxz_user': self.dxz.user_tianyuan, 'dxz_persona': self.dxz.ai_persona,
        'dxz_tick': self.dxz.tick,
        'yj_gua': self.yj.gua, 'yj_shallow': self.yj.shallow, 'yj_deep': self.yj.deep,
        'yj_tick': self.yj.tick, 'yj_trigger': self.yj.trigger_count,
        'packet_body': self.packet.body, 'packet_ghost': self.packet.ghost,
        'packet_ctx': self.packet.ctx, 'packet_prev': self.packet.prev_body,
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False)

def load_fusion(self, path: str):
    with open(path, 'r', encoding='utf-8') as f:
        state = json.load(f)
    self.tick = state['tick']
    self.l1.yin, self.l1.yang, self.l1.tick = state['l1_yin'], state['l1_yang'], state['l1_tick']
    self.l2.pool, self.l2.tick, self.l2.idle_ticks = state['l2_pool'], state['l2_tick'], state['l2_idle']
    self.phi.connections, self.phi._last_active = {}, {}
    for k, v in state['phi_conn'].items():
        a, b = k.split(',')
        self.phi.connections[(int(a), int(b))] = v
    for k, v in state['phi_last'].items():
        a, b = k.split(',')
        self.phi._last_active[(int(a), int(b))] = v
    self.phi.tick = state['phi_tick']
    self.l3.active_idx, self.l3.active_gua, self.l3.tick = state['l3_idx'], state['l3_gua'], state['l3_tick']
    self.l3.lightning_path = state['l3_path']
    self.dxz.user_tianyuan, self.dxz.ai_persona, self.dxz.tick = state['dxz_user'], state['dxz_persona'], state['dxz_tick']
    self.yj.gua, self.yj.shallow, self.yj.deep = state['yj_gua'], state['yj_shallow'], state['yj_deep']
    self.yj.tick, self.yj.trigger_count = state['yj_tick'], state['yj_trigger']
    self.packet.body, self.packet.ghost, self.packet.ctx = state['packet_body'], state['packet_ghost'], state['packet_ctx']
    self.packet.prev_body = state['packet_prev']

LingxiFusion.save = save_fusion
LingxiFusion.load = load_fusion


if __name__ == '__main__':
    lx = LingxiFusion(l1_capacity=64, l2_capacity=128)
    print("Lingxi full-layer fusion ready\n")
    attractors = [0x1234567, 0x89ABCDE, 0xFEDCBA98765 & MASK28]
    for i, a in enumerate(attractors):
        st = lx.receive(a, text=f"input{i+1}")
        print(f"[{i+1}] {lx.report()}")
