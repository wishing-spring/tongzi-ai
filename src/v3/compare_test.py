# -*- coding: utf-8 -*-
"""对比测试：不同输入 → 不同输出？"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from v3.tongzi import TongziV3
from v3.eco_pool import EcoPool
from v3.express import express
from collections import Counter
import v3.eco_pool as ep
ep.F0 = 32

def test(input_text):
    tz = TongziV3()
    tz.add(EcoPool("🔥快生", tau=3, fit_min=2, birth_rate=1.5, flow_back=True,
                   density_max=128, stagnation_window=2, jitter_bits=5))
    tz.add(EcoPool("⚡涌动", tau=5, fit_min=2, birth_rate=1.2, flow_back=True,
                   density_max=96, stagnation_window=2, jitter_bits=5))
    chars = list(dict.fromkeys(list(input_text)))
    tz.feed(" ".join(chars))
    
    for _ in range(400):
        tz.tick()
    
    natives = [g for g in tz.surge.all() if g.is_native]
    native_by_ct = {g.ct: g for g in natives}
    
    result = Counter()
    for e in tz.eco:
        for g in e.guas:
            if not g.is_native:
                ct = g.ct
                best, best_dist = "?", 99
                for nct in native_by_ct:
                    d = bin(ct ^ nct).count('1')
                    if d < best_dist:
                        best_dist = d
                        best = express(native_by_ct[nct], natives)
                result[best] += 1
    
    top = [f"{n}({c})" for n,c in result.most_common(5)]
    births = sum(e.total_births for e in tz.eco)
    return top, births

tests = [
    ("A.天气对话", "今天天气真好风轻云淡阳光灿烂春风吹过花开满地草长莺飞万物生"),
    ("B.你好",     "你好"),
    ("C.吃饭",     "今天吃了吗肚子饿了想吃饭"),
    ("D.打架",     "打死你滚开别碰我刀剑枪炮战争"),
    ("E.爱情",     "我爱你一生一世永远在一起不离不弃"),
    ("F.数字",     "一二三四五六七八九十百千万亿"),
]

print(f"\n{'':14s} {'输入':22s} → 输出")
print("─"*80)
for label, text in tests:
    top, births = test(text)
    display = text[:20] + ("…" if len(text)>20 else "")
    out = " ".join(top)
    print(f"{label:14s} {display:22s} → {out:40s} ({births}孩子)")
print()
