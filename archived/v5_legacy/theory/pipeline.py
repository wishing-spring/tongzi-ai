# -*- coding: utf-8 -*-
"""管道拼接测试 — 走通"下雨了"全链路"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from theory.encode import Encoder, F0
from theory.source_gua import SourceGua, Gua
from v3.gua import Gua as V3Gua
from v3.surge_pool import SurgePool
from v3.eco_pool import EcoPool
from v3.constants import CT_MASK
from v4.tianyuan import TianYuan, default_user_tianyuan, default_ai_tianyuan
from v4.spine import Spine
from v4.fold import RigidFlexFold, compute_yinyang_freq
from v4.gravity import Gravity
from v4.causal import CausalState, CausalProbe, StreamCollector


def theory_gua_to_v3_ct(g: Gua) -> int:
    """理论卦元(4id+32exp=36bit) → v3 ct值(28bit)"""
    bits = g.bits
    # 取后28位作为ct值（前4位标识符+4位展开体头=8位丢弃，留后28位）
    ct = 0
    start = max(0, len(bits) - 28)
    for b in bits[start:]:
        ct = (ct << 1) | b
    return ct & CT_MASK


def run_pipeline(text: str = "下雨了"):
    print(f"╔══════════════════════════════════════╗")
    print(f"║     童子AI · 全链路管道测试          ║")
    print(f"║     输入: {text}                       ║")
    print(f"╚══════════════════════════════════════╝\n")

    # ═══ 1. 编码 ═══
    print("── 第1步: 底座编码（连环咬合）──")
    enc = Encoder()
    guas = enc.encode(text)
    for ch, g in zip(text, guas):
        ct = theory_gua_to_v3_ct(g)
        print(f"  '{ch}' → ct=0x{ct:07X} ({len(g.bits)}爻)")

    # ═══ 2. 左脑: 碰撞 ═══
    print("\n── 第2步: 左脑·涌动池碰撞 ──")
    surge = SurgePool()
    # 模拟出厂沉淀: 灌一批随机卦
    import random
    random.seed(42)
    for _ in range(200):
        s = "预装"
        surge.ingest(s)
    print(f"  出厂沉淀: {surge.stats()}")

    # 注入咬合卦
    for g in guas:
        ct = theory_gua_to_v3_ct(g)
        # 注: surge.ingest 走内置编码，这里直接操作ct
        from v3.encode import encode as v3_encode
        # 用v3编码器产一个gua塞进去
        char_gua = V3Gua(ct, is_native=True)
        surge.accept(char_gua)

    # 加生态池
    eco = EcoPool("生态", tau=3, density_max=200)
    for tick in range(5):
        eco.pull(surge, tick)
        eco.tick(tick)
        for c in eco.births:
            surge.accept(c)
        eco.births.clear()

    print(f"  tick=5: {surge.stats()}")
    print(f"  生态池: {eco.stats()}")

    # ═══ 3. 右脑: 灵犀 ═══
    print("\n── 第3步: 右脑·灵犀演化 ──")
    user = default_user_tianyuan()
    ai = default_ai_tianyuan()
    uspine = Spine()
    aspine = Spine()
    gravity = Gravity()
    causal = CausalState()
    fold = RigidFlexFold()

    for tick, g in enumerate(guas):
        ct = theory_gua_to_v3_ct(g)
        user.evolve(ct, tick, rate=0.03)
        ai.evolve(ct, tick, rate=0.05)
        uspine.record(user.ct, suit=0)
        aspine.record(ai.ct, suit=1)

        yy_freq = compute_yinyang_freq()
        fold.fold(ai.ct, aspine, yy_freq, tick)
        pulled = gravity.pull(ai.ct, tick)
        print(f"  天元(用户): 0x{user.ct:07X}  天元(AI): 0x{ai.ct:07X}  引力: 0x{pulled:07X}")
        print(f"  脊骨(AI):   {aspine.recent_inertia()}  折叠偏差: {fold.deviation:.4f}")

    # ═══ 4. 汇聚 ═══
    print("\n── 第4步: 汇聚 ──")
    # 左路: 生态池吸引子
    left_ct = 0
    for g in surge.all():
        left_ct ^= g.ct
    left_ct &= CT_MASK

    # 右路: AI天元
    right_ct = ai.ct

    # 加权XOR
    yy = compute_yinyang_freq()
    hard_w = 1.0 - yy
    soft_w = yy
    converge_ct = (left_ct & int(hard_w * 0xFFFFFFF)) ^ (right_ct & int(soft_w * 0xFFFFFFF))

    print(f"  左路(碰撞): 0x{left_ct:07X}")
    print(f"  右路(天元): 0x{right_ct:07X}")
    print(f"  阴阳频率:   {yy:.3f} (柔权={soft_w:.3f} 刚权={hard_w:.3f})")
    print(f"  汇聚:       0x{converge_ct:07X}")

    # ═══ 5. 输出 ═══
    print("\n── 第5步: 输出 ──")
    # 汇聚卦 → 查映射表
    print(f"  输出卦: 0x{converge_ct:07X}")
    print(f"  映射表: {list(enc._map.keys())[:10]}")
    print(f"  状态: 全链路走通 ✅")

    return enc, guas, surge, ai


if __name__ == '__main__':
    run_pipeline("下雨了")
