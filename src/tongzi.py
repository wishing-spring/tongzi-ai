#!/usr/bin/env python3
"""
童子 · 极简群域架构 · 交互入口
===================================
输入文本 → φ 编码成卦 → 碰撞 → 输出位串。

投石入水，看涟漪。
无固定应答，无外部模板，无神经网络。

命令:
  任意文本    → 摄入并生成新卦
  /tick [N]  → 推进 N 个节律周期 (默认 1)
  /status    → 显示空间状态
  /list      → 列出所有卦
  /exit      → 退出并保存
"""
import sys
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
    lines = [
        f"  tick: {s['tick']}",
        f"  卦: {s['total']}  活跃: {s['active']}  固化: {s['solid']}",
        f"  Lmax: {s['max_layer']}",
    ]
    return '\n'.join(lines)


def cmd_list(space: Space, args: list) -> str:
    guas = space.guas
    n = len(guas)
    if args and args[0] == 'solid':
        guas = [g for g in guas if g.is_solid]
    elif args and args[0] == 'active':
        guas = [g for g in guas if not g.is_solid]

    if not guas:
        return "  (空)"
    lines = []
    for i, g in enumerate(guas):
        lines.append(f"  [{i}] {g}")
        if len(lines) >= 20:
            lines.append(f"  ... (共 {len(guas)} 卦)")
            break
    return '\n'.join(lines)


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
            else:
                print(f"  未知命令: {cmd}")
            continue

        # ---- 摄入文本 ----
        g = space.ingest(inp)
        print(f"  → {g}")

        # 与前卦碰撞
        if space.size >= 2:
            other = space.guas[-2]
            diff, common = g.collide(other)
            print(f"      ⊕={diff:016b}  ∧={common:016b}")
            g.hit_count += 1
            other.hit_count += 1

    # 退出保存
    space.save()
    print(f"\n已保存。{space}")


if __name__ == "__main__":
    main()
