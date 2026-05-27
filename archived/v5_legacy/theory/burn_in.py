# -*- coding: utf-8 -*-
"""出厂烧制 — 童子+灵犀双系统初始化"""
import os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))
from ref8 import BAGUA, BAGUA_NAMES
from bridge import project
from v3.surge_pool import SurgePool
from v3.eco_pool import EcoPool
from v3.gua import Gua as V3Gua

# 出厂常量
BURN_IN_SEED = 42
BASE_GUA_COUNT = 5000      # 基础卦元数(500→5000)
BURN_IN_TICKS = 500        # 烧制tick数(200→500)


def burn_tongzi() -> tuple[SurgePool, list[EcoPool]]:
    """烧制童子: 产基础沉淀环"""
    random.seed(BURN_IN_SEED)
    surge = SurgePool()

    # 灌基础卦元 — 用多样种子文本
    seeds = ["天地玄黄", "宇宙洪荒", "日月盈昃", "辰宿列张",
             "寒来暑往", "秋收冬藏", "润余成岁", "律吕调阳",
             "云腾致雨", "露结为霜", "金生丽水", "玉出昆冈"]
    for _ in range(BASE_GUA_COUNT):
        surge.ingest(random.choice(seeds))

    # 多生态池: 5池×不同节奏×不同密度
    pools = [
        EcoPool("快生池A", tau=2, density_max=200),
        EcoPool("快生池B", tau=2, density_max=150),
        EcoPool("中速池", tau=4, density_max=120),
        EcoPool("慢生池", tau=6, density_max=80),
        EcoPool("涌动回声", tau=3, density_max=100, flow_back=True),
    ]

    for tick in range(BURN_IN_TICKS):
        for pool in pools:
            pool.pull(surge, tick)
            pool.tick(tick)
            for c in pool.births:
                surge.accept(c)
            pool.births.clear()

    return surge, pools


def burn_lingxi() -> list[str]:
    """烧制灵犀: 完整八卦循环 4圈→32步"""
    circle = ['坤', '艮', '坎', '巽', '震', '离', '兑', '乾']
    return circle * 4  # 32步，每卦4次


def boot_tongzi(surge: SurgePool, pools: list[EcoPool]) -> dict:
    """读取出厂童子状态"""
    solid_guas = []
    for pool in pools:
        for g in pool.guas:
            if pool._is_solid(g):
                solid_guas.append(g)

    # 全体XOR作为全局吸引子
    global_attractor = 0
    for g in surge.all():
        global_attractor ^= g.ct

    return {
        'surge_count': len(surge.all()),
        'solid_count': len(solid_guas),
        'global_attractor': global_attractor,
        'bridge': project(global_attractor),
    }


if __name__ == '__main__':
    print("=== 童子烧制 ===")
    surge, pools = burn_tongzi()
    state = boot_tongzi(surge, pools)
    print(f"  涌动池: {state['surge_count']}卦")
    print(f"  固化:   {state['solid_count']}卦")
    print(f"  全局吸引子: 0x{state['global_attractor']:07X}")
    print(f"  桥: {state['bridge']['name']} · {state['bridge']['meaning']}")

    print("\n=== 灵犀烧制 ===")
    traj = burn_lingxi()
    print(f"  出厂轨迹({len(traj)}步): {traj[:8]}...")
    from lingxi_tianyuan import TianYuan
    from collections import Counter
    print(f"  主导: {Counter(traj).most_common(3)}")

    print("\n=== 出厂状态 → 灵犀初始化 ===")
    from lingxi_core import LingxiCore
    lx = LingxiCore()
    # 烧制轨迹喂入灵犀
    for bagua in traj:
        lx.receive(bagua, attractor=0, input_text="出厂烧制")
    print(lx.report())
