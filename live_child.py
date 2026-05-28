# -*- coding: utf-8 -*-
"""Child Live Process — always-on 10-year-old kid

Boot -> Dream -> Speak -> Wait -> Respond -> Dream on
Ctrl+C to exit (auto-save)
"""
import sys, os, io, time, threading, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from .lingxi_fusion import LingxiFusion

# global control
running = True
dream_lock = threading.Lock()
input_buffer: list[str] = []


def dream_loop(child: LingxiFusion):
    """Background dream — low-frequency breathing, ~2s per cycle"""
    global running
    while running:
        with dream_lock:
            child.dream(1, quiet=True)
        time.sleep(2.0)


def input_listener():
    """Foreground stdin listener"""
    global running, input_buffer
    while running:
        try:
            line = input()
            if line.strip():
                input_buffer.append(line.strip())
        except (EOFError, KeyboardInterrupt):
            running = False
            break


def main():
    global running, input_buffer

    print("=" * 56)
    print("  Child Live Process  v1.0")
    print("  Age 10 · Dreaming · Self-Growing · With Mood")
    print("  Ctrl+C to exit | /save save | /state status")
    print("=" * 56)

    child = LingxiFusion()

    # load saved state
    if os.path.exists('live_child_state.json'):
        loaded = child.load('live_child_state.json')
        if loaded:
            print(f"\n[awake] restored memory (tick={child.tick})")
        else:
            print("\n[newborn] save corrupt, fresh start")

    # boot dream
    print("\n[... dreaming ...]\n")
    child.dream(5, quiet=True)

    # start threads
    dreamer = threading.Thread(target=dream_loop, args=(child,), daemon=True)
    listener = threading.Thread(target=input_listener, daemon=True)
    dreamer.start()
    listener.start()

    last_save = time.time()

    try:
        while running:
            # process input
            if input_buffer:
                text = input_buffer.pop(0)

                if text == '/save':
                    with dream_lock:
                        child.save('live_child_state.json')
                    edges = sum(len(v) for v in child.pool.cooccur.values())
                    print(f'  [saved] tick={child.tick} edges={edges}')

                elif text == '/state':
                    with dream_lock:
                        mood = child.xiaotianyuan['mood']
                        energy = child.xiaotianyuan['mood_energy']
                        rules = len(child.rules.branches)
                        edges = sum(len(v) for v in child.pool.cooccur.values())
                        grown = len([b for _, b in child.rules.branches.items()
                                    if b.category == 'HARVESTED'])
                    print(f'  [status] tick={child.tick} mood={mood}({energy:.1f}) '
                          f'rules={rules}(+{grown}) edges={edges}')

                elif text == '/dream':
                    print('  [dreaming on...]')

                else:
                    with dream_lock:
                        result = child.receive(text)
                        reply = child.speak(result)
                    mood = child.xiaotianyuan['mood']
                    print(f'\n  Child({mood}): {reply}\n')

                    # dream after responding
                    with dream_lock:
                        child.dream(3, quiet=True)

            # auto-save every 5 minutes
            if time.time() - last_save > 300:
                with dream_lock:
                    child.save('live_child_state.json')
                last_save = time.time()

            time.sleep(0.1)

    except KeyboardInterrupt:
        pass

    finally:
        running = False
        child.save('live_child_state.json')
        edges = sum(len(v) for v in child.pool.cooccur.values())
        print(f'\n[sleep] tick={child.tick} saved live_child_state.json '
              f'rules={len(child.rules.branches)} edges={edges}')
        print('Goodnight.\n')


if __name__ == '__main__':
    main()
