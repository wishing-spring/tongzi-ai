"""2爻→8爻 · 七层全满"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi_kernel import phi_slice, Gua, voxel_view, voxel_layout
from tongzi_constants import PHI_LEN

total_gua = 0
total_yao = 0

for width in range(2, 9):
    n_gua = 1 << width  # 2^width
    layout = voxel_layout(width)
    
    guas = []
    for i in range(n_gua):
        pos = (i * width) % PHI_LEN
        v = phi_slice(pos, width)
        guas.append(Gua(v))
    
    ones = [g.value.bit_count() for g in guas]
    
    print(f"第{width-1}层 · {width}爻 · {layout[0]}x{layout[1]}x{layout[2]}")
    print(f"  {n_gua} 卦元 | 密度 min={min(ones)} max={max(ones)} avg={sum(ones)/len(ones):.1f}")
    
    # 展示首中尾三个
    for idx in [0, n_gua//2, n_gua-1]:
        g = guas[idx]
        print(f"  [{idx:3d}] {g.value:0{width}b} (密度{g.value.bit_count()})")
    print()
    
    total_gua += n_gua
    total_yao += n_gua * width

print("=" * 40)
print(f"七层塔满: {total_gua} 卦元 | {total_yao} 爻")
print(f"来源: phi母体 256位, 循环~{total_yao//PHI_LEN}周")
