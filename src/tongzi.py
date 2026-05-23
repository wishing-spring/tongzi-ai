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
  /chain <词> [N] → 从词出发，跑 N 步碰撞关联链
  /ask <问题>      → 灌入问题、浸泡、收割被激活吸引子
  /exit      → 退出并保存
"""
from tongzi_core import Space, Gua


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
                    f"撞:{r['collisions']} 固:{r['solidified']} 合:{r['merges']}")
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


def cmd_chain(space: Space, args: list) -> str:
    """关联链: 从词出发，orbit 绕 0 旋转探索邻域，express 译出。

    /chain 冷 5 → 冷 → orbit(k=7) → express → 冬 → orbit(k=14) → express → ...
    不依赖 tick 频控，直接 orbit 在 GF(2) 空间跳关联。
    """
    if not args:
        return "用法: /chain <词> [步数]"
    word = args[0]
    n = int(args[1]) if len(args) > 1 else 3
    n = max(1, min(n, 12))

    # 预播种语义种子
    seeds = ["的", "是", "在", "有", "和", "了",
             "冷", "热", "冬", "夏", "雪", "火", "冰", "春", "秋"]
    for w in seeds:
        if space.size >= 25:
            break
        space.ingest(w)

    g = space.ingest(word)
    chain = [word]
    seen = {word}

    for i in range(n):
        step = (i + 1) * 7
        new_val = g.orbit(0, step)
        temp = Gua(new_val, 0, g.length)
        expr = space.express(temp)

        if expr and expr not in seen:
            chain.append(expr)
            seen.add(expr)
        elif expr:
            # 重复 → 换步长再试
            new_val2 = g.orbit(0, step + 3)
            temp2 = Gua(new_val2, 0, g.length)
            expr2 = space.express(temp2)
            if expr2 and expr2 not in seen:
                chain.append(expr2)
                seen.add(expr2)
            else:
                break
        else:
            break

        last = chain[-1]
        if last != word:
            g = space.ingest(last)

    return " → ".join(chain)


def cmd_ask(space: Space, args: list) -> str:
    """/ask <问题> — 势场扫描：石子投湖，看涟漪。

    三指标:
      1. hit_count 增量 — 被直接碰撞
      2. energy 变化   — 势能波动（间接传递）
      3. 衰变异常      — 本该衰变但被反复激活的"不死卦"

    不找答案，不预设关联。只看扰动。
    """
    if not args:
        return "用法: /ask <问题>"

    TICKS = 100
    TOP_K = 5

    question = ' '.join(args)

    # 0. 入水前状态
    state_before = {}
    for g in space.guas:
        state_before[id(g)] = {
            'hit':    g.hit_count,
            'energy': g.energy,
            'dead':   g.is_dead,
            'solid':  g.is_solid,
        }

    # 1. 投入
    q = space.ingest(question)
    state_before[id(q)] = {'hit': 0, 'energy': 0, 'dead': False, 'solid': False}

    # 2. 涟漪扩散
    for _ in range(TICKS):
        space.tick()

    # 3. 扫描三指标
    hit_deltas = []    # hit_count 增量
    energy_swings = [] # energy 波动
    undead = []        # 本该死但被激活的

    for g in space.guas:
        if id(g) == id(q):
            continue

        prev = state_before.get(id(g), {'hit': 0, 'energy': 0, 'dead': False, 'solid': False})

        dh = g.hit_count - prev['hit']
        de = abs(g.energy - prev['energy'])

        if dh > 0:
            hit_deltas.append((dh, g))
        if de > 0:
            energy_swings.append((de, g))

        # 衰变异常: 之前不是死的、现在也不是死的、但期间曾死过
        # (间接指标: 非原生卦居然活了这么久——被反复激活)
        if not g.is_native and not g.is_dead and dh >= 2:
            undead.append((dh, g))

    hit_deltas.sort(key=lambda x: x[0], reverse=True)
    energy_swings.sort(key=lambda x: x[0], reverse=True)
    undead.sort(key=lambda x: x[0], reverse=True)

    # 4. 输出
    lines = [f'  石子: "{question}"  →  投湖 {TICKS} tick']
    lines.append(f"  池中: {space.size} 卦  {space.status()['active']} 活跃  {space.status()['solid']} 固化")
    lines.append("")

    lines.append("  ◆ 被撞 (hit_count):")
    if hit_deltas:
        for i, (d, g) in enumerate(hit_deltas[:TOP_K]):
            src = f'"{g.source}"' if g.source else '(无源)'
            lines.append(f"    {i+1}. +{d}碰 {src}  {'[固]' if g.is_solid else ''}")
    else:
        lines.append("    (无 — 石子没碰到任何卦)")

    lines.append("")
    lines.append("  ◆ 势能波 (energy):")
    if energy_swings:
        for i, (d, g) in enumerate(energy_swings[:TOP_K]):
            src = f'"{g.source}"' if g.source else '(无源)'
            lines.append(f"    {i+1}. Δ{d}  {src}  {'[固]' if g.is_solid else ''}")
    else:
        lines.append("    (无 — 能量场平静)")

    lines.append("")
    lines.append("  ◆ 不死卦 (该衰但被激活):")
    if undead:
        for i, (d, g) in enumerate(undead[:TOP_K]):
            lines.append(f"    {i+1}. +{d}碰  #{g.id_t}  (子卦活过 {TICKS}tick)")
    else:
        lines.append("    (无 — 子卦都按时消逝)")

    return '\n'.join(lines)
    lines = [f"  问: \"{question}\""]
    lines.append(f"  浸泡 {TICKS} tick → 卦:{space.size} 活跃:{space.status()['active']}")
    lines.append("")

    if not deltas:
        lines.append("  (没有卦被激活 — 可能语料太少)")
    else:
        lines.append(f"  被激活的吸引子 (Top {min(TOP_K, len(deltas))}):")
        for i, (delta, g) in enumerate(deltas[:TOP_K]):
            mark = []
            if g.is_solid:
                mark.append("固")
            if g.is_native:
                mark.append("原")
            marker = f"[{'·'.join(mark)}]" if mark else ""
            src = f' "{g.source}"' if g.source else ""
            lines.append(f"  {i+1}. +{delta}碰 {g}{marker}{src}")

    return '\n'.join(lines)


def main():
    print("童子 · F2 极简群域")
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
            elif cmd == '/chain':
                print(cmd_chain(space, args))
            elif cmd == '/ask':
                print(cmd_ask(space, args))
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
