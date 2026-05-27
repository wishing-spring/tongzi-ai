from strokes import get_component, get_structure, get_strokes, STROKE_COUNT

# 在库的正反对立字
opposites = [
    ('大','小'), ('多','少'), ('长','短'), ('高','低'),
    ('上','下'), ('左','右'), ('前','后'),
    ('好','坏'), ('真','假'), ('新','旧'), ('轻','重'), ('快','慢'),
]

# 在库的归类字
categories = {
    '自然': '山水风雨云花草木日月',
    '动物': '鱼鸟虎兔虫马',
    '饮食': '米面菜茶酒盐糖',
    '器物': '桌椅灯刀笔门窗',
    '人体': '头手耳口心骨',
}

# 在库的日常字
daily = '走跑吃喝睡看听说你我他早晚今明春秋家路车书衣'

# 正反对: 同部还是异部?
print("=== 正反对立 部件/结构 ===")
for a,b in opposites:
    ca,cb = get_component(a), get_component(b)
    sa,sb = get_structure(a), get_structure(b)
    tag = "同部" if ca==cb else "异部"
    print(f"  {a}-{b}  comp:{ca}/{cb} st:{sa}/{sb} {tag}")

print("\n=== 归类组 ===")
for name, chars in categories.items():
    comps = [get_component(c) for c in chars]
    print(f"  {name}: {chars}  comps:{comps}")

print("\n缺失: 里开关进来去冷热胖瘦猫狗果杯脚眼拿放爸妈哥钱")
