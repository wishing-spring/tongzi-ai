#!/usr/bin/env python3
"""
童子 · 极简群域架构 · 交互入口
===================================
输入文本 → φ 编码成卦 → 群运算碰撞演化 → 输出碰撞结果

输入即投石入水，输出即水面涟漪。
无固定应答，无外部模板。
"""
from tongzi_core import Space, Gua, hamming, bit_count

def main():
    space = Space()

    if space.load():
        print("童子 · F₂ 极简群域")
        print("状态已加载。")
    else:
        print("童子 · F₂ 极简群域")
        print("初启。空无一卦。")
        print("输入文字开始投石入水。")

    print(f"  卦数:{space.size}  活跃:{space.active_count}  固化:{space.solid_count}  tick:{space.tick_count}")
    print("输入 /tick 推进节律 | /status 状态 | /exit 退出")
    print()

    while True:
        try:
            inp = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n关闭。")
            space.save()
            break

        if not inp:
            continue

        if inp.lower() in ("/exit", "/quit"):
            space.save()
            print("关闭。状态已保存。")
            break

        if inp == "/tick":
            space.tick()
            print(f"  tick {space.tick_count}  卦:{space.size}  活:{space.active_count}  固:{space.solid_count}")
            continue

        if inp == "/status":
            s = space.status()
            print(f"  tick:{s['tick']}  卦:{s['total']}  活跃:{s['active']}  固化:{s['solid']}  Lmax:{s['max_layer']}")
            continue

        # 摄入文字 → 生成卦
        g = space.ingest(inp)
        print(f"  → 生卦: {g}")

        # 对已有卦做一次碰撞（产出不写回）
        if space.size >= 2:
            other = space.guas[-2]
            diff, common = g.collide(other)
            print(f"     与前卦碰撞: ⊕={diff:016b}  ∧={common:016b}")
            g.hit_count += 1
            other.hit_count += 1

        space.save()


if __name__ == "__main__":
    main()
