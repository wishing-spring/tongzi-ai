"""变量对比 · 多组信息代入"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi_kernel import Gua, Space, phi_slice
from mortise import fit
from tools.encode import text_to_seed

inputs = [
    "道法自然",
    "天地玄黄",
    "1234",
    "abcd",
    "乾",
    "坤",
    "乾坤",
    "hello",
]

print("变量对比 · 信息→榫卯接触")
print("=" * 60)
print(f"{'输入':<10} {'卦元':>4} {'咬合':>6} {'碰撞':>6} {'空过':>6} {'咬合率':>8}")
print("-" * 60)

for text in inputs:
    guas = []
    for ch in text:
        seed = text_to_seed(ch)
        v = phi_slice(seed, 8)
        guas.append(Gua(v))
    
    n = len(guas)
    locks = bumps = gaps = 0
    for i in range(n):
        for j in range(n):
            r = fit(guas[i], guas[j], '+Z', '-Z')
            if r['碰'] == 0 and r['锁'] > 0: locks += 1
            elif r['碰'] > 0: bumps += 1
            else: gaps += 1
    
    total = n * n
    rate = locks / total * 100 if total > 0 else 0
    print(f"{text:<10} {n:>4} {locks:>6} {bumps:>6} {gaps:>6} {rate:>7.1f}%")

# 2. 单独对比: 乾 vs 坤
print("\n" + "=" * 60)
print("乾 vs 坤 · 面对面")
a = Gua(phi_slice(text_to_seed("乾"), 8))
b = Gua(phi_slice(text_to_seed("坤"), 8))
print(f"  乾: {a.value:08b}  坤: {b.value:08b}")
for face, opp in [('+Z','-Z'),('+X','-X'),('+Y','-Y')]:
    r = fit(a, b, face, opp)
    status = "咬合" if r['碰']==0 and r['锁']>0 else "碰撞" if r['碰']>0 else "空过"
    print(f"  {face} vs {opp}: 锁{r['锁']} 碰{r['碰']} 空{r['空']} → {status}")

# 3. 密度分析
print("\n" + "=" * 60)
print("密度分布 (8爻, 0~8个凸)")
from collections import Counter
for text in ["道法自然", "天地玄黄", "乾坤"]:
    densities = []
    for ch in text:
        v = phi_slice(text_to_seed(ch), 8)
        densities.append(v.bit_count())
    print(f"  {text}: {densities}  均值={sum(densities)/len(densities):.1f}")
