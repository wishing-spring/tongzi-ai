"""
童子 v0.5 · responder
======================
Three-stage pipeline: ingest → cluster → respond.
Uses BitStore + Balancer. Persistence via .tongzi_state.json.
"""
from tongzi_core import BitStore
from tongzi_mao import Balancer
from tongzi_constants import *
from typing import Optional
import os

STATE_FILE = os.path.join(os.path.dirname(__file__), '.tongzi_state.json')

class Responder:
    """Three-stage response pipeline on top of BitStore + Balancer."""

    YANG_AURAS = {'heaven', 'warm', 'bright', 'joy', 'motion', 'day', 'rigid', 'union'}
    YIN_AURAS  = {'earth', 'cold', 'dark', 'sorrow', 'still', 'night', 'fluid', 'split'}

    def __init__(self, store: BitStore, balancer: Balancer):
        self.store = store
        self.balancer = balancer
        self.cluster_labels: dict[str, str] = {}  # tag → cluster name

    # ========== Stage 1: Ingest ==========

    def ingest(self, text: str, tag: str = None) -> dict:
        """Encode input → store. Anomalies stored silently."""
        vec = self.store.encode(text)
        tag = tag or f"entry_{self.store.tick}"

        # Anomaly check
        if self.store.size > 0 and self.store.is_anomaly(vec):
            self.store.data[tag] = vec
            self.store.active[tag] = self.store.tick - PURGE_AFTER
            self.store.potency[tag] = -1
            return {"status": "anomaly", "tag": tag, "vec": vec}

        # Normal ingest
        self.store.data[tag] = vec
        self.store.active[tag] = self.store.tick
        self.store.potency[tag] = 0

        # Check for existing cluster
        cluster_tags = self.store.find_cluster(vec)
        if cluster_tags:
            existing = self.cluster_labels.get(cluster_tags[0], "unknown")
            self.cluster_labels[tag] = existing

        return {"status": "ok", "tag": tag, "vec": vec,
                "cluster_hits": len(cluster_tags)}

    # ========== Stage 2: Cluster assimilation ==========

    def cluster_assimilate(self) -> dict:
        """Scan store for cluster-neighbor pairs, unify labels."""
        pairs = 0
        tags = list(self.store.data.keys())
        for i in range(len(tags)):
            if self.store.potency.get(tags[i], 0) == -1:
                continue
            vi = self.store.data[tags[i]]
            for j in range(i + 1, len(tags)):
                if self.store.potency.get(tags[j], 0) == -1:
                    continue
                vj = self.store.data[tags[j]]
                if self.store.hamming(vi, vj) <= CLUSTER_DISTANCE:
                    self.store.active[tags[i]] = self.store.tick
                    self.store.active[tags[j]] = self.store.tick
                    label = (self.cluster_labels.get(tags[i]) or
                             self.cluster_labels.get(tags[j]) or
                             f"cluster_{self.store.tick}")
                    self.cluster_labels[tags[i]] = label
                    self.cluster_labels[tags[j]] = label
                    pairs += 1
        return {"pairs": pairs,
                "clusters": len(set(self.cluster_labels.values()))}

    # ========== Stage 3: Select response ==========

    def select_response(self, clue_tags: list[str]) -> str:
        """Choose output text based on vector state."""
        # Frequency tiers
        deep = [t for t in clue_tags if self.store.potency.get(t, 0) >= 2]
        mid  = [t for t in clue_tags if self.store.potency.get(t, 0) >= 1]
        shallow = [t for t in clue_tags if self.store.potency.get(t, 0) == 0]

        # Cluster analysis
        auras = set()
        for t in clue_tags:
            if t in self.cluster_labels:
                auras.add(self.cluster_labels[t])

        yang_n = self.balancer.yang_count
        yin_n  = self.balancer.yin_count

        return self._pick_output(deep, mid, shallow, auras, yang_n, yin_n)

    def _pick_output(self, deep, mid, shallow, auras, yang, yin) -> str:
        """Hardcoded output selection tree — 9 possible responses."""
        aura_yang = any(w in str(auras) for w in self.YANG_AURAS)
        aura_yin  = any(w in str(auras) for w in self.YIN_AURAS)

        # Tier 3: deep (≥30 hits)
        if deep:
            if aura_yang and yang >= yin:
                return "心生暖意。"
            if aura_yin and yin >= yang:
                return "心绪沉郁。"
            if yang > yin:
                return "安好。"
            return "知晓。"

        # Tier 2: mid (≥10 hits)
        if mid:
            if aura_yang and not aura_yin:
                return "暖意生。"
            if aura_yin and not aura_yang:
                return "沉郁在。"
            if yang > yin:
                return "安好。"
            return "知晓。"

        # Tier 1: shallow (all entries start here)
        if shallow:
            if aura_yang and aura_yin:
                return "嗯。"
            if aura_yang:
                return "安好。"
            if aura_yin:
                return "……"
            if yang > yin:
                return "好。"
            return "……"

        # Empty: factory default
        if yang > yin:
            return "嗯。"
        return "……"

    # ========== Full pipeline ==========

    def respond(self, text: str) -> str:
        """Full pipeline: ingest → cycle → assimilate → respond."""
        # Stage 1
        result = self.ingest(text)
        if result["status"] == "anomaly":
            return ANOMALY_RESPONSE

        # Run one scheduling cycle
        self.balancer.cycle()

        # Stage 2
        self.cluster_assimilate()

        # Stage 3
        vec = self.store.encode(text)
        similar = self.store.find_nearest(vec, threshold=SIMILARITY_NEAR)
        return self.select_response(similar)

    # ========== Persistence ==========

    def save(self):
        """Save full state (store + cluster labels)."""
        import json
        self.store.save(STATE_FILE)
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
        state['clusters'] = self.cluster_labels
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def load(self) -> bool:
        """Load full state. Returns False on first run."""
        import json
        if not self.store.load(STATE_FILE):
            return False
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
        self.cluster_labels = state.get('clusters', {})
        return True
