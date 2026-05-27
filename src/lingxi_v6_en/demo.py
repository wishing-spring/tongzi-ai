# -*- coding: utf-8 -*-
"""Lingxi v6.0 Full-Link Demo — Tongzi + Lingxi → F₂ Ecosystem · zero-float · GuaYuan universal carrier"""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(__file__))

from tongzi_f2 import TongziPool
from lingxi_fusion import LingxiFusion
from word_world import WordWorld
from tian_tian import TianTian

SAVE_FILE = 'lingxi_v6_state.json'


def step1_init():
    """Step 1: Initialize — Tongzi + Lingxi + WordWorld + Heavenly Court"""
    print("=" * 60)
    print("STEP 1: Initialization — Tongzi F₂ · Lingxi 5 layers · WordWorld")
    print("=" * 60)

    tz = TongziPool(surge_cap=512, eco_cap=64)
    lx = LingxiFusion(l1_capacity=128, l2_capacity=1024)
    ww = WordWorld()

    # Wire Tongzi into Lingxi for Heavenly Court access
    lx.tongzi = tz
    tt = TianTian(lx)

    print(f"  Tongzi: surge={len(tz.surge)} eco={[len(p) for p in tz.eco]}")
    print(f"  Lingxi: L1 {len(lx.l1.yin)}/{len(lx.l1.yang)} L2 {len(lx.l2.pool)} Φ {lx.phi.size()} L3 {lx.l3.current_hex_name()}")
    print(f"  WordWorld: {len(ww.word_hashes)} words {len(ww.hash_words)} hashes")
    print(f"  Heavenly Court: 7 Heaven · 3 Earth departments\n")
    return tz, lx, ww, tt


def step2_inject(tz, lx, ww, tt):
    """Step 2: Text Injection — 3 rounds"""
    print("=" * 60)
    print("STEP 2: Text Injection — 'Heaven is deep','Earth is vast','Mountain streams flow'")
    print("=" * 60)

    texts = ["天高地厚深不可测", "大地广袤万物生", "山川河流奔涌不息"]
    for i, text in enumerate(texts):
        chain = tz.encode(text)
        attr = tz.tick_once(inject_guas=chain)
        st = lx.receive(attractor=attr, text=text)
        tt.tick_once()
        words = ww.speak(attr, lx.l2.get_active_guas())
        print(f"  [{i+1}] '{text[:8]}'")
        print(f"      attractor=0x{attr:07X} | L3={st['l3_hex']} | DX={st['dxz_level']} | YJ:L={st['yj_L']:.2f}")
        print(f"      F₂ output: {words}")
    print(f"  Tongzi: {tz.report()}\n")


def step3_burnin(tz, lx, ww, tt):
    """Step 3: Deep Factory Burn-in — 60 ticks"""
    print("=" * 60)
    print("STEP 3: Burn-in — 60 tick collision · anti-entropy · attractor drift")
    print("=" * 60)

    burn_guas = [tz.encode(f"burn_{i}")[0] for i in range(10)]
    for i in range(60):
        inject = burn_guas if i < 5 else None
        attr = tz.tick_once(inject_guas=inject)
        lx.receive(attractor=attr)
        tt.tick_once()
        if (i + 1) % 15 == 0:
            print(f"  t{i+1:>3}: {tz.report()}")

    print(f"\n  Final: {tz.report()}\n")


def step4_ecosystem(tz, lx, ww, tt):
    """Step 4: Eco-Pool Showcase — current state"""
    print("=" * 60)
    print("STEP 4: Ecosystem State — 4 eco-pools · solid rate · attractor")
    print("=" * 60)

    for i in range(4):
        pool = tz.eco[i]
        solid = sum(1 for d in pool.values() if d['solid'])
        print(f"  {'♠♥♦♣'[i]} Pool {i}: {len(pool)} gua solid={solid}"
              f" rate={solid/len(pool)*100:.0f}%"
              if len(pool) > 0 else f"  {'♠♥♦♣'[i]} Pool {i}: empty")

    print(f"\n  Attractor: 0x{tz.attractor:07X}")
    print(f"  L3 hex: {lx.l3.current_hex_name()} ({lx.l3.current_trigram()})")
    print(f"  YJ: split={lx.yj.shallow.bit_count()} L={lx.yj.three_talents(lx.l2.pool):.3f}")
    print(f"  Φ: {lx.phi.size()} connections\n")


def step5_speak(lx, ww, tt):
    """Step 5: Output Showcase — F₂ native output"""
    print("=" * 60)
    print("STEP 5: F₂ Output — XOR chain-jump word chain")
    print("=" * 60)

    bodies = [lx.packet.body, lx.packet.ghost, lx.packet.ctx]
    labels = ['Body', 'Ghost', 'Ctx']
    for label, gua in zip(labels, bodies):
        words = ww.speak(gua, lx.l2.get_active_guas())
        print(f"  {label}(0x{gua:07X}): {words}")

    # Heavenly Court status
    if len(tt.alerts) >= 5:
        print(f"\n  Heavenly Court recent alerts:")
        for a in tt.alerts[-5:]:
            print(f"    {a}")
    print()


def step6_save(tz, lx):
    """Step 6: Persistence"""
    print("=" * 60)
    print("STEP 6: Persistence — save/load")
    print("=" * 60)

    lx.save(SAVE_FILE)
    print(f"  Saved → {SAVE_FILE}")
    s = os.path.getsize(SAVE_FILE)
    print(f"  File size: {s} bytes")

    # Verify
    with open(SAVE_FILE, 'r') as f:
        data = json.load(f)
    print(f"  Verify: tick={data['tick']} keys={len(data)}")

    # Load
    lx2 = LingxiFusion(l1_capacity=128, l2_capacity=1024)
    before = lx2.report()
    lx2.load(SAVE_FILE)
    after = lx2.report()
    print(f"  Before load: {before}")
    print(f"  After  load: {after}")
    print(f"  ✅ Persistence OK\n")


def main():
    print("🌊 Lingxi v6.0 Full-Link Demo\n")

    tz, lx, ww, tt = step1_init()
    step2_inject(tz, lx, ww, tt)
    step3_burnin(tz, lx, ww, tt)
    step4_ecosystem(tz, lx, ww, tt)
    step5_speak(lx, ww, tt)
    step6_save(tz, lx)

    print("=" * 60)
    print("✅ Lingxi v6.0 Demo Complete")
    print(f"   YongJiu triggers: {lx.yj.trigger_count} | quench: {sum(1 for s in lx.history if s['yj_quench'])}")
    print(f"   Heavenly Court alerts: {len(tt.alerts)}")
    print(f"   Season: {['Spring','Summer','Autumn','Winter'][tt.season]}")
    print("=" * 60)


if __name__ == '__main__':
    start = time.time()
    main()
    print(f"\n⏱  Total time: {time.time() - start:.2f}s")
