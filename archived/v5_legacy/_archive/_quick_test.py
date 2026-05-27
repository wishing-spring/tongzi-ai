from tongzi_core import Space, Gua
from tongzi_constants import VEC_DIM, FULL_MASK

print('--- 基本导入 OK ---')
s = Space()
s.ingest('test')
print(f'ingest OK: {s}')
for i in range(5):
    r = s.tick()
    print(f'  tick {s.tick_count}: 撞{r["collisions"]} 合{r["merges"]}')
print(f'5 ticks OK: {s}')
print('--- 基本测试 PASS ---')
