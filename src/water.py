"""童子自动浇花 v2.0 - 定时投喂本源粒子（持久化版）"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from tongzi_core import TongziCore
from tongzi_mao import ShiErMao
from tongzi_data import NeiDan, STATE_FILE
from tongzi_seeds import 注入种子, 气场标注
from datetime import datetime

def water():
    core = TongziCore()
    mao = ShiErMao(core)
    dan = NeiDan(core, mao)

    # 尝试加载持久化状态
    首次 = not dan.load_state()

    if 首次:
        # 首次启动：注入60颗本源种子
        注入种子(core)
        for tag, aura in 气场标注.items():
            if tag in core.data:
                dan.气场记录[tag] = aura
        print(f"[{datetime.now().strftime('%m-%d %H:%M')}] 首次筑基")
        print(f"  注入种子：{core.size} 条")
    else:
        # 已有内丹：不再重复注入种子，直接继续
        print(f"[{datetime.now().strftime('%m-%d %H:%M')}] 继续养护")
        print(f"  内丹卦象：{core.size} 条  tick：{core.tick}")
        # 检查是否需要补充种子（归元后可能种子不足）
        if core.size < 50:
            print(f"  种子不足({core.size})，补注...")
            注入种子(core)
            for tag, aura in 气场标注.items():
                if tag in core.data:
                    dan.气场记录[tag] = aura

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
    气场数 = len(set(dan.气场记录.values()))
    print(f"  卦象:{s['total']} 活跃:{s['active']} 气场:{气场数}")
    print(f"  归元:{s['returned']} 沉敛:{s['deep']}")
    for r in results[:5]:
        print(r)
    print(f"  ... 共{len(results)}条")

    # 保存状态
    dan.save_state()
    print(f"  状态已保存 -> {STATE_FILE}")

if __name__ == "__main__":
    water()
