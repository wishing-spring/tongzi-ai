"""
童子 v0.5 · balancer & polarizer
==================================
12 polarity flags (6 yang + 6 yin). Auto-balance.
Cluster detection via union-find on Hamming distance.
"""
from tongzi_core import BitStore
from tongzi_constants import *

class Balancer:
    """12-flag polarity balancer with auto-correction."""

    YANG_NAMES = ('聚', '配', '顺', '升', '生', '连')
    YIN_NAMES  = ('散', '破', '逆', '降', '溯', '断')

    def __init__(self, store: BitStore):
        self.store = store
        self.yang_flags = [False] * 6
        self.yin_flags  = [False] * 6

    # ========== Flag state ==========

    @property
    def yang_count(self) -> int:
        return sum(self.yang_flags)

    @property
    def yin_count(self) -> int:
        return sum(self.yin_flags)

    @property
    def balance_gap(self) -> int:
        return self.yang_count - self.yin_count

    def activate_yang(self, idx: int) -> bool:
        if self.balance_gap >= BALANCE_THRESHOLD:
            return False
        self.yang_flags[idx] = True
        return True

    def activate_yin(self, idx: int) -> bool:
        if self.balance_gap <= -BALANCE_THRESHOLD:
            return False
        self.yin_flags[idx] = True
        return True

    def deactivate_yang(self, idx: int):
        self.yang_flags[idx] = False

    def deactivate_yin(self, idx: int):
        self.yin_flags[idx] = False

    @property
    def status(self) -> dict:
        return {
            'yang': ''.join('1' if s else '0' for s in self.yang_flags),
            'yin':  ''.join('1' if s else '0' for s in self.yin_flags),
            'gap':  self.balance_gap,
        }

    # ========== Auto-balance ==========

    def auto_balance(self):
        """Force-correct if gap exceeds threshold."""
        diff = self.balance_gap
        if abs(diff) < AUTO_BALANCE_AT:
            return False

        if diff > 0:  # yang-heavy → deactivate yang, activate yin
            for i in [4, 5, 3, 2, 1, 0]:
                if self.yang_flags[i]:
                    self.deactivate_yang(i)
                    diff -= 1
                    if diff < AUTO_BALANCE_AT:
                        break
            for i in [0, 5, 3]:
                if not self.yin_flags[i] and self.balance_gap >= AUTO_BALANCE_AT:
                    self.activate_yin(i)
        else:  # yin-heavy → deactivate yin, activate yang
            for i in [4, 5, 3, 2, 1, 0]:
                if self.yin_flags[i]:
                    self.deactivate_yin(i)
                    diff += 1
                    if abs(diff) < AUTO_BALANCE_AT:
                        break
            for i in [0, 5, 3]:
                if not self.yang_flags[i] and self.balance_gap <= -AUTO_BALANCE_AT:
                    self.activate_yang(i)
        return True

    # ========== Yang anchors ==========

    def find_clusters(self, threshold: int = SIMILARITY_TIGHT) -> list[list[str]]:
        """Union-find clustering by Hamming distance ≤ threshold."""
        tags = list(self.store.data.keys())
        n = len(tags)
        if n < 2:
            return []
        parent = {t: t for t in tags}
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        def union(x, y):
            rx, ry = find(x), find(y)
            if rx != ry:
                parent[rx] = ry
        for i in range(n):
            for j in range(i + 1, n):
                if self.store.potency.get(tags[i], 0) == -1:
                    continue
                if self.store.potency.get(tags[j], 0) == -1:
                    continue
                d = self.store.hamming(self.store.data[tags[i]],
                                       self.store.data[tags[j]])
                if d <= threshold:
                    union(tags[i], tags[j])
        groups = {}
        for t in tags:
            r = find(t)
            groups.setdefault(r, []).append(t)
        return [g for g in groups.values() if len(g) >= 2]

    def match_pattern(self, target_vec: int, threshold: int = SIMILARITY_NEAR) -> list[str]:
        """Find pattern-matching vectors."""
        return self.store.find_nearest(target_vec, threshold)

    def cascade_activate(self, idx: int) -> list[int]:
        """Activate one yang anchor, cascade to adjacent ones."""
        activated = []
        if self.activate_yang(idx):
            activated.append(idx)
        for offset in [-1, 1]:
            nb = (idx + offset) % 6
            if not self.yang_flags[nb]:
                self.yang_flags[nb] = True
                activated.append(nb)
        return activated

    def entropy_scan(self) -> dict:
        """Scan vector population distribution across all entries."""
        import math
        tags = [t for t in self.store.data
                if self.store.potency.get(t, 0) != -1]
        if not tags:
            return {'total': 0, 'avg_hamming': 0}
        vectors = [self.store.data[t] for t in tags]
        dists = []
        for i in range(len(vectors)):
            for j in range(i + 1, len(vectors)):
                dists.append(self.store.hamming(vectors[i], vectors[j]))
        avg = sum(dists) / len(dists) if dists else 0
        return {'total': len(tags), 'avg_hamming': round(avg, 2)}

    def rank_by_centrality(self) -> list[tuple[str, float]]:
        """Rank tags by average Hamming distance to all others (lower = more central)."""
        tags = [t for t in self.store.data
                if self.store.potency.get(t, 0) != -1]
        if len(tags) < 2:
            return [(t, 0.0) for t in tags]
        scores = []
        for t in tags:
            vt = self.store.data[t]
            total = sum(self.store.hamming(vt, self.store.data[o])
                        for o in tags if o != t)
            avg = total / (len(tags) - 1)
            scores.append((t, round(avg, 2)))
        scores.sort(key=lambda x: x[1])
        return scores

    # ========== Yin anchors ==========

    def disperse_check(self, threshold: int = SIMILARITY_FAR) -> list[str]:
        """Find vectors that are far from all clusters (dispersed)."""
        from collections import Counter
        tags = [t for t in self.store.data
                if self.store.potency.get(t, 0) != -1]
        if len(tags) < 3:
            return []
        neighbor_counts = {}
        for t in tags:
            vt = self.store.data[t]
            count = sum(1 for o in tags if o != t and
                        self.store.hamming(vt, self.store.data[o]) <= SIMILARITY_NEAR)
            neighbor_counts[t] = count
        avg_neighbors = sum(neighbor_counts.values()) / len(neighbor_counts)
        return [t for t, c in neighbor_counts.items() if c < avg_neighbors * 0.5]

    def detect_anomalies(self, threshold: int = SIMILARITY_ALIEN) -> list[str]:
        """Find vectors anomalous to the entire population."""
        tags = [t for t in self.store.data
                if self.store.potency.get(t, 0) != -1]
        if len(tags) < 2:
            return []
        anomalies = []
        for t in tags:
            vt = self.store.data[t]
            others = [o for o in tags if o != t]
            min_d = min(self.store.hamming(vt, self.store.data[o]) for o in others)
            if min_d >= threshold:
                anomalies.append(t)
        return anomalies

    # ========== Main cycle ==========

    def cycle(self):
        """One scheduling cycle: tick → schedule → execute → maintain."""
        self.store.advance_tick()
        self._schedule()
        self._execute()

        # Gentle cleanup only when above rest threshold
        if self.store.size > REST_AT:
            self.store.purge_stale()

        # Periodic mark-stale
        if self.store.tick % CYCLE_LENGTH == 0:
            self.store.mark_stale()

        # Periodic compact
        if self.store.tick % (CYCLE_LENGTH * 3) == 0:
            self.store.compact()

    def _schedule(self):
        """Decide which anchors to activate this cycle."""
        tick = self.store.tick

        # Yang activation pattern (phase-dependent)
        yang_patterns = [
            [0],           # tick%6==0: gather
            [0, 1],        # tick%6==1: gather+pair
            [1, 2],        # tick%6==2: pair+flow
            [2, 3],        # tick%6==3: flow+rise
            [3, 4],        # tick%6==4: rise+generate
            [4, 5],        # tick%6==5: generate+link
        ]
        for idx in yang_patterns[tick % 6]:
            self.activate_yang(idx)

        # Yin activation pattern (complementary)
        yin_patterns = [
            [0],           # scatter
            [0, 1],        # scatter+break
            [1, 2],        # break+reverse
            [2, 3],        # reverse+descend
            [3, 4],        # descend+trace
            [4, 5],        # trace+cut
        ]
        for idx in yin_patterns[tick % 6]:
            self.activate_yin(idx)

        # Deactivate stale anchors periodically
        if tick % DECAY_INTERVAL == 0:
            for i in range(6):
                if self.yang_flags[i]:
                    self.deactivate_yang(i)
            for i in range(6):
                if self.yin_flags[i]:
                    self.deactivate_yin(i)

    def _execute(self):
        """Execute active anchors: run yang/yin operations on store."""
        # This is the bridge between scheduling and actual vector operations.
        # Active yang anchors trigger clustering & matching.
        # Active yin anchors trigger dispersion & anomaly detection.
        pass  # Operations are called explicitly by Responder as needed.
