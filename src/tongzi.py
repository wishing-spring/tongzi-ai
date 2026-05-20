#!/usr/bin/env python3
"""
童子 v0.5 · interactive entry point
=====================================
Three-stage pipeline: ingest → cluster → respond.
Type /status for internal state, /exit to quit.
State auto-saves after each response.
"""
from tongzi_core import BitStore
from tongzi_mao import Balancer
from tongzi_data import Responder, STATE_FILE
from tongzi_seeds import inject_seeds, SEED_LABELS

def main():
    store = BitStore()
    balancer = Balancer(store)
    responder = Responder(store, balancer)

    if responder.load():
        print("童子 v0.5 · bit-store responder")
        print("state loaded.")
        print(f"  entries:{store.size} active:{store.active_count} tick:{store.tick}")
        if store.size < 50:
            inject_seeds(store)
            for tag, label in SEED_LABELS.items():
                if tag in store.data:
                    responder.cluster_labels[tag] = label
    else:
        print("童子 v0.5 · bit-store responder")
        print("first boot.")
        inject_seeds(store)
        for tag, label in SEED_LABELS.items():
            if tag in store.data:
                responder.cluster_labels[tag] = label
        print(f"seeds: {store.size}")

    print("type /status or /exit")
    print()

    while True:
        try:
            inp = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nshutdown.")
            break

        if not inp:
            continue
        if inp.lower() in ("/exit", "/quit"):
            print("shutdown.")
            break
        if inp == "/status":
            s = store.status()
            m = balancer.status
            clusters = len(set(responder.cluster_labels.values()))
            print(f"  entries:{s['total']} active:{s['active']} stale:{s['stale']} tier2:{s['tier2']}")
            print(f"  yang:{m['yang']} yin:{m['yin']} gap:{m['gap']}")
            print(f"  clusters:{clusters} tick:{s['tick']}")
            continue

        resp = responder.respond(inp)
        print(f"tongzi: {resp}")
        responder.save()

if __name__ == "__main__":
    main()
