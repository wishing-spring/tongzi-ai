# -*- coding: utf-8 -*-
"""TongLing Interactive Chat

python chat.py
Type 'quit' / 'save' / 'report'
First run: 40s burn-in → saves factory.tl. Next run: instant load.
"""

import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'theory'))

from theory.fusion import TongLing

print("TongLing v5.0 - Interactive Chat")

native = '--native' in sys.argv

factory_path = os.path.join(os.path.dirname(__file__), 'factory.tl' if not native else 'factory_native.tl')
if os.path.exists(factory_path):
    print(f"Loading factory ({os.path.getsize(factory_path)//1024}KB)...")
    tl = TongLing.load(factory_path)
else:
    mode = "native" if native else "template"
    print(f"Burn-in ({mode} mode, ~40s)...")
    tl = TongLing(native=native)
    tl.save(factory_path)
    print("Factory saved.")

print(f"Ready! {len(tl.surge.all())} gua | AI={tl.lingxi.ai_ty.bagua}" + (" [F2原生]" if native else ""))
print("Talk to me. quit / save / report\n")

while True:
    try:
        text = input("> ").strip()
    except (EOFError, KeyboardInterrupt):
        break

    if not text:
        continue
    if text.lower() == 'quit':
        break
    elif text.lower() == 'save':
        tl.save()
        continue
    elif text.lower() == 'report':
        print(tl.report())
        continue

    resp = tl.chat(text)
    print(resp)

print("\nGoodbye.")
