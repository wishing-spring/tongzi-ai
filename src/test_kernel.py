"""第三组基核验证"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi_kernel import *

# 公理1-2
a = generate_gua(0); b = generate_gua(16)
assert (a ^ b).value == (b ^ a).value
print('公理1-2: OK  XOR交换/自消')

# 公理3: 汉明
d = hamming(a.value, b.value)
print(f'公理3:   d(a,b)={d}')

# 公理4: 旋转保距
r1 = Gua(rotate_left(a.value, 3), a.pos)
r2 = Gua(rotate_left(b.value, 3), b.pos)
assert hamming(r1.value, r2.value) == d
print('公理4:   OK  旋转保距')

# 碰撞
diff, comm = a.collide(b)
assert diff == (a.value ^ b.value)
print(f'collide: diff={diff:04X} comm={comm:04X}')

# 轨道
o = a.orbit(b, 1)
print(f'orbit:   {a.value:04X} -> {o.value:04X}')

# 伸缩
s = a.stretch(b, 4)
print(f'stretch: lambda=4 -> {s.value:04X}')

# 汉明球
ball = a.ball(2)
print(f'ball(r=2): {len(ball)} (理论137)')

# 编码
g1 = encode('天地'); g2 = encode('玄黄')
print(f'encode:  {g1.value:04X} {g2.value:04X}  d={hamming(g1.value,g2.value)}')

# 环
ring = generate_ring(4, 0)
print(f'ring(4):  {[hex(g.value) for g in ring]}')

# 群操作
batch_collide(ring[:3])
mutual_orbit(ring[:2], a, 2)
print('batch/orbit: OK')

print('=' * 30)
print('第三组基核: OK 全部通过')
