"""两步半流程 · 完整走一遍"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi_kernel import Pyramid, Gua, form, phi_slice
from tools.encode import text_to_seed

p = Pyramid()

# 测试1: 全凸 (11111111)
print("=== 测试1: 全凸 ===")
r = p.flow(Gua(0xFF))
print(f"  输入: {form(Gua(0xFF))}  (8凸, 全凸)")
print(f"  第1步 路由: 停在 {r['入层']}爻  ({r['入值']})")
print(f"  第2步 碰撞: {r['咬合']} 个咬合")
print(f"  半步 归类: 归到 {r['出层']}爻  ({form(r['出值'],8)})")

# 测试2: 全凹 (00000000)
print("\n=== 测试2: 全凹 ===")
r = p.flow(Gua(0x00))
print(f"  输入: {form(Gua(0x00))}  (0凸, 全凹)")
print(f"  第1步 路由: 停在 {r['入层']}爻")
print(f"  第2步 碰撞: {r['咬合']} 个咬合")
print(f"  半步 归类: 归到 {r['出层']}爻  ({form(r['出值'],8)})")

# 测试3: 文字代入 "道"
print("\n=== 测试3: '道' ===")
ch = "道"
v = phi_slice(text_to_seed(ch), 8)
g = Gua(v)
r = p.flow(g)
print(f"  输入: '{ch}' → {form(g,8)}  ({v.bit_count()}凸)")
print(f"  第1步 路由: 停在 {r['入层']}爻")
print(f"  第2步 碰撞: {r['咬合']} 个咬合")
print(f"  半步 归类: 归到 {r['出层']}爻  ({form(r['出值'],8)})")

# 测试4: "天地玄黄" 四个字
print("\n=== 测试4: '天地玄黄' ===")
for ch in "天地玄黄":
    v = phi_slice(text_to_seed(ch), 8)
    g = Gua(v)
    r = p.flow(g)
    print(f"  '{ch}' {form(g,8)} → 入{r['入层']}爻 咬{r['咬合']}块 出{r['出层']}爻")

print("\n两步半流程: 路由→碰撞→归类, 全在塔内, 零外部干预")
