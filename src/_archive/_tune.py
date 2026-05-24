from tongzi import Tongzi

train = '水河火木天地日月山河金刀剑一二三四五六七八九十万千爱恨生死你我他'
for fm in [6,7,8,9,10,11,12]:
    tz = Tongzi(tau=5, fit_min=fm)
    tz.feed(train)
    r = sum(1 for n in tz.archives.values() if n.state=='result')
    p = sum(1 for n in tz.archives.values() if n.state=='pruned')
    h = sum(1 for n in tz.archives.values() if n.state=='active')
    print(f'FIT={fm:2d}({fm/32:.0%})  归约:{r:2d}  剪枝:{p:2d}  悬:{h}  剪枝率:{p/max(1,r+p):.0%}')
