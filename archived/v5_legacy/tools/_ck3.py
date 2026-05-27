from strokes import STROKE_COUNT, COMPONENT, STRUCTURE

# 统计
total = len(STROKE_COUNT)
comp31 = sum(1 for c in STROKE_COUNT if COMPONENT.get(c,31)==31)
struct0 = sum(1 for c in STROKE_COUNT if STRUCTURE.get(c,0)==0)
print(f"当前: {total}字 | 部件未分类: {comp31}字 | 独体: {struct0}字")
print(f"需补至300: +{300-total}字")

# 缺的23字
missing = '里开关进来去冷热胖瘦猫狗果杯脚眼拿放爸妈哥钱'
print(f"\n缺字({len(missing)}): {missing}")

# 部件=31但常见的正反对
problem = [('大','小'),('多','少'),('长','短'),('上','下'),('左','右'),('前','后')]
print("\n部件=31的正反对:")
for a,b in problem:
    print(f"  {a}-{b} 笔画:{STROKE_COUNT[a]}/{STROKE_COUNT[b]} 结构:{STRUCTURE.get(a,0)}/{STRUCTURE.get(b,0)}")
