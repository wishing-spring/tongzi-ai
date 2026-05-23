"""金字塔 · 层叠排布 · 复数卦元"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi_kernel import Gua, Space, voxel_layout

仓 = Space("金字塔")

total = 0
for width in range(2, 9):
    n = 1 << width
    for i in range(n):
        仓.put(Gua(i))
    total += n

print(f"金字塔: {total} 块砖 · {len(仓)} 卦元")
print()

# 层叠显示
for width in range(8, 1, -1):
    n = 1 << width
    layout = voxel_layout(width)
    indent = (8 - width) * 2
    
    # 取该层首中尾三块展示
    vals = [Gua(i).value for i in range(n)]
    first = f"{vals[0]:0{width}b}"
    mid   = f"{vals[n//2]:0{width}b}"
    last  = f"{vals[n-1]:0{width}b}"
    
    print(f"{' '*indent}{width}爻层 [{layout[0]}x{layout[1]}x{layout[2]}] × {n}块")
    print(f"{' '*indent}  {first} ... {mid} ... {last}")
    print()

print(f"底面积: 16×16×4 = 1024 格位 (用 {256} 块)")
print(f"尖面积: 2×1×1 = 2 格位 (用 {4} 块)")
print(f"总砖: {total} 块 · 从底到尖 7 层")
