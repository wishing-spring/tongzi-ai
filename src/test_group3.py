"""第三组完整验证"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi_blocks import *
clear()

print("=" * 40)
print("1. kernel: 卦爻")
print("=" * 40)
from tongzi_kernel import generate_gua, phi_slice, Gua, yao, bits
g = generate_gua(0)
print(f"  Gua: {bits(g)}  ({g})")
print(f"  yao: {yao(g)[:10]}...")
print(f"  phi_slice(0,4): {phi_slice(0,4):04b}")
print(f"  phi_slice(0,8): {phi_slice(0,8):08b}")

print()
print("=" * 40)
print("2. tools.axioms: 公理")
print("=" * 40)
from tools.axioms import hamming, collide, orbit, stretch, ball
a = generate_gua(0).value
b = generate_gua(16).value
print(f"  hamming(a,b) = {hamming(a,b)}")
print(f"  collide(a,b) = diff={collide(a,b)[0]:04X}")
print(f"  orbit(a,b,1) = {orbit(a,b,1):04X}")
print(f"  stretch(a,b,4) = {stretch(a,b,4):04X}")
print(f"  ball(a,1) = {len(ball(a,1))} (理论 {1+16}=17)")

print()
print("=" * 40)
print("3. 工坊: block + batch + 名册")
print("=" * 40)
print(census())
b1 = block("天地")
b2 = block("玄黄")
print(f"  造了两块: {census()}")
batch(["宇宙","洪荒","日月","盈昃"])
print(f"  又造四块: {census()}")
chain(all_blocks())
print(f"  串了链: {census()}")
print()
print(map())

print()
print("OK")
