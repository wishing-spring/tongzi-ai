"""补字至300 · 安全模式 · 直接重写数据库文件"""
import sys; sys.path.insert(0, '.')
from strokes import STROKE_COUNT, STRUCTURE, COMPONENT

# === 新增35字 ===
add_strokes = {
    '里':7,'开':4,'关':6,'进':7,'出':5,'来':7,'去':5,
    '冷':7,'热':10,'胖':9,'瘦':14,'猫':11,'狗':8,'果':8,'杯':8,
    '脚':11,'眼':11,'拿':10,'放':8,'爸':8,'妈':6,'哥':10,'钱':10,
    '正':5,'反':4,'立':5,'本':5,'平':5,'方':4,'工':3,
    '净':8,'脏':10,'深':11,'答':12,'直':8,'睛':13,
}
add_struct = {
    '里':2,'开':0,'关':2,'进':5,'出':0,'来':0,'去':2,
    '冷':1,'热':2,'胖':1,'瘦':5,'猫':1,'狗':1,'果':0,'杯':1,
    '脚':1,'眼':1,'拿':2,'放':1,'爸':2,'妈':1,'哥':2,'钱':1,
    '正':0,'反':0,'立':0,'本':0,'平':0,'方':0,'工':0,
    '净':1,'脏':1,'深':1,'答':2,'直':2,'睛':1,
}
add_comp = {
    '里':31,'开':31,'关':31,'进':24,'出':31,'来':31,'去':31,
    '冷':29,'热':1,'胖':10,'瘦':27,'猫':25,'狗':25,'果':2,'杯':2,
    '脚':10,'眼':26,'拿':8,'放':31,'爸':28,'妈':20,'哥':31,'钱':3,
    '正':31,'反':31,'立':31,'本':2,'平':31,'方':31,'工':31,
    '净':29,'脏':10,'深':0,'答':31,'直':31,'睛':26,
}

new_count = 0
for ch in add_strokes:
    if ch not in STROKE_COUNT:
        new_count += 1
        STROKE_COUNT[ch] = add_strokes[ch]
        STRUCTURE[ch] = add_struct.get(ch, 0)
        COMPONENT[ch] = add_comp.get(ch, 31)

print(f"新增 {new_count} 字 · 总字库 {len(STROKE_COUNT)}")
print(f"部件未分类: {sum(1 for c in STROKE_COUNT if COMPONENT.get(c,31)==31)}")

# 验证关键对
pairs = [('冷','热'),('进','出'),('猫','狗'),('爸','妈'),('左','右'),('正','反')]
from strokes import get_component, get_structure
for a,b in pairs:
    print(f"  {a}-{b}  comp:{get_component(a)}/{get_component(b)} st:{get_structure(a)}/{get_structure(b)}")

# 现在要把更新后的数据写回文件
# 直接重写整个文件
path = r'C:\Users\45757\Desktop\lingxiAI_v5.0\src\tools\strokes.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 更新STROKE_COUNT
for ch in add_strokes:
    if f"'{ch}':" not in content.split('STROKE_COUNT')[1].split('}')[0]:
        # 在 STROKE_COUNT 的最后一个条目后插入
        insert = f"    '{ch}':{add_strokes[ch]},\n"
        # 找到 STROKE_COUNT 闭合括号前的位置
        marker = "'神':10,\n}"
        if marker in content:
            content = content.replace(marker, "'神':10,\n" + insert + "}")
        else:
            print(f"找不到插入点 STROKE_COUNT, 请手动添加 {ch}")

# 更新STRUCTURE  
for ch in add_struct:
    if f"'{ch}':" not in content.split('STRUCTURE')[1].split('}')[0]:
        marker = "'嘉':7,\n}"
        if marker in content:
            content = content.replace(marker, "'嘉':7,\n" + f"    '{ch}':{add_struct[ch]},\n" + "}")
        else:
            print(f"找不到插入点 STRUCTURE, 请手动添加 {ch}")

# 更新COMPONENT
for ch in add_comp:
    if f"'{ch}':" not in content.split('COMPONENT')[1].split('}')[0]:
        marker = "'户':30,'所':30,'局':30,'展':30,\n    '新':31"
        if marker in content:
            content = content.replace(marker, f"'{ch}':{add_comp[ch]}, " + marker)
        else:
            print(f"找不到插入点 COMPONENT, 请手动添加 {ch}")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("文件已更新")
