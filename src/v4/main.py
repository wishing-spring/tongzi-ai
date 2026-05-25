# -*- coding: utf-8 -*-
"""灵悉 v4 · 交互对话入口"""

import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from v4.v4 import LingxiV4
from v3.eco_pool import EcoPool
import v3.eco_pool as ep
ep.F0 = 32

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
SAVE_PATH = os.path.join(DATA_DIR, 'lingxi_v4_state.json')

def init():
    """初始化或恢复灵悉"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    v4 = LingxiV4()
    v4.add_pool(EcoPool("🔥快生", tau=3, fit_min=2, birth_rate=1.5, flow_back=True,
                         density_max=128, stagnation_window=2, jitter_bits=5))
    v4.add_pool(EcoPool("⚡涌动", tau=5, fit_min=2, birth_rate=1.2, flow_back=True,
                         density_max=96, stagnation_window=2, jitter_bits=5))
    
    if os.path.exists(SAVE_PATH):
        if v4.load(SAVE_PATH):
            print(f"📂 从记忆恢复 (tick={v4.global_tick}, 脊骨用户{v4.user_spine.count}点)")
            return v4
    
    print("🌟 灵悉诞生。出厂天元已就位。")
    return v4

def main():
    v4 = init()
    print("输入 '状态' 看内部, '退出' 结束\n")
    
    while True:
        try:
            text = input("👤 ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        
        if not text:
            continue
        if text in ('退出', 'exit', 'quit'):
            v4.save(SAVE_PATH)
            print(f"💾 已保存到 {SAVE_PATH}")
            break
        if text == '状态':
            print(v4.status())
            print()
            continue
        
        reply, resp = v4.chat(text)
        print(f"🤖 {reply}")
        
        # 每5轮自动保存
        if v4.global_tick % 1000 == 0:
            v4.save(SAVE_PATH)

if __name__ == '__main__':
    main()
