"""童子自动浇花 v1.0 - 定时投喂本源粒子"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from tongzi_core import TongziCore
from tongzi_mao import ShiErMao
from tongzi_data import NeiDan
from tongzi_seeds import 注入种子, 气场标注
from datetime import datetime

def water():
    core = TongziCore()
    mao = ShiErMao(core)
    dan = NeiDan(core, mao)

    # 注入本源种子
    注入种子(core)
    for tag, aura in 气场标注.items():
        if tag in core.data:
            dan.气场记录[tag] = aura
    dan.气场同化()

    # 每日浇花词库
    today_words = [
        "天地", "阴阳", "虚实", "动静", "冷暖",
        "明暗", "刚柔", "离合", "朝夕", "山海",
        "清宁", "澄澈", "风霜", "心境", "悠然",
    ]

    results = []
    for w in today_words:
        resp = dan.应答(w)
        results.append(f"  {w} → {resp}")

    s = core.status()
    print(f"[{datetime.now().strftime('%m-%d %H:%M')}] 浇花完成")
    print(f"  卦象:{s['total']} 活跃:{s['active']} 气场:{len(set(dan.气场记录.values()))}")
    for r in results[:5]:
        print(r)
    print(f"  ... 共{len(results)}条")

if __name__ == "__main__":
    water()
