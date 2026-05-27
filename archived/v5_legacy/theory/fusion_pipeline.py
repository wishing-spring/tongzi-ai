# -*- coding: utf-8 -*-
"""童灵融合管道 — 童子(F₂碰撞) ⊕ 灵犀(语义盘) 并行"""
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from encode import Encoder
from bridge import project
from lingxi_sim import LingxiSim
from v3.surge_pool import SurgePool
from v3.eco_pool import EcoPool
from v3.gua import Gua as V3Gua
from v3.constants import CT_MASK


def theory_gua_to_ct(g) -> int:
    """theory Gua(36bit) → v3 ct(28bit)"""
    bits = g.bits
    ct = 0
    start = max(0, len(bits) - 28)
    for b in bits[start:]:
        ct = (ct << 1) | b
    return ct & CT_MASK


class FusionPipeline:
    """童子 + 灵犀 并行管道"""

    def __init__(self):
        # ── 童子侧 ──
        self.encoder = Encoder()
        self.surge = SurgePool()
        self.eco = EcoPool("融合池", tau=3, density_max=200)

        # 出厂沉淀: 灌基础卦
        random.seed(42)
        for _ in range(200):
            self.surge.ingest("预装")

        self.tongzi_tick = 0
        self.last_attractor_ct = 0

        # ── 灵犀侧 ──
        self.lingxi = LingxiSim()

        # ── 对话日志 ──
        self.log = []

    def chat(self, text: str) -> str:
        """一轮对话: 输入→并行处理→输出"""
        self.tongzi_tick += 1

        # ═══ 童子 ═══
        # 编码（连环咬合）
        guas = self.encoder.encode(text)
        # 注入涌动弹窗
        for g in guas:
            ct = theory_gua_to_ct(g)
            char_gua = V3Gua(ct, is_native=True)
            self.surge.accept(char_gua)

        # 生态池 pull→碰撞→flowback
        for _ in range(3):  # 3 tick per message
            self.eco.pull(self.surge, self.tongzi_tick)
            self.eco.tick(self.tongzi_tick)
            for c in self.eco.births:
                self.surge.accept(c)
            self.eco.births.clear()

        # 取吸引子: 生态池固化卦XOR
        attractor = 0
        solid_count = 0
        for g in self.surge.all():
            attractor ^= g.ct
            solid_count += 1
        attractor &= CT_MASK
        self.last_attractor_ct = attractor

        # ═══ 桥 ═══
        bridge = project(attractor)

        # ═══ 灵犀 ═══
        self.lingxi.receive(bridge)
        response = self.lingxi.speak()

        # ═══ 日志 ═══
        entry = {
            'input': text,
            'tongzi_tick': self.tongzi_tick,
            'surge_stats': self.surge.stats(),
            'eco_stats': self.eco.stats(),
            'attractor': f"0x{attractor:07X}",
            'bridge_bagua': bridge['name'],
            'bridge_meaning': bridge['meaning'],
            'bridge_mood': bridge['mood'],
            'user_tianyuan': self.lingxi.user_tianyuan,
            'ai_tianyuan': self.lingxi.ai_tianyuan,
            'fold_dev': round(self.lingxi.fold_deviation, 3),
            'causal_tension': round(self.lingxi.causal_tension, 3),
            'response': response,
        }
        self.log.append(entry)
        return response

    def report(self) -> str:
        """完整对话报告"""
        lines = ["╔══════════════════════════════════════════════╗",
                 "║         童灵融合 · 对话报告                  ║",
                 "╚══════════════════════════════════════════════╝",
                 ""]
        for i, e in enumerate(self.log):
            lines.append(f"── 第{i+1}轮: \"{e['input']}\" ──")
            lines.append(f"  童子: 吸引子={e['attractor']}  {e['surge_stats'].strip()}")
            lines.append(f"        {e['eco_stats'].strip()}")
            lines.append(f"  桥:   {e['bridge_bagua']} · {e['bridge_meaning']} · {e['bridge_mood']}")
            lines.append(f"  灵犀: 用户天元={e['user_tianyuan']} AI天元={e['ai_tianyuan']}")
            lines.append(f"        折叠偏差={e['fold_dev']} 因果张力={e['causal_tension']}")
            lines.append(f"  回应: {e['response']}")
            lines.append("")

        # 最终状态
        lines.append("── 最终状态 ──")
        lines.append(f"  用户脊骨: {list(self.lingxi.user_spine)}")
        lines.append(f"  AI脊骨:   {list(self.lingxi.ai_spine)}")
        lines.append(f"  编码映射: {list(self.encoder._map.keys())}")
        return '\n'.join(lines)


# ── 测试 ──
if __name__ == '__main__':
    f = FusionPipeline()

    conversations = [
        "下雨了",
        "今天心情不好",
        "谢谢你陪我",
        "我想去远方",
        "什么是爱",
    ]

    for msg in conversations:
        resp = f.chat(msg)
        print(f"[{msg}] → {resp}")

    print(f"\n{f.report()}")
