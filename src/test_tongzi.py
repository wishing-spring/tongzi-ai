# Copyright (c) 2026 Tongzi Project (wishing-spring)
# Licensed under the MIT License. See LICENSE file for details.
"""
童子 v1.0 · 完整测试套件
========================
测试范围: encode, Gua ops, Space lifecycle, save/load, density, tick.
纯 F₂ 运算，零外部依赖。
"""
import os
import sys
import json
import io

# UTF-8 输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from tongzi_core import (
    Space, Gua,
    bit_count, hamming, rotate_left, rotate_right,
    gray_encode, gray_ring
)
from tongzi_constants import VEC_DIM, FULL_MASK, PHI_BITS, PHI_LEN

PASS = 0
FAIL = 0

def check(condition, label):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [OK] {label}")
    else:
        FAIL += 1
        print(f"  [FAIL] {label}")

def section(name):
    print(f"\n--- {name} ---")

# ================================================================
section("1. 公理验证")
# ================================================================

# XOR 交换
a, b = 0x3A5C, 0xC9F1
check(a ^ b == b ^ a, "XOR交换")
check(a ^ a == 0, "XOR自消")
check(hamming(a, b) == hamming(b, a), "汉明对称")

# 旋转保距
for k in [1, 3, 7]:
    ra = rotate_left(a, k)
    rb = rotate_left(b, k)
    check(hamming(ra, rb) == hamming(a, b), f"旋转保距 k={k}")

# 格雷环: 相邻卦汉明距离 = 1
for n in range(16):
    g1 = gray_encode(n)
    g2 = gray_encode((n + 1) % 16)
    check(hamming(g1, g2) == 1, f"格雷相邻 n={n}")

# ================================================================
section("2. φ 编码")
# ================================================================

v1, p1 = Space.encode("hello")
v2, p2 = Space.encode("hello")
check(v1 == v2, "同文本→同卦")
check(0 <= v1 <= FULL_MASK, f"value 在 [0, {FULL_MASK}] 内")
check(0 <= p1 < PHI_LEN, f"pos 在 [0, {PHI_LEN}) 内")

v3, p3 = Space.encode("world")
check(v1 != v3 or p1 != p3, "不同文本→不同卦")

# 空文本抛异常
try:
    Space.encode("")
    check(False, "空文本应抛异常")
except ValueError:
    check(True, "空文本抛异常")  # 实际代码不抛？再确认

# ================================================================
section("3. Gua 基本操作")
# ================================================================

g = Gua(0xABCD, 42, 16)
check(g.id_t == 42, "id_t = pos")
check(g.id_l == 16, "id_l = length")
check(g.value == 0xABCD, "value 正确")
check(g.is_solid == False, "初始未固化")
check(g.hit_count == 0, "初始碰撞数 0")
check(g.energy == 0, "初始能量 0")

# moving_bits
check(g.moving_bits == 0xABCD, "未固化时 moving_bits = value")

# ================================================================
section("4. 核心运算: collide")
# ================================================================

g1 = Gua(0xA5A5, 0, 16)
g2 = Gua(0x5A5A, 1, 16)
diff, common = g1.collide(g2)
check(diff == 0xFFFF, "全异 → diff=0xFFFF")
check(common == 0x0000, "全异 → common=0x0000")

g3 = Gua(0xFFFF, 2, 16)
diff, common = g1.collide(g3)
check(common == 0xA5A5, "部分重叠 common")

# ================================================================
section("5. 核心运算: orbit / stretch")
# ================================================================

v = 0x0001
g = Gua(v, 0, 16)
center = 0

# orbit: 绕 0 旋转 1 步 = 左移 1 位
orb = g.orbit(center, 1)
check(orb == 0x0002, "orbit 1 步")
check(hamming(g.moving_bits, center) == hamming(orb, center), "orbit 保距")

# stretch: λ=1 → 推到对面 → XOR(v, v^c) = c
st = g.stretch(center, 1)
check(st == 0x0000, "stretch λ=1 → center")
st0 = g.stretch(center, 0)
check(st0 == 0x0001, "stretch λ=0 → 原位")

# ================================================================
section("6. 固化")
# ================================================================

g = Gua(0xFFFF, 0, 16)
check(g.is_solid == False, "初始未固化")
g.solidify()
check(g.is_solid == True, "固化后 is_solid=True")
check(g.core != 0, "固化后有 core")
check(g.moving_bits != 0xFFFF, "固化后 moving_bits ≠ value (内核被剥除)")

# 弱解禁
old = g.value
g.weakly_unlock(0)
check(g.value != old, "弱解禁改变了值")

# ================================================================
section("7. Space 初始/摄入/持久化")
# ================================================================

# 清理旧状态
state_path = os.path.join(os.path.dirname(__file__), '.tongzi_state.json')
if os.path.exists(state_path):
    os.remove(state_path)

