import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from theory.fusion import TongLing

print("=== F2 Native + Logic Frames ===")
tl = TongLing(native=True)

msgs = [
    "下雨了",
    "冷",
    "为什么",
    "那我走",
    "原来是这样"
]
for msg in msgs:
    print(f"\n> {msg}")
    print(f"  {tl.chat(msg)}")
