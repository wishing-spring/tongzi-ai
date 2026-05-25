# -*- coding: utf-8 -*-
"""V4 interactive shell."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from v4.v4 import LingxiV4
from v3.eco_pool import EcoPool
import v3.eco_pool as ep
ep.F0 = 32

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
SAVE_PATH = os.path.join(DATA_DIR, 'lingxi_v4_state.json')


def init():
    os.makedirs(DATA_DIR, exist_ok=True)
    v4 = LingxiV4()
    v4.add_pool(EcoPool("fast", tau=3, fit_min=2, birth_rate=1.5, flow_back=True,
                         density_max=128, stagnation_window=2, jitter_bits=5))
    v4.add_pool(EcoPool("surge", tau=5, fit_min=2, birth_rate=1.2, flow_back=True,
                         density_max=96, stagnation_window=2, jitter_bits=5))

    if os.path.exists(SAVE_PATH):
        if v4.load(SAVE_PATH):
            print(f"[loaded] tick={v4.global_tick}, user spine={v4.user_spine.count} pts")
            return v4
    print("[born] fresh tianyuan online.")
    return v4


def main():
    v4 = init()
    print("type 'status' for internals, 'quit' to exit\n")
    while True:
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not text:
            continue
        if text in ('quit', 'exit'):
            v4.save(SAVE_PATH)
            print(f"[saved] {SAVE_PATH}")
            break
        if text == 'status':
            print(v4.status())
            print()
            continue
        reply, _ = v4.chat(text)
        print(reply)


if __name__ == '__main__':
    main()
