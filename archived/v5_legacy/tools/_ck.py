from strokes import STROKE_COUNT
wanted = '大小多少长短高低上下左右前后里外开关进出来去好坏冷热胖瘦真假新旧轻重快慢'
wanted += '山水风雨云花草木日月猫狗鱼鸟虎兔虫马米面菜果茶酒盐糖桌椅杯灯刀笔门窗'
wanted += '头手脚眼耳口心骨走跑吃喝睡看听说拿放爸妈哥姐你我他早晚今明春秋家路车书钱衣'
missing = [c for c in wanted if c not in STROKE_COUNT]
print(f'共{len(wanted)}字, 缺{len(missing)}字: {" ".join(missing)}')
print(f'在库: {len(wanted)-len(missing)}字')
