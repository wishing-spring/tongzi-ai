# -*- coding: utf-8 -*-
"""童灵融合 · 最终管道 — 童子⊕灵犀 并行运行 + 持久化"""
import os, sys, random, json
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))

from encode import Encoder
from bridge import project
from ref8 import BAGUA, BAGUA_NAMES
from lingxi_core import LingxiCore
from burn_in import burn_tongzi, burn_lingxi
from lingxi_native import NativeSpeaker
from v3.surge_pool import SurgePool
from v3.eco_pool import EcoPool
from v3.gua import Gua as V3Gua
from v3.constants import CT_MASK


def theory_gua_to_ct(g) -> int:
    """theory Gua(4id+28exp=32bit) → v3 ct(28bit) — 直接取展开体"""
    bits = g.bits
    ct = 0
    # 取后28位（跳过4位标识符）
    for b in bits[-28:]:
        ct = (ct << 1) | b
    return ct & CT_MASK


class TongLing:
    """童灵融合系统"""

    def __init__(self, native: bool = False):
        # ═══ 出厂烧制 ═══
        print("烧制童子...")
        self.surge, self.eco_pools = burn_tongzi()
        print("烧制灵犀...")
        self.lingxi = LingxiCore()
        traj = burn_lingxi()
        for bagua in traj:
            self.lingxi.receive(bagua, attractor=0, input_text="出厂")

        # ═══ 运行时状态 ═══
        self.encoder = Encoder()
        self.tick = 0
        self.log = []
        self.native = native
        if native:
            self.native_speaker = NativeSpeaker()

        print(f"童灵融合就绪: 童子{len(self.surge.all())}卦, "
              f"灵犀AI={self.lingxi.ai_ty.bagua}"
              + (" [原生模式]" if native else ""))

    def chat(self, text: str) -> str:
        """一轮对话"""
        self.tick += 1

        # ═══ 童子 ═══
        guas = self.encoder.encode(text)
        for g in guas:
            ct = theory_gua_to_ct(g)
            self.surge.accept(V3Gua(ct, is_native=True))

        # 生态池碰撞
        for _ in range(3):
            for pool in self.eco_pools:
                pool.pull(self.surge, self.tick)
                pool.tick(self.tick)
                for c in pool.births:
                    self.surge.accept(c)
                pool.births.clear()

        # 全局吸引子
        attractor = 0
        for g in self.surge.all():
            attractor ^= g.ct
        attractor &= CT_MASK

        # ═══ 桥 ═══
        bridge = project(attractor)

        # ═══ 灵犀 (传入吸引子) ═══
        if self.native:
            response = self.native_speaker.speak(attractor, bridge['name'], text)
        else:
            response = self.lingxi.receive(bridge['name'],
                                           attractor=attractor,
                                           input_text=text)

        # ═══ 日志 ═══
        self.log.append({
            'tick': self.tick,
            'input': text,
            'attractor': f"0x{attractor:07X}",
            'bridge': bridge['name'],
            'bridge_meaning': bridge['meaning'],
            'bridge_mood': bridge['mood'],
            'user_ty': self.lingxi.user_ty.bagua,
            'ai_ty': self.lingxi.ai_ty.bagua,
            'fold_dev': round(self.lingxi.fold.deviation, 3),
            'causal_tension': round(self.lingxi.causal.causal_tension, 3),
            'response': response,
        })

        return response

    def report(self) -> str:
        """完整报告"""
        lines = ["╔══════════════════════════════════════════════╗",
                 "║           童灵融合 · 对话报告                ║",
                 "╚══════════════════════════════════════════════╝"]
        for i, e in enumerate(self.log):
            lines.append(f"\n── 第{i+1}轮: \"{e['input']}\" ──")
            lines.append(f"  童子吸引子: {e['attractor']}")
            lines.append(f"  桥: {e['bridge']} · {e['bridge_meaning']} · {e['bridge_mood']}")
            lines.append(f"  灵犀: 用户@{e['user_ty']} AI@{e['ai_ty']} "
                         f"折叠={e['fold_dev']} 张力={e['causal_tension']}")
            lines.append(f"  回应: {e['response']}")

        lines.append(f"\n── 最终状态 ──")
        lines.append(self.lingxi.report())
        return '\n'.join(lines)

    # ═══ 持久化 ═══
    def save(self, path: str = None):
        """保存全态到文件"""
        if path is None:
            path = f"tongling_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tl"
        state = {
            'tick': self.tick,
            'version': '5.0',
            # 童子: 涌动池所有卦ct
            'surge_guas': [{'ct': g.ct, 'native': getattr(g, 'is_native', False)}
                          for g in self.surge.all()],
            # 生态池: 卦状态
            'eco_pools': [],
            # 灵犀: 天元+因果
            'lingxi': {
                'user_bagua': self.lingxi.user_ty.bagua,
                'user_offset': self.lingxi.user_ty.offset,
                'ai_bagua': self.lingxi.ai_ty.bagua,
                'ai_offset': self.lingxi.ai_ty.offset,
                'ai_momentum_dir': self.lingxi.ai_ty.momentum_dir,
                'ai_momentum_strength': self.lingxi.ai_ty.momentum_strength,
                'causal_state': self.lingxi.causal.causal_state,
                'causal_tension': self.lingxi.causal.causal_tension,
                'fold_deviation': self.lingxi.fold.deviation,
                'fold_past': self.lingxi.fold.past_rigid,
                'fold_flex': self.lingxi.fold.future_flex,
                'fold_generated': self.lingxi.fold.generated_now,
            },
            'log': self.log,
        }
        # 原生模式: 记忆状态
        if self.native:
            state['native'] = {
                'memory_seed': self.native_speaker.memory_seed,
                'recent': [hex(x) for x in self.native_speaker.recent],
                'total_rounds': self.native_speaker.total_rounds,
            }
        # 生态池状态
        for pool in self.eco_pools:
            pool_state = {'name': pool.name, 'tau': pool.tau,
                         'density_max': pool.density_max,
                         'guas': []}
            for g in pool.guas:
                pool_state['guas'].append({
                    'ct': g.ct, 'energy': pool._energy.get(id(g), 0),
                    'hit': pool._hits.get(id(g), 0),
                    'solid': id(g) in pool._solid,
                })
            state['eco_pools'].append(pool_state)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        print(f"已保存: {path} ({len(state['surge_guas'])}卦, "
              f"{len(self.log)}轮对话)")
        return path

    @classmethod
    def load(cls, path: str):
        """从文件恢复全态"""
        with open(path, 'r', encoding='utf-8') as f:
            state = json.load(f)

        tl = cls.__new__(cls)
        tl.encoder = Encoder()
        tl.tick = state['tick']
        tl.log = state['log']

        # 恢复童子
        tl.surge = SurgePool()
        for gd in state['surge_guas']:
            g = V3Gua(gd['ct'], is_native=gd.get('native', False))
            tl.surge._ingest_raw(g)

        tl.eco_pools = []
        for ps in state['eco_pools']:
            pool = EcoPool(ps['name'], tau=ps['tau'],
                          density_max=ps['density_max'])
            for gd in ps['guas']:
                g = V3Gua(gd['ct'])
                pool._ingest_raw(g, gd['energy'], gd['hit'], gd['solid'])
            tl.eco_pools.append(pool)

        # 恢复灵犀
        lx = LingxiCore.__new__(LingxiCore)
        lx.plate = LingxiCore().plate  # 新盘
        from lingxi_tianyuan import TianYuan, Spine
        from lingxi_dynamics import RigidFlexFold, Gravity, CausalChain
        from lingxi_output import LingxiSpeaker

        ls = state['lingxi']
        lx.user_ty = TianYuan(ls['user_bagua'])
        lx.user_ty.offset = ls['user_offset']
        lx.ai_ty = TianYuan(ls['ai_bagua'])
        lx.ai_ty.offset = ls['ai_offset']
        lx.ai_ty.momentum_dir = ls.get('ai_momentum_dir', 0)
        lx.ai_ty.momentum_strength = ls.get('ai_momentum_strength', 0.0)
        lx.user_spine = Spine()
        lx.ai_spine = Spine()
        lx.fold = RigidFlexFold()
        lx.fold.past_rigid = ls.get('fold_past', '坤')
        lx.fold.future_flex = ls.get('fold_flex', '坤')
        lx.fold.generated_now = ls.get('fold_generated', '坤')
        lx.fold.deviation = ls.get('fold_deviation', 0.0)
        lx.gravity = Gravity(0.7)
        lx.causal = CausalChain()
        lx.causal.causal_state = ls['causal_state']
        lx.causal.causal_tension = ls['causal_tension']
        lx.speaker = LingxiSpeaker(lx.plate)
        lx.tick = tl.tick
        lx.history = []

        tl.lingxi = lx

        # 原生模式: 恢复记忆
        if 'native' in state:
            tl.native = True
            tl.native_speaker = NativeSpeaker()
            ns = state['native']
            tl.native_speaker.memory_seed = ns['memory_seed']
            tl.native_speaker.recent = [int(x, 16) for x in ns['recent']]
            tl.native_speaker.total_rounds = ns['total_rounds']

        print(f"已加载: {path} ({len(state['surge_guas'])}卦, "
              f"{len(tl.log)}轮对话, AI={lx.ai_ty.bagua})")
        return tl


if __name__ == '__main__':
    tl = TongLing()

    conversations = [
        "下雨了",
        "今天心情不好",
        "谢谢你陪我",
        "我想去远方",
        "什么是爱",
        "我害怕失败",
        "明天会更好",
    ]

    for msg in conversations:
        resp = tl.chat(msg)
        print(f"\n>> {msg}")
        print(f"   {resp}")

    print(f"\n{tl.report()}")

    # 测试持久化
    path = tl.save("test_save.tl")
    tl2 = TongLing.load(path)
    print(f"\n恢复后对话:")
    r = tl2.chat("还记得我吗")
    print(f"   {r}")
