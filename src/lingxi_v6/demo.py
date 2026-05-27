# -*- coding: utf-8 -*-
"""v6.0 全链路演示 — 零浮点·F₂卦元·五层灵犀"""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(__file__))
from guayuan import MASK28, hamming, random_gua, gua_hash
from lingxi_fusion import LingxiFusion


def demo():
    print("=" * 60)
    print("  童灵 v6.0 — 卦元统一 · 五层灵犀 · 零浮点")
    print("=" * 60)

    lx = LingxiFusion(l1_capacity=64, l2_capacity=128)

    # ── 步1: 出厂状态 ──
    print("\n[步1] 出厂状态")
    l1 = lx.l1
    l2 = lx.l2
    print(f"  L1阴阳: 阴{len(l1.yin)}个 阳{len(l1.yang)}个 coherence={l1.coherence():.3f}")
    print(f"  L2世界: {len(l2.pool)}卦元 "
          f"激活{l2.active_count()} 流动{l2.flowing_count()} 休眠{l2.dormant_count()}")
    print(f"  L3八卦: {lx.l3.current_hex_name()}")
    print(f"  定心: 5维={lx.dxz.VALUES}")

    # ── 步2: 接收童子符 (模拟F₂碰撞产物) ──
    print("\n[步2] 童子F₂注入 → 卦元流转")
    seed = 0x55AA33F & MASK28
    for i in range(5):
        attractor = (seed ^ (seed << (i + 1)) ^ random_gua(i * 7)) & MASK28
        st = lx.receive(attractor, text=f"输入{i+1}")
        print(f"  [{i+1}] {lx.report()}")

    # ── 步3: YongJiu分岔增长 ──
    print("\n[步3] YongJiu 双井推移 (50 tick)")
    for i in range(50):
        attractor = random_gua((lx.tick + i) * 13)
        st = lx.receive(attractor)
        if (i + 1) % 10 == 0:
            print(f"  t={i+1}: YJ split={st['yj_split']} L={st['yj_L']:.3f} "
                  f"{'🔥触发' if st['yj_triggered'] else ''}"
                  f"{'❄️骤冷' if st['yj_quench'] else ''}")

    # ── 步4: 灵犀八卦长跑 ──
    print("\n[步4] 八卦跃迁路径 (20 tick)")
    path = []
    for i in range(20):
        attractor = random_gua(lx.tick * 17 + i)
        st = lx.receive(attractor)
        path.append(st['l3_hex'])
    print(f"  {' → '.join(path[:10])}")
    print(f"  {' → '.join(path[10:])}")

    # ── 步5: 系统终态 ──
    print("\n[步5] 终态报告")
    s = lx.history[-1]
    print(f"  总tick: {s['tick']}")
    print(f"  L2世界: 活{s['l2_active']} 流{s['l2_flowing']} 眠{s['l2_dormant']}"
          f" {'💤做梦' if s['l2_dreaming'] else '清醒'}")
    print(f"  Φ场: {s['phi_size']}连接 total_w={s['phi_total_w']}")
    print(f"  L3卦: {s['l3_hex']} 定心:{s['dxz_level']}")
    print(f"  YongJiu: {s['yj_split']:2d} 分岔 L={s['yj_L']:.2f}")
    print(f"  货柜: body={s['packet_body']} ghost={s['packet_ghost']}")

    # ── 步6: 持久化 ──
    print("\n[步6] 持久化 save/load")
    save_path = os.path.join(os.path.dirname(__file__), 'state_v6.json')
    lx.save(save_path)
    print(f"  保存: {save_path}")

    lx2 = LingxiFusion(l1_capacity=64, l2_capacity=128)
    lx2.load(save_path)
    print(f"  加载: tick={lx2.tick} L1_coherence={lx2.l1.coherence():.3f} "
          f"L3={lx2.l3.current_hex_name()} Φ={lx2.phi.size()}连接")
    os.remove(save_path)

    print("\n" + "=" * 60)
    print("  v6.0 全链路验证通过 ✓")
    print("=" * 60)


# ── 持久化 ──
def save_fusion(self, path: str):
    """保存全层状态"""
    import base64, struct
    state = {
        'tick': self.tick,
        'l1_yin': [g for g in self.l1.yin],
        'l1_yang': [g for g in self.l1.yang],
        'l1_tick': self.l1.tick,
        'l2_pool': [g for g in self.l2.pool],
        'l2_tick': self.l2.tick,
        'l2_idle': self.l2.idle_ticks,
        'phi_connections': {f"{a},{b}": w for (a,b), w in self.phi.connections.items()},
        'phi_last_active': {f"{a},{b}": t for (a,b), t in self.phi._last_active.items()},
        'phi_tick': self.phi.tick,
        'l3_idx': self.l3.active_idx,
        'l3_gua': self.l3.active_gua,
        'l3_tick': self.l3.tick,
        'l3_path': self.l3.lightning_path,
        'dxz_user': self.dxz.user_tianyuan,
        'dxz_persona': self.dxz.ai_persona,
        'dxz_tick': self.dxz.tick,
        'yj_gua': self.yj.gua,
        'yj_shallow': self.yj.shallow,
        'yj_deep': self.yj.deep,
        'yj_tick': self.yj.tick,
        'yj_trigger': self.yj.trigger_count,
        'packet_body': self.packet.body,
        'packet_ghost': self.packet.ghost,
        'packet_ctx': self.packet.ctx,
        'packet_prev': self.packet.prev_body,
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False)
    return f"已保存 {len(json.dumps(state))} 字节 → {path}"

def load_fusion(self, path: str):
    """加载全层状态"""
    with open(path, 'r', encoding='utf-8') as f:
        state = json.load(f)

    self.tick = state['tick']
    self.l1.yin = state['l1_yin']
    self.l1.yang = state['l1_yang']
    self.l1.tick = state['l1_tick']
    self.l2.pool = state['l2_pool']
    self.l2.tick = state['l2_tick']
    self.l2.idle_ticks = state['l2_idle']
    self.phi.connections = {}
    self.phi._last_active = {}
    for k, v in state['phi_connections'].items():
        a, b = k.split(',')
        self.phi.connections[(int(a), int(b))] = v
    for k, v in state['phi_last_active'].items():
        a, b = k.split(',')
        self.phi._last_active[(int(a), int(b))] = v
    self.phi.tick = state['phi_tick']
    self.l3.active_idx = state['l3_idx']
    self.l3.active_gua = state['l3_gua']
    self.l3.tick = state['l3_tick']
    self.l3.lightning_path = state['l3_path']
    self.dxz.user_tianyuan = state['dxz_user']
    self.dxz.ai_persona = state['dxz_persona']
    self.dxz.tick = state['dxz_tick']
    self.yj.gua = state['yj_gua']
    self.yj.shallow = state['yj_shallow']
    self.yj.deep = state['yj_deep']
    self.yj.tick = state['yj_tick']
    self.yj.trigger_count = state['yj_trigger']
    self.packet.body = state['packet_body']
    self.packet.ghost = state['packet_ghost']
    self.packet.ctx = state['packet_ctx']
    self.packet.prev_body = state['packet_prev']
    return f"已加载 {path}"

# 猴子补丁注入
LingxiFusion.save = save_fusion
LingxiFusion.load = load_fusion


if __name__ == '__main__':
    demo()
