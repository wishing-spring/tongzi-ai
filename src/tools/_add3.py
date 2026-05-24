"""一次性补字 · 找到每个字典的}前插入所有新条目"""
import re

new = [
    # (字, 笔画, 结构, 部件)
    ('里',7,2,31),('开',4,0,31),('关',6,2,31),('进',7,5,24),('出',5,0,31),
    ('来',7,0,31),('去',5,2,31),('冷',7,1,29),('热',10,2,1),('胖',9,1,10),
    ('瘦',14,5,27),('猫',11,1,25),('狗',8,1,25),('果',8,0,2),('杯',8,1,2),
    ('脚',11,1,10),('眼',11,1,26),('拿',10,2,8),('放',8,1,31),('爸',8,2,28),
    ('妈',6,1,20),('哥',10,2,31),('钱',10,1,3),
    ('正',5,0,31),('反',4,0,31),('立',5,0,31),('本',5,0,2),('平',5,0,31),
    ('方',4,0,31),('工',3,0,31),('净',8,1,29),('脏',10,1,10),('深',11,1,0),
    ('答',12,2,31),('直',8,2,31),('睛',13,1,26),
]

path = r'C:\Users\45757\Desktop\lingxiAI_v5.0\src\tools\strokes.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 在 STROKE_COUNT 的 } 前插入
stroke_insert = ",\n".join(f"    '{ch}':{sc}" for ch,sc,_,_ in new)
content = re.sub(
    r"('神':10,\n)(\s*\})",
    rf"\1{stroke_insert},\n\2",
    content
)

# 在 STRUCTURE 的 } 前插入
struct_insert = ",\n".join(f"    '{ch}':{st}" for ch,_,st,_ in new)
content = re.sub(
    r"('嘉':7,\n)(\s*\})",
    rf"\1{struct_insert},\n\2",
    content
)

# 在 COMPONENT 中: 在最后一个明确条目和 } 之间插入
comp_insert = ",\n".join(f"    '{ch}':{cp}" for ch,_,_,cp in new)
content = re.sub(
    r"(    '户':30,'所':30,'局':30,'展':30,\n)",
    rf"\1{comp_insert},\n",
    content
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

# 验证
import sys; sys.path.insert(0, '.')
from strokes import STROKE_COUNT
print(f"总字库: {len(STROKE_COUNT)}")
print(f"新增验证: 里={STROKE_COUNT.get('里','缺')} 冷={STROKE_COUNT.get('冷','缺')} 睛={STROKE_COUNT.get('睛','缺')}")
