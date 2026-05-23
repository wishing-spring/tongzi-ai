"""观察 · 全仓咬合矩阵"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi_kernel import Gua, Space
from mortise import fit, face_view, FACES

# 入仓
仓 = Space("童子")
# 只取 8爻层的 256 卦 (全立方体)
guas_8 = [Gua(i) for i in range(256)]
for g in guas_8:
    仓.put(g)

print("观察: 256 个 8爻榫卯卦元")
print("=" * 50)

# 1. 互补对观察
print("\n--- 互补对 ---")
for v in range(16):
    a = Gua(v)
    b = Gua(v ^ 0xFF)  # 位取反
    r = fit(a, b, '+Z', '-Z')
    if r['锁'] > 0:
        print(f"  {v:08b} ⊕ {v^0xFF:08b}  → 锁{r['锁']} 碰{r['碰']} 空{r['空']}")
print()

# 2. 全对全扫描 · +Z/-Z 面
print("--- 全对全 +Z/-Z 接触统计 ---")
locks = bumps = gaps = matches = 0
for i in range(256):
    for j in range(256):
        r = fit(Gua(i), Gua(j), '+Z', '-Z')
        if r['碰'] == 0 and r['锁'] > 0:
            locks += 1
            matches += 1
        elif r['碰'] > 0:
            bumps += 1
        else:
            gaps += 1

total = 256 * 256
print(f"  咬合: {locks} ({locks/total*100:.1f}%)")
print(f"  碰撞: {bumps} ({bumps/total*100:.1f}%)")
print(f"  空过: {gaps} ({gaps/total*100:.1f}%)")

# 3. 咬合分布: 每个卦元能跟多少个配对
print("\n--- 咬合分布 (每个卦元的配对数量) ---")
pair_counts = []
for i in range(256):
    count = 0
    for j in range(256):
        r = fit(Gua(i), Gua(j), '+Z', '-Z')
        if r['碰'] == 0 and r['锁'] > 0:
            count += 1
    pair_counts.append(count)

print(f"  min={min(pair_counts)} max={max(pair_counts)} avg={sum(pair_counts)/256:.1f}")

# 4. 展示最"合群"和最"孤僻"的
print("\n--- 极端卦元 ---")
most = max(range(256), key=lambda i: pair_counts[i])
least = min(range(256), key=lambda i: pair_counts[i])
print(f"  最合群: {most:08b} → {pair_counts[most]} 个配对")
print(f"  最孤僻: {least:08b} → {pair_counts[least]} 个配对")

# 5. 自咬统计
print("\n--- 自咬检测 ---")
self_fit = sum(1 for i in range(256) 
               if fit(Gua(i), Gua(i), '+Z', '-Z')['碰'] == 0 
               and fit(Gua(i), Gua(i), '+Z', '-Z')['锁'] > 0)
print(f"  能自咬: {self_fit}/256")
