# -*- coding: utf-8 -*-
"""Lingxi v6.0 Chat — Full Pipeline: Tongzi → Attractor → Lingxi 5 layers → WordWorld output"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from tongzi_f2 import TongziPool
from lingxi_fusion import LingxiFusion
from word_world import WordWorld
from tian_tian import TianTian


# ── Init ──
print("🌊 Lingxi v6.0 Chat — F₂ GuaYuan Ecosystem\nLoading...")

tz = TongziPool(surge_cap=512, eco_cap=64)
lx = LingxiFusion(l1_capacity=128, l2_capacity=1024)
ww = WordWorld()
lx.tongzi = tz
tt = TianTian(lx)

print(f"Ready — {len(ww.word_hashes)} words | L3: {lx.l3.current_hex_name()} | "
      f"Φ: {lx.phi.size()} connections\n")

# ── Burn-in ──
print("Factory burn-in (30 ticks)...")
burn_words = ["天地", "山水", "风云", "万物", "生息"]
for i in range(30):
    if i < 5:
        chain = tz.encode(burn_words[i])
        attr = tz.tick_once(inject_guas=chain)
    else:
        attr = tz.tick_once()
    lx.receive(attractor=attr)
    tt.tick_once()
print(f"Burn-in done — eco: {[len(p) for p in tz.eco]} solid: "
      f"{[sum(1 for d in p.values() if d['solid']) for p in tz.eco]}\n")


def chat(text: str) -> str:
    """Full pipeline: text → Tongzi → attractor → Lingxi 5 layers → F₂ output"""
    chain = tz.encode(text)
    attr = tz.tick_once(inject_guas=chain)
    st = lx.receive(attractor=attr, text=text)
    tt.tick_once()

    body = lx.packet.body
    ghost = lx.packet.ghost
    ctx = lx.packet.ctx
    active_guas = lx.l2.get_active_guas()

    body_words = ww.speak(body, active_guas)
    ghost_ctx = body ^ ghost ^ ctx
    gc_words = ww.speak(ghost_ctx & 0x0FFFFFFF, active_guas)

    meta = (f"[{st['l3_hex']}|{st['l3_trigram']}|{st['dxz_level']}|"
            f"YJ:{st['yj_L']:.2f}{'🔥' if st['yj_triggered'] else ''}]")

    return f"{meta} {body_words}"


# ── Main loop ──
print("Type to talk (type 'exit' to quit, 'state' for internal state)\n")

try:
    while True:
        text = input("You> ").strip()
        if not text:
            continue
        if text.lower() == 'exit':
            print("Goodbye.")
            break
        if text.lower() == 'state':
            print(f"  Tongzi: {tz.report()}")
            print(f"  Lingxi: {lx.report()}")
            print(f"  YJ: gua=0x{lx.yj.gua:07X} L={lx.yj.three_talents(lx.l2.pool):.3f} "
                  f"triggers={lx.yj.trigger_count}")
            print(f"  Φ: {lx.phi.size()}c total_w={lx.phi.total_weight()}")
            print(f"  TT: {tt.summary()}")
            continue

        response = chat(text)
        print(f"Lingxi> {response}")
except KeyboardInterrupt:
    print("\nGoodbye.")
