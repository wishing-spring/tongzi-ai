"""
童子 v0.5 · F₂^16 vector store
===============================
Pure bitwise operations. No floats. No matrices.
"""
from tongzi_constants import *
from typing import Optional
import json, os

class BitStore:
    """16-bit F₂ vector store with Hamming-distance retrieval."""

    def __init__(self):
        self.data: dict[str, int] = {}        # tag → 16-bit vector
        self.active: dict[str, int] = {}      # tag → last_used_tick
        self.tick: int = 0
        self.hits: dict[str, int] = {}        # tag → cumulative hits
        self.potency: dict[str, int] = {}     # tag → frequency tier (0/1/2/-1)
                                              # -1 = stale (marked for later purge)

    # ========== Static bitwise ops ==========

    @staticmethod
    def xor(a: int, b: int) -> int:
        return a ^ b

    @staticmethod
    def popcount(v: int) -> int:
        return v.bit_count()

    @staticmethod
    def hamming(a: int, b: int) -> int:
        return BitStore.popcount(a ^ b)

    @staticmethod
    def rotate_left(v: int, step: int = 1) -> int:
        return ((v << step) | (v >> (VEC_DIM - step))) & FULL_MASK

    @staticmethod
    def rotate_right(v: int, step: int = 1) -> int:
        return ((v >> step) | (v << (VEC_DIM - step))) & FULL_MASK

    # ========== Text encoding ==========

    def encode(self, text: str) -> int:
        """ord-sum → 16-bit. Collision-prone but zero-dependency."""
        return sum(ord(c) for c in text) & FULL_MASK

    # ========== Vector storage ==========

    def put(self, tag: str, text: str):
        """Store a vector. Triggers purge at capacity."""
        if len(self.data) >= MAX_ENTRIES:
            self.purge_stale()
        vec = self.encode(text)
        self.data[tag] = vec
        self.active[tag] = self.tick
        self.hits[tag] = 0
        self.potency[tag] = 0

    def get(self, tag: str) -> Optional[int]:
        """Retrieve vector. Refreshes active timestamp, bumps freq tier."""
        if tag in self.data:
            self.active[tag] = self.tick
            self.hits[tag] = self.hits.get(tag, 0) + 1
            h = self.hits[tag]
            p = self.potency.get(tag, 0)
            if p < 1 and h >= FREQ_TIER1:
                self.potency[tag] = 1
            elif p < 2 and h >= FREQ_TIER2:
                self.potency[tag] = 2
            return self.data[tag]
        return None

    @property
    def size(self) -> int:
        return len(self.data)

    @property
    def active_count(self) -> int:
        return sum(1 for t in self.active
                   if self.tick - self.active[t] <= STALE_AFTER)

    def find_nearest(self, target_vec: int,
                     threshold: int = SIMILARITY_NEAR) -> list[str]:
        """Find vectors within Hamming distance ≤ threshold."""
        res = []
        for t, v in self.data.items():
            if self.potency.get(t, 0) == -1:  # skip stale
                continue
            if self.hamming(target_vec, v) <= threshold:
                self.active[t] = self.tick
                self.hits[t] = self.hits.get(t, 0) + 1
                res.append(t)
        return res

    def find_cluster(self, target_vec: int) -> list[str]:
        """Find same-cluster vectors (dH ≤ CLUSTER_DISTANCE)."""
        return self.find_nearest(target_vec, threshold=CLUSTER_DISTANCE)

    def find_distant(self, target_vec: int,
                     threshold: int = SIMILARITY_ALIEN) -> list[str]:
        """Find far-away vectors (dH ≥ threshold)."""
        res = []
        for t, v in self.data.items():
            if self.potency.get(t, 0) == -1:
                continue
            if self.hamming(target_vec, v) >= threshold:
                self.active[t] = self.tick
                res.append(t)
        return res

    def is_anomaly(self, vec: int) -> bool:
        """True if vector is too far from all known vectors."""
        if not self.data:
            return False
        min_d = min(self.hamming(vec, v) for v in self.data.values())
        return min_d >= ANOMALY_DISTANCE

    # ========== Tick & lifecycle ==========

    def advance_tick(self):
        self.tick += 1

    def purge_stale(self):
        """Delete vectors unused for > PURGE_AFTER ticks."""
        doomed = [t for t, last in self.active.items()
                  if self.tick - last > PURGE_AFTER]
        for t in doomed:
            self.data.pop(t, None)
            self.active.pop(t, None)
            self.potency.pop(t, None)
            self.hits.pop(t, None)

    def mark_stale(self):
        """Mark low-activity entries as stale (-1) without deleting."""
        count = 0
        for t in list(self.data.keys()):
            idle = self.tick - self.active.get(t, 0)
            pot = self.potency.get(t, 0)
            if idle > PURGE_AFTER + HALF_CYCLE_LENGTH and pot == 0:
                self.active[t] = self.tick - PURGE_AFTER * 2
                self.potency[t] = -1
                count += 1
        return count

    def compact(self):
        """Compact store: mark stale + purge."""
        if self.size < COMPACT_AT:
            return 0
        n = self.mark_stale()
        self.purge_stale()
        return n

    def status(self) -> dict:
        return {
            'total': self.size,
            'active': self.active_count,
            'tick': self.tick,
            'stale': sum(1 for p in self.potency.values() if p == -1),
            'tier2': sum(1 for p in self.potency.values() if p >= 2),
        }

    # ========== Persistence ==========

    def save(self, filepath: str) -> None:
        """Save store state to JSON with wall-clock timestamp."""
        from datetime import datetime
        state = {
            'data': self.data,
            'active': self.active,
            'hits': self.hits,
            'potency': self.potency,
            'tick': self.tick,
            'saved_at': datetime.now().isoformat(),
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def load(self, filepath: str) -> bool:
        """Load store state. Advances tick by elapsed real hours.
        Returns False on first run (no save file yet)."""
        from datetime import datetime
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                state = json.load(f)
            self.data = {k: int(v) for k, v in state['data'].items()}
            self.active = {k: int(v) for k, v in state['active'].items()}
            self.hits = {k: int(v) for k, v in state['hits'].items()}
            self.potency = {k: int(v) for k, v in state['potency'].items()}
            old_tick = int(state['tick'])

            # Compensate offline time: 1 tick ≈ 1 hour, capped at 72
            saved_at = state.get('saved_at', '')
            if saved_at:
                try:
                    saved_dt = datetime.fromisoformat(saved_at)
                    elapsed = (datetime.now() - saved_dt).total_seconds() / 3600
                    extra = max(1, min(int(elapsed), 72))
                    self.tick = old_tick + extra
                except ValueError:
                    self.tick = old_tick + 1
            else:
                self.tick = old_tick + 1

            return True
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            return False
