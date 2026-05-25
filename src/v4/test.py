# -*- coding: utf-8 -*-
"""灵悉 v4 · 对话测试 · 独立实例 + 新鲜加权"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from v4.v4 import LingxiV4
from v3.eco_pool import EcoPool
import v3.eco_pool as ep
ep.F0 = 32

def fresh_v4():
    v4 = LingxiV4()
    v4.add_pool(EcoPool("🔥快生", tau=3, fit_min=2, birth_rate=1.5, flow_back=True,
                         density_max=128, stagnation_window=2, jitter_bits=5))
    v4.add_pool(EcoPool("⚡涌动", tau=5, fit_min=2, birth_rate=1.2, flow_back=True,
                         density_max=96, stagnation_window=2, jitter_bits=5))
    return v4

# ═══ 连续对话(共享上下文) ═══
print("╔══════════════════════════════════════════════════╗")
print("║     灵 悉 v4  ·  连 续 对 话                     ║")
print("║     F₂身体×v4.3灵魂 · 卦象内化·文字输出           ║")
print("╚══════════════════════════════════════════════════╝\n")

v4 = fresh_v4()
conversation = [
    "你好",
    "今天天气真好",
    "我昨晚做了个梦梦见在飞",
    "那你害怕吗",
]

for text in conversation:
    reply, _ = v4.chat(text)
    print(f"  👤 {text}")
    print(f"  🤖 {reply}\n")

print("─── 连续对话后系统状态 ───")
print(v4.status())

# ═══ 独立暴力测试 ═══
print(f"\n╔══════════════════════════════════════════════════╗")
print(f"║     独 立 对 比 测 试                             ║")
print(f"╚══════════════════════════════════════════════════╝\n")

independent = [
    ("你好", "社交"),
    ("打死你滚开别碰我刀剑枪炮战争", "暴力"),
    ("我爱你一生一世永远在一起", "情感"),
    ("今天天气真好风轻云淡阳光灿烂", "自然"),
    ("今天吃了吗肚子饿了想吃饭", "日常"),
]

for text, label in independent:
    v4x = fresh_v4()
    reply, resp = v4x.chat(text)
    print(f"  [{label}] 👤 {text[:18]}...")
    print(f"          🤖 {reply}")
    print(f"          ⚙ 吸引子: {', '.join(resp.attractors[:4])}")
    print()
