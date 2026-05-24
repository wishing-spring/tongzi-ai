"""榫卯卦元 · 8棱角凹凸 · 统一接触点"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi_kernel import Gua

# ============================================================
# 立方体 8 个棱角 → 8 爻直接映射
#       4-------5
#      /|      /|
#     0-------1 |    前=0-1-2-3  后=4-5-6-7
#     | 7-----|-6    上=0-1-4-5  下=3-2-7-6
#     |/      |/     右=1-2-5-6  左=0-3-4-7
#     3-------2
#
# bit_i = 1 → 角 i 凸出
# bit_i = 0 → 角 i 凹陷
# ============================================================

# 6个面各自包含的4个角
FACES = {
    '+Z': [0,1,2,3],
    '-Z': [4,5,6,7],
    '+X': [1,2,5,6],
    '-X': [0,3,4,7],
    '+Y': [0,1,4,5],
    '-Y': [3,2,7,6],
}

# 面对面时角的对应关系 (A的+Z对B的-Z)
# A[0]对B[7], A[1]对B[6], A[2]对B[5], A[3]对B[4]
FACE_CORNER_MAP = {
    ('+Z', '-Z'): {0:7, 1:6, 2:5, 3:4},
    ('-Z', '+Z'): {4:3, 5:2, 6:1, 7:0},
    ('+X', '-X'): {1:4, 2:7, 5:0, 6:3},
    ('-X', '+X'): {0:5, 3:6, 4:1, 7:2},
    ('+Y', '-Y'): {0:3, 1:2, 4:7, 5:6},
    ('-Y', '+Y'): {3:0, 2:1, 7:4, 6:5},
}

def corner(g: Gua, i: int) -> int:
    """角 i 是凸(1)还是凹(0)"""
    return (g.value >> i) & 1

def face_corners(g: Gua, face: str) -> list:
    """面上4角的凹凸状态"""
    return [corner(g, i) for i in FACES[face]]

def face_view(g: Gua, face: str) -> str:
    """面 2x2 凹凸图"""
    idx = FACES[face]
    c = [corner(g, i) for i in idx]
    # 角顺序: 左上 右上 / 左下 右下
    return f"{'#' if c[0] else '.'}{'#' if c[1] else '.'}\n{'#' if c[3] else '.'}{'#' if c[2] else '.'}"

def gua_view(g: Gua):
    """卦元完整榫卯结构"""
    print(f"卦 {g.value:016b}  (角值: {g.value & 0xFF:08b})")
    labels = {'+Z':'前','+X':'右','+Y':'上','-Z':'后','-X':'左','-Y':'下'}
    for name in ['+Z', '+X', '+Y', '-Z', '-X', '-Y']:
        fv = face_view(g, name)
        print(f"  {labels[name]}({name}):  {fv[0]}{fv[1]} / {fv[3]}{fv[4]}")

def fit(g1: Gua, g2: Gua, face1: str, face2: str) -> dict:
    """两卦元面面接触。

    返回: {咬合点数, 碰撞点数, 空过点数}
    """
    key = (face1, face2)
    if key not in FACE_CORNER_MAP:
        return {'锁': 0, '碰': 0, '空': 4}

    cmap = FACE_CORNER_MAP[key]
    locks = bumps = gaps = 0

    for ca, cb in cmap.items():
        a = corner(g1, ca)
        b = corner(g2, cb)
        if a == 1 and b == 0: locks += 1
        elif a == 1 and b == 1: bumps += 1
        else: gaps += 1

    return {'锁': locks, '碰': bumps, '空': gaps}

# ============================================================
# 测试
# ============================================================
if __name__ == '__main__':
    # 互补卦: A的凸对应B的凹
    a = Gua(0b10100101)
    b = Gua(0b01011010)  # a取反

    print("=== 卦A ===")
    gua_view(a)
    print("\n=== 卦B (互补) ===")
    gua_view(b)

    print("\n=== 接触测试 ===")
    for face, opp in [('+Z', '-Z'), ('+X', '-X'), ('+Y', '-Y')]:
        r = fit(a, b, face, opp)
        print(f"  {face} vs {opp}: 锁{r['锁']} 碰{r['碰']} 空{r['空']}  → {'咬合!' if r['碰']==0 and r['锁']>0 else '碰撞' if r['碰']>0 else '空过'}")

    # 自接触
    print(f"\n  A+Z vs A-Z: {fit(a,a,'+Z','-Z')}")

    # 展示8个值的外观
    print("\n=== 8 种基本卦元形态 ===")
    for v in range(8):
        g = Gua(v)
        fv = face_view(g, '+Z')
        print(f"  {v:03b} → 前: {fv[0]}{fv[1]} / {fv[3]}{fv[4]}")
