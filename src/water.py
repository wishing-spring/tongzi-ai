"""童子 v0.5 · watering script (persistent)
=============================================
Scheduled cron: 15 seed-concept words per session, 2x/day.
State persists across runs via .tongzi_state.json.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from tongzi_core import BitStore
from tongzi_mao import Balancer
from tongzi_data import Responder, STATE_FILE
from tongzi_seeds import inject_seeds, SEED_LABELS
from datetime import datetime

def water():
    store = BitStore()
    balancer = Balancer(store)
    responder = Responder(store, balancer)

    is_first = not responder.load()

    if is_first:
        inject_seeds(store)
        for tag, label in SEED_LABELS.items():
            if tag in store.data:
                responder.cluster_labels[tag] = label
        print(f"[{datetime.now().strftime('%m-%d %H:%M')}] first boot")
        print(f"  seeds: {store.size}")
    else:
        print(f"[{datetime.now().strftime('%m-%d %H:%M')}] continue")
        print(f"  entries: {store.size}  tick: {store.tick}")
        if store.size < 50:
            print(f"  low ({store.size}), re-seeding...")
            inject_seeds(store)
            for tag, label in SEED_LABELS.items():
                if tag in store.data:
                    responder.cluster_labels[tag] = label

    # Daily watering words
    today_words = [
        "天地", "阴阳", "虚实", "动静", "冷暖",
        "明暗", "刚柔", "离合", "朝夕", "山海",
        "清宁", "澄澈", "风霜", "心境", "悠然",
    ]

    results = []
    for w in today_words:
        resp = responder.respond(w)
        results.append(f"  {w} → {resp}")

    s = store.status()
    clusters = len(set(responder.cluster_labels.values()))
    print(f"  entries:{s['total']} active:{s['active']} clusters:{clusters}")
    print(f"  stale:{s['stale']} tier2:{s['tier2']}")
    for r in results[:5]:
        print(r)
    print(f"  ... {len(results)} total")
    responder.save()
    print(f"  saved → {STATE_FILE}")

if __name__ == "__main__":
    water()