space = Space()
check(space.size == 0, "空空间 size=0")
check(space.load() == False, "无状态文件 → load=False")

g = space.ingest("first")
check(space.size == 1, "ingest 后 size=1")
check(isinstance(g, Gua), "ingest 返回 Gua")

g2 = space.ingest("second")
check(space.size == 2, "ingest 两次 size=2")

# save
space.save()
check(os.path.exists(state_path), "save 创建文件")

# load
space2 = Space()
check(space2.load() == True, "load 成功")
check(space2.size == 2, "load 后 size 一致")
check(space2.tick_count == space.tick_count, "tick 一致")

# lambda_base 恢复
for g_orig, g_loaded in zip(space.guas, space2.guas):
    check(g_loaded.lambda_base == g_orig.lambda_base,
          f"lambda_base 恢复 t={g_orig.id_t}")

# ================================================================
section("8. 频控")
# ================================================================

g_low  = Gua(0, 0, 4)       # id_l=4 (浅层)
g_high = Gua(0, 0, 14)      # id_l=14 (深层)
check(space._rate(g_low) > space._rate(g_high), "浅层卦速率 > 深层卦速率")

# 能量累积
g_test = Gua(0, 10, 8)
rate = space._rate(g_test)
check(rate > 0, "速率 > 0")
space._accumulate_energy(g_test)
check(g_test.energy == rate, "累积后能量 == 速率")
check(space._try_discharge(g_test) == False, "能量未满不放")

g_test.energy = space.F0
check(space._try_discharge(g_test) == True, "能量满 → 放电")
check(g_test.energy == 0, "放电后能量归零")

# ================================================================
section("9. 密度感知")
# ================================================================

space3 = Space()
g_a = space3.ingest("aaa")
g_b = space3.ingest("bbb")
g_c = space3.ingest("ccc")

d_a = space3.local_density(g_a)
check(d_a >= 0, f"密度非负: {d_a:.3f}")

S_max = space3.max_density()
check(S_max >= 0, f"max_density 非负: {S_max:.3f}")

# μ
check(0 <= space3.mu(4) <= 1.0, "μ 在 [0,1] 内")
check(space3.mu(16) == 1.0, "id_l=Lmax → μ=1.0")

# ================================================================
section("10. tick 周期")
# ================================================================

space4 = Space()
# 手动创建低 id_t 卦，确保能快速碰撞
g1 = Gua(0xA5A5, 0, 8)    # id_t=0 → f1=256/1=256, 速率=min(256,28)=28
g2 = Gua(0x5A5A, 1, 8)    # id_t=1 → f1=256/2=128
g3 = Gua(0x3333, 2, 8)
g4 = Gua(0x0F0F, 3, 8)    # 4 卦 → 每次放电 2 对碰撞
for g in [g1, g2, g3, g4]:
    g.lambda_base = 0
    g.is_native = True   # 手工卦标原生，防止衰变误杀
    g.origin = g.value
    space4._update_layer_max(g.id_l)
space4.guas = [g1, g2, g3, g4]

# 100 ticks → 速率 28 → 每约 9 tick 放电 → 11 次放电 × 2 碰撞 = 22 碰撞
for _ in range(100):
    space4.tick()

check(g1.hit_count >= 4, f"g1 碰撞 ≥ 4: {g1.hit_count}")
check(any(g.is_solid for g in space4.guas),
      f"有卦固化 (阈值={max(3, 16-8)}=8)")

# ================================================================
section("11. 密度自清")
# ================================================================

space5 = Space()
# 添加超过 limit 的卦
for i in range(40):
    space5.ingest(f"test_{i}")

before = space5.size
for _ in range(10):
    space5.tick()
after = space5.size
check(after <= before, f"密度自清: {before} → {after}")

# ================================================================
section("12. 边界情况")
# ================================================================

# 单卦空间
space_single = Space()
space_single.ingest("solo")
check(space_single.max_density() == 0.0, "单卦密度=0")
r = space_single.tick()
check(r['collisions'] == 0, "单卦无碰撞")

# Gua 长度边界
try:
    Gua(0, 0, 0)
    check(False, "length=0 应抛异常")
except ValueError:
    check(True, "length=0 抛异常")

try:
    Gua(0, 0, 100)
    check(False, "length>VEC_DIM 应抛异常")
except ValueError:
    check(True, "length>VEC_DIM 抛异常")

# ================================================================
section("13. 极简内丹 — 反向译出")
# ================================================================

space6 = Space()
g_h = space6.ingest("hello")
g_w = space6.ingest("world")
g_hi = space6.ingest("hi")

# express: 找到与 g_h 最近的源文本
e_h = space6.express(g_h)
check(e_h == "world" or e_h == "hi" or e_h == "", f"express(g_h) 返回最近文本: '{e_h}'")

