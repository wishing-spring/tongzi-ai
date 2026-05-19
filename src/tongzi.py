#!/usr/bin/env python3
"""
童子 v0.5 · 出厂版 · 主入口
============================
唯一入口。极简交互。
使用者：输入信息静养，静待输出。
"""
from tongzi_core import TongziCore
from tongzi_mao import ShiErMao
from tongzi_data import NeiDan
from tongzi_seeds import 注入种子, 气场标注

def main():
    core = TongziCore()
    mao = ShiErMao(core)
    dan = NeiDan(core, mao)

    print("童子 v0.5 · 赤子之心")
    print("筑基完整版 · 开源首发")
    print()

    # 预暖：注入60颗本源种子·标注气场
    n = 注入种子(core)
    for tag, aura in 气场标注.items():
        if tag in core.data:
            dan.气场记录[tag] = aura
    print(f"筑基完成。种子卦象：{core.size} 条")
    print("静养中。输入任意文字，静待内丹回应。")
    print("输入 /exit 退出。输入 /status 查看内丹状态。")
    print()

    while True:
        try:
            inp = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n童子归元。")
            break

        if not inp:
            continue
        if inp.lower() in ("/exit", "/quit"):
            print("童子归元。")
            break
        if inp == "/status":
            s = core.status()
            m = mao.状态摘要
            气场数 = len(set(dan.气场记录.values()))
            print(f"  总卦象:{s['total']} 活跃:{s['active']} 归元:{s['returned']} 沉敛:{s['deep']}")
            print(f"  阳:{m['阳']} 阴:{m['阴']} 差:{m['阴阳差']}")
            print(f"  气场数:{气场数}")
            continue

        resp = dan.应答(inp)
        print(f"童子：{resp}")

if __name__ == "__main__":
    main()
