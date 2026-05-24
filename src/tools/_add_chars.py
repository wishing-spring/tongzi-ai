"""补字至300·新增35字·含正反对立测试组"""
import os, sys

# 当前库
sys.path.insert(0, '.')
from strokes import STROKE_COUNT, STRUCTURE, COMPONENT

# === 新增35字 ===
new_strokes = {
    # -- 缺的22字 --
    '里':7,'开':4,'关':6,'进':7,'出':5,'来':7,'去':5,
    '冷':7,'热':10,'胖':9,'瘦':14,
    '猫':11,'狗':8,'果':8,'杯':8,
    '脚':11,'眼':11,'拿':10,'放':8,
    '爸':8,'妈':6,'哥':10,'钱':10,
    # -- 补13字 --
    '正':5,'反':4,'立':5,'本':5,'平':5,'方':4,'工':3,
    '净':8,'脏':10,'深':11,'答':12,'直':8,'睛':13,
}

new_struct = {
    '里':2,'开':0,'关':2,'进':5,'出':0,'来':0,'去':2,
    '冷':1,'热':2,'胖':1,'瘦':5,
    '猫':1,'狗':1,'果':0,'杯':1,
    '脚':1,'眼':1,'拿':2,'放':1,
    '爸':2,'妈':1,'哥':2,'钱':1,
    '正':0,'反':0,'立':0,'本':0,'平':0,'方':0,'工':0,
    '净':1,'脏':1,'深':1,'答':2,'直':2,'睛':1,
}

# 新部件编码: 24=辶 25=犭 26=目 27=疒 28=父 29=冫 30=礻
new_comp = {
    '里':31,'开':31,'关':31,'进':24,'出':31,'来':31,'去':31,
    '冷':29,'热':1,'胖':10,'瘦':27,
    '猫':25,'狗':25,'果':2,'杯':2,
    '脚':10,'眼':26,'拿':8,'放':31,
    '爸':28,'妈':20,'哥':31,'钱':3,
    '正':31,'反':31,'立':31,'本':2,'平':31,'方':31,'工':31,
    '净':29,'脏':10,'深':0,'答':31,'直':31,'睛':26,
}

# 输出追加行
stroke_lines = []
struct_lines = []
comp_lines = []

for ch in new_strokes:
    if ch not in STROKE_COUNT:
        sc = new_strokes[ch]
        st = new_struct.get(ch, 0)
        cp = new_comp.get(ch, 31)
        stroke_lines.append(f"'{ch}':{sc}")
        struct_lines.append(f"'{ch}':{st}")
        comp_lines.append(f"'{ch}':{cp}")
    else:
        print(f"跳过已存在: {ch}")

print(f"将新增 {len(stroke_lines)} 字")
print(f"笔画: {', '.join(stroke_lines[:5])}...")
print(f"结构: {', '.join(struct_lines[:5])}...")
print(f"部件: {', '.join(comp_lines[:5])}...")

# 追加到文件
path = r'C:\Users\45757\Desktop\lingxiAI_v5.0\src\tools\strokes.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 在 STROKE_COUNT 字典闭合 } 前插入
content = content.replace(
    "'命':8,'运':7,'梦':11,'魂':13,'鬼':10,'神':10,\n}",
    "'命':8,'运':7,'梦':11,'魂':13,'鬼':10,'神':10,\n" +
    ",\n".join(f"    {l}" for l in stroke_lines) + ",\n}"
)

# 在 STRUCTURE 字典闭合 } 前插入
content = content.replace(
    "'意':7,'竟':7,'曼':7,'复':7,'喜':7,'嘉':7,\n}",
    "'意':7,'竟':7,'曼':7,'复':7,'喜':7,'嘉':7,\n" +
    ",\n".join(f"    {l}" for l in struct_lines) + ",\n}"
)

# 在 COMPONENT 字典闭合 } 前插入
content = content.replace(
    "'户':30,'所':30,'局':30,'展':30,\n    '新':31,'旧':31,'真':31,'假':31,'是':31,'非':31,'无':31,'有':31,",
    "'户':30,'所':30,'局':30,'展':30,\n" +
    ",\n".join(f"    {l}" for l in comp_lines) + ",\n" +
    "    '新':31,'旧':31,'真':31,'假':31,'是':31,'非':31,'无':31,'有':31,"
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("完成")
