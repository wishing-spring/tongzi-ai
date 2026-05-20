"""童子 v0.5 · boundary observer (read-only)"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from tongzi_core import BitStore
from tongzi_mao import Balancer
from tongzi_data import Responder
from tongzi_seeds import inject_seeds, SEED_LABELS

store = BitStore()
balancer = Balancer(store)
responder = Responder(store, balancer)
inject_seeds(store)
for tag, label in SEED_LABELS.items():
    if tag in store.data:
        responder.cluster_labels[tag] = label

print("=" * 50)
print("童子 v0.5 · boundary check (read-only)")
print("=" * 50)

results = {}

# 1. Emotion differentiation
tests_emotion = ["hello", "joy", "delight", "anger", "sorrow", "grief"]
responses = {}
for t in tests_emotion:
    resp = responder.respond(t)
    responses[t] = resp
unique = len(set(responses.values()))
results["emotion"] = f"{unique}/{len(tests_emotion)} distinct ({', '.join(set(responses.values()))})"

# 2. Yang/Yin differentiation
tests_yang = ["sun", "light", "day"]
tests_yin  = ["night", "abyss", "winter"]
yang_resp = [responder.respond(t) for t in tests_yang]
yin_resp  = [responder.respond(t) for t in tests_yin]
yang_set = set(yang_resp)
yin_set  = set(yin_resp)
results["polarity"] = f"yang:{yang_set} yin:{yin_set} {'diff' if yang_set != yin_set else 'same'}"

# 3. Capacity
start = store.size
results["init_entries"] = str(start)
for i in range(15):
    responder.respond(f"test_{i}")
end = store.size
results["growth"] = f"+{end - start} ({start}→{end})"

# 4. Anomaly silence
try:
    for s in ["!!!", "12345", "0xDEADBEEF", "", "  "]:
        r = responder.respond(s)
    results["anomaly"] = "no crash"
except Exception as e:
    results["anomaly"] = f"crash: {e}"

# 5. Clusters
results["clusters"] = str(len(set(responder.cluster_labels.values())))

# 6. Balance
gap_before = balancer.balance_gap
balancer.auto_balance()
gap_after = balancer.balance_gap
results["auto_balance"] = f"gap {gap_before}→{gap_after}"

print()
for k, v in results.items():
    print(f"  {k}: {v}")
print()
print("boundary check complete.")
print("=" * 50)
