#!/usr/bin/env python3
# Copyright (c) 2026 Tongzi Project (wishing-spring)
# Licensed under the MIT License. See LICENSE file for details.
"""
童子 · 极简群域架构 · 交互入口
===================================
输入文本 → φ 编码成卦 → 碰撞 → 极简内丹反向译出。

投石入水，看涟漪。
无固定应答，无外部模板，无神经网络。

命令:
  任意文本    → 摄入并生成新卦，与最近卦碰撞后反向译出
  /tick [N]  → 推进 N 个节律周期 (默认 1)
  /status    → 显示空间状态
  /list      → 列出所有卦
  /show <N>  → 对第 N 个卦做反向译出
  /exit      → 退出并保存
"""
from tongzi_core import Space


def cmd_tick(space: Space, args: list) -> str:
    n = 1
    if args:
        try:
            n = int(args[0])
        except ValueError:
            return "用法: /tick [N]"
    msgs = []
    for _ in range(n):
        r = space.tick()
        msgs.append(f"  tick {space.tick_count}  "
                    f"撞:{r['collisions']} 固:{r['solidified']} 并:{r['merged']}")
    return '\n'.join(msgs)


def cmd_status(space: Space) -> str:
    s = space.status()
    return (f"  tick:{s['tick']}  卦:{s['total']}  "
            f"活跃:{s['active']}  固化:{s['solid']}  "
            f"Lmax:{s['max_layer']}")


def cmd_list(space: Space, args: list) -> str:
    guas = space.guas
    if args and args[0] == 'solid':
        guas = [g for g in guas if g.is_solid]
    elif args and args[0] == 'active':
        guas = [g for g in guas if not g.is_solid]
    if not guas:
        return "  (空)"
    lines = []
    for i, g in enumerate(guas):
        src = f' "{g.source}"' if g.source else ''
        lines.append(f"  [{i}] {g}{src}")
        if len(lines) >= 20:
            lines.append(f"  ... (共 {len(guas)} 卦)")
            break
    return '\n'.join(lines)


def cmd_show(space: Space, args: list) -> str:
    if not args:
        return "用法: /show <序号>"
    try:
        idx = int(args[0])
    except ValueError:
        return "序号需为整数"
    if idx < 0 or idx >= space.size:
        return f"序号超出范围 [0, {space.size - 1}]"
    g = space.guas[idx]
    expr = space.express(g)
    return f"  [{idx}] {g}\n  内丹译出: {expr if expr else '(无匹配)'}"


def main():
    print("童子 · F₂ 极简群域")
    print("投石入水，看涟漪。")

    space = Space()
    if space.load():
        print(f"已加载: {space}")
    else:
        print("初启，空无一卦。")
    print()

    while True:
        try:
            inp = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not inp:
            continue

        # ---- 命令 ----
        if inp.startswith('/'):
            parts = inp.split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd in ('/exit', '/quit'):
                break
            elif cmd == '/tick':
                print(cmd_tick(space, args))
            elif cmd == '/status':
                print(cmd_status(space))
            elif cmd == '/list':
                print(cmd_list(space, args))
            elif cmd == '/show':
                print(cmd_show(space, args))
            else:
                print(f"  未知命令: {cmd}")
            continue

        # ---- 摄入文本 ----
        g = space.ingest(inp)

        # 与前卦碰撞
        if space.size >= 2:
            other = space.guas[-2]
            diff, common = g.collide(other)
            g.hit_count += 1
            other.hit_count += 1

            # 极简内丹: 反向译出
            expr = space.express(g)
            print(f"  {expr if expr else g}")
        else:
            print(f"  (第一卦，等待更多输入)")

    # 退出保存
    space.save()
    print(f"\n已保存。{space}")


if __name__ == "__main__":
    main()
