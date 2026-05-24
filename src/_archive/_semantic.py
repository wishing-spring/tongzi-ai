import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from ren_tongzi import RenTongzi, _fit_16
from tools.strokes import STROKE_COUNT

train = '水河火木天地日月星云风雨雷电山水土金石你我他爱恨生死人女男父母心身体家走跑飞说看听吃打开关上下出入一二三四五六七八九十百千万刀剑门车灯书本笔纸桌凳衣帽大小长短高多少好坏新旧美丑红白光明暗'
seen = set()
chars = []
for ch in train:
    if ch not in seen:
        seen.add(ch)
        chars.append(ch)
train = ''.join(chars)

rt = RenTongzi(tau=5)
rt.learn(train)

for a,b,t in [
    ('水','河','near'),('火','水','anti'),('爱','恨','anti'),
    ('生','死','anti'),('天','地','anti'),('一','二','digit'),
    ('一','十','digit'),('大','小','anti'),('上','下','anti'),
    ('爱','水','none'),('人','石','none'),
]:
    if a not in rt.archives or b not in rt.archives: continue
    na,nb = rt.archives[a], rt.archives[b]
    ok_a = _fit_16(na.gA, nb.gA, 4) or _fit_16(nb.gA, na.gA, 4)
    ok_b = _fit_16(na.gB, nb.gB, 4) or _fit_16(nb.gB, na.gB, 4)
    ok_c = _fit_16(na.gC, nb.gC, 4) or _fit_16(nb.gC, na.gC, 4)
    ax = sum([ok_a, ok_b, ok_c])
    print(f'{a}-{b} [{t}]  {ax}/3')
