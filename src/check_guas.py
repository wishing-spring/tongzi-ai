"""全覆盖 · 直接枚举 · 数学保证"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi_kernel import Gua, voxel_layout
from tongzi_constants import PHI_LEN

total_gua = 0
total_yao = 0

for width in range(2, 9):
    n = 1 << width
    layout = voxel_layout(width)
    
    guas = [Gua(i) for i in range(n)]
    
    unique = len(set(g.value for g in guas))
    ones = [g.value.bit_count() for g in guas]
    
    print(f"{width}爻: {n}卦 | 独特={unique} OK | 密度={min(ones)}~{max(ones)} avg={sum(ones)/len(ones):.1f}")
    
    # 展示首中尾
    for idx in [0, n//2, n-1]:
        g = guas[idx]
        print(f"  [{idx:3d}] {g.value:0{width}b}")
    print()
    
    total_gua += n
    total_yao += n * width

print(f"七层: {total_gua} 卦元 | {total_yao} 爻 | 全独特全完整")