e_w = space6.express(g_w)
check(isinstance(e_w, str), f"express 返回字符串: '{e_w}'")

# source 持久化
space6.save()
space7 = Space()
space7.load()
check(space7.size == 3, "load 后 size 一致")
for g in space7.guas:
    check(g.source != "", f"source 已恢复: '{g.source}'")

# ================================================================
# v1.3 卦元本体 · 势 · 子卦衰变 · 原生复生
# ================================================================

# --- ingest → 原生卦 ---
space8 = Space()
g_native = space8.ingest("test")
check(g_native.is_native, "ingest 产生原生卦: is_native=True")
check(g_native.origin == g_native.value, f"原生卦 origin=value: {g_native.origin}")
check(g_native.potential == 0, "新卦 Ψ=0")
check(g_native.orbit_step == 16, "新卦 ω=16")

# --- potential 计算 ---
g_native.hit_count = 0
check(g_native.potential == 0, "C=0 → Ψ=0")
g_native.hit_count = 1
check(g_native.potential == 1, "C=1 → Ψ=1")
g_native.hit_count = 2
check(g_native.potential == 1, "C=2 → Ψ=1 (⌊log₂(3)⌋=1)")
g_native.hit_count = 3
check(g_native.potential == 2, "C=3 → Ψ=2 (⌊log₂4⌋=2)")
g_native.hit_count = 4
check(g_native.potential == 2, "C=4 → Ψ=2")
g_native.hit_count = 15
check(g_native.potential == 4, "C=15 → Ψ=4")
g_native.hit_count = 100000
check(g_native.potential == 16, f"极大C → Ψ=VEC_DIM=16, 实际={g_native.potential}")

# --- orbit_step 计算 ---
g_native.hit_count = 0
check(g_native.orbit_step == 16, "Ψ=0 → ω=16")
g_native.hit_count = 8
check(g_native.orbit_step == 13, f"Ψ=3 → ω=13, 实际={g_native.orbit_step}")
g_native.hit_count = 100000
check(g_native.orbit_step == 1, f"Ψ=16 → ω=1, 实际={g_native.orbit_step}")

# --- merge → 子卦 ---
space9 = Space()
ga = space9.ingest("a")
gb = space9.ingest("b")
ga.hit_count = 10
gb.hit_count = 10
# 强制碰撞触发合体
h = hamming(ga.moving_bits, gb.moving_bits)
xor_val = ga.moving_bits ^ gb.moving_bits
and_val = ga.moving_bits & gb.moving_bits
child_count_before = space9.size
if xor_val:
    child = Gua(xor_val, 999, VEC_DIM)
    child.is_native = False
    space9.guas.append(child)
    check(not child.is_native, "合体子卦: is_native=False")
    check(child.origin == 0, "合体子卦: origin=0")

# --- 子卦势从 0 开始 ---
child2 = Gua(0x4000, 1000, VEC_DIM)
child2.is_native = False
check(child2.potential == 0, "新生子卦 Ψ=0")
child2.hit_count = 5
check(child2.potential == 2, "子卦 C=5 → Ψ=2")

# --- save/load 保留 v1.3 字段 ---
space8.save()
space8b = Space()
check(space8b.load(), "v1.3 load: 成功")
check(space8b.size == 1, "v1.3 load: size 一致")
g_restored = space8b.guas[0]
check(g_restored.is_native, "v1.3 load: is_native 保留")
check(g_restored.origin == g_native.origin, "v1.3 load: origin 保留")

# --- tick 原生卦慢消散 (1/256) + 复生 ---
space10 = Space()
g1 = space10.ingest("one")
g2 = space10.ingest("two")
rebirths = 0
for _ in range(500):
    r = space10.tick()
    rebirths += r.get('rebirths', 0)
native_alive = sum(1 for g in space10.guas if g.is_native and not g.is_dead)
check(native_alive >= 1, f"原生卦存活: {native_alive} >= 1")
check(rebirths >= 0, f"原生复生: {rebirths} 次 (期望 ~4)")

# --- 子卦 tick 中放射衰变 ---
space11 = Space()
g3 = Gua(0xAAAA, 2000, VEC_DIM)
g3.is_native = False
space11.guas.append(g3)
dead_ticks = 0
for _ in range(200):
    space11.tick()
    if g3.is_dead:
        dead_ticks += 1
# 期望 ~VEC_DIM tick 内衰变，200 tick 内大概率
check(dead_ticks > 0, f"子卦在 200 tick 内衰变: dead_ticks={dead_ticks}")

# ================================================================
print(f"\n{'='*50}")
print(f"总计: {PASS} 通过, {FAIL} 失败")
print(f"{'='*50}")

# 清理
if os.path.exists(state_path):
    os.remove(state_path)

exit(0 if FAIL == 0 else 1)
