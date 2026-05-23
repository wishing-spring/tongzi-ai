"""测试 ingest_batch + /ask"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from tongzi_core import Space

qzw_text = "天地玄黄宇宙洪荒日月盈昃辰宿列张寒来暑往秋收冬藏闰余成岁律吕调阳云腾致雨露结为霜金生丽水玉出昆冈剑号巨阙珠称夜光果珍李柰菜重芥姜海咸河淡鳞潜羽翔龙师火帝鸟官人皇始制文字乃服衣裳推位让国有虞陶唐吊民伐罪周发殷汤坐朝问道垂拱平章爱育黎首臣伏戎羌遐迩一体率宾归王鸣凤在竹白驹食场化被草木赖及万方"
words = [qzw_text[i:i+2] for i in range(0, len(qzw_text), 2)]
seen = set()
words = [w for w in words if not (w in seen or seen.add(w))]

s = Space()

# 分批灌入，每批16词
BATCH = 16
for i in range(0, len(words), BATCH):
    batch = words[i:i+BATCH]
    s.ingest_batch(batch)

print(f"灌入 {len(words)} 词 ({len(words)//BATCH + 1} 批), 泡 300 tick...")
for _ in range(100):
    s.tick()

print(f"池: {s.size} 卦  {s.status()['active']} 活跃  {s.status()['solid']} 固化")
print()

# 验证: 找还活着的同批词
survivors = {g.source: g for g in s.guas if g.source}
print(f"幸存词: {list(survivors.keys())[:10]}...")

# 验证: 同批活着的词汉明距离
from tongzi_core import hamming
for b_idx in range(0, len(words), BATCH):
    batch = words[b_idx:b_idx+BATCH]
    alive = [(a, b) for a in batch for b in batch 
             if a < b and a in survivors and b in survivors]
    if alive:
        a, b = alive[0]
        ga, gb = survivors[a], survivors[b]
        print(f"  批{b_idx//BATCH}: d({a},{b})={hamming(ga.value, gb.value)}")
        break

print()

# /ask 测试 (减少 tick 防过度清理)
for q_text in ["天地", "龙师", "金生"]:
    snap = {id(g): g.hit_count for g in s.guas}
    
    q = s.ingest(q_text)
    snap[id(q)] = 0
    
    for _ in range(50):
        s.tick()
    
    hit_d = []
    for g in s.guas:
        if g is q: continue
        dh = g.hit_count - snap.get(id(g), 0)
        if dh > 0: hit_d.append((dh, g))
    
    hit_d.sort(key=lambda x: x[0], reverse=True)
    
    print(f"石子: '{q_text}'")
    print(f"  被撞: ", end="")
    if hit_d: print(", ".join(f"{g.source}+{d}" for d,g in hit_d[:5]))
    else: print("无")
    print()
