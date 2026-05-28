# -*- coding: utf-8 -*-
"""Child Experience Pool v8.1 — thought-chain sedimentation · experience-loop adjustment · 4-pool classification"""
import os, sys, time, random
from .guayuan import MASK28, hamming, gua_hash, xor_reduce, random_gua

# ── experience entry ──

class ExperienceEntry:
    """One experience = complete sedimentation of one thought chain"""
    __slots__ = ('id', 'gua_chain', 'words', 'rules', 'gate',
                 'tianyuan_gua', 'tianyuan_text', 'success', 'tick', 'reuse')

    def __init__(self, eid: int, gua_chain: list, words: list, rules: list,
                 gate: str, tianyuan_gua: int, tianyuan_text: str,
                 success: bool, tick: int):
        self.id = eid
        self.gua_chain = gua_chain        # cell vector sequence [int, ...]
        self.words = words                 # world-layer words
        self.rules = rules                 # rule name
        self.gate = gate                   # gate result
        self.tianyuan_gua = tianyuan_gua   # focal anchor vector
        self.tianyuan_text = tianyuan_text # raw input
        self.success = success             # valid experience
        self.tick = tick
        self.reuse = 0                     # reuse count

    def chain_hash(self) -> int:
        """Hash of vector chain (for fast dedup)"""
        return xor_reduce(self.gua_chain) if self.gua_chain else 0


# ── 4 eco-pools ──

class EcoPool:
    """An eco-pool: classified experience storage"""
    __slots__ = ('name', 'entries', 'max_size')

    def __init__(self, name: str, max_size: int = 256):
        self.name = name
        self.entries: list[ExperienceEntry] = []
        self.max_size = max_size

    def add(self, entry: ExperienceEntry):
        self.entries.append(entry)
        if len(self.entries) > self.max_size:
            # keep high-reuse entries
            self.entries.sort(key=lambda e: e.reuse, reverse=True)
            self.entries = self.entries[:self.max_size]

    def query_by_chain(self, gua_chain: list[int], top_n: int = 5) -> list:
        """Query similar experiences by vector chain"""
        if not gua_chain:
            return []
        target = xor_reduce(gua_chain)
        scored = []
        for e in self.entries:
            d = hamming(target, e.chain_hash())
            scored.append((28 - d, e))  # 28-d = similarity
        scored.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in scored[:top_n]]

    def query_by_tianyuan(self, tianyuan_gua: int, top_n: int = 5) -> list:
        """Query by focal anchor vector"""
        scored = []
        for e in self.entries:
            d = hamming(tianyuan_gua, e.tianyuan_gua)
            scored.append((28 - d, e))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in scored[:top_n]]

    def size(self) -> int:
        return len(self.entries)


# ── child experience pool master ──

class TongziExperience:
    """Child experience pool: 4-pool classification · sedimentation · query · feedback"""

    POOL_NAMES = {
        'success': 'success exp',     # 经过各层验证的有效经验
        'pattern': '♥模式经验',     # 反复出现的思维模式
        'insight': '♦灵感经验',     # 第九卦触发的跳跃经验
        'common':  '♣常识经验',     # 世界层+规则树验证的通用经验
    }

    def __init__(self):
        self.pools: dict[str, EcoPool] = {
            k: EcoPool(v) for k, v in self.POOL_NAMES.items()
        }
        self.next_id = 0
        self.tick = 0

    # ── 沉淀 ──

    def deposit(self, gua_chain: list[int], words: list[str],
                rules: list[str], gate: str,
                tianyuan_gua: int, tianyuan_text: str,
                success: bool = True, jiugua_used: bool = False):
        """沉淀一条思维链路经验"""
        self.tick += 1
        entry = ExperienceEntry(
            self.next_id, gua_chain, words, rules,
            gate, tianyuan_gua, tianyuan_text,
            success, self.tick)
        self.next_id += 1

        # 按特征分池
        if success and gate in ('GUIDE', 'ACCEPT'):
            self.pools['success'].add(entry)
        if success and rules:
            self.pools['pattern'].add(entry)
        if jiugua_used:
            self.pools['insight'].add(entry)
        if words and rules:
            self.pools['common'].add(entry)

    # ── 查询 ──

    def query(self, gua_chain: list[int],
              tianyuan_gua: int,
              pool_names: list[str] = None) -> dict:
        """
        查询相似经验
        返回: {pool_name: [ExperienceEntry, ...]}
        """
        if pool_names is None:
            pool_names = ['success', 'pattern', 'common']

        results = {}
        for pn in pool_names:
            if pn not in self.pools:
                continue
            pool = self.pools[pn]

            # 综合查询：卦元链相似 + 天元相似
            chain_matches = pool.query_by_chain(gua_chain, top_n=3)
            tianyuan_matches = pool.query_by_tianyuan(tianyuan_gua, top_n=3)

            # 合并去重
            seen = set()
            merged = []
            for e in chain_matches + tianyuan_matches:
                if e.id not in seen:
                    seen.add(e.id)
                    merged.append(e)
            results[pn] = merged[:5]

        return results

    # ── 参与调整 ──

    def participate(self, raw_chain: list[int],
                    tianyuan_gua: int,
                    current_words: list[str],
                    current_rules: list[str]) -> dict:
        """
        经验参与调整原始思维链：
        - 查询相似经验
        - 如果经验链的词/规则和当前一致→增强
        - 如果经验链有更好结果→建议替换
        """
        results = self.query(raw_chain, tianyuan_gua)

        adjustments = {
            'boost_words': [],      # 经验中反复出现的词
            'boost_rules': [],      # 经验中反复触发的规则
            'suggest_chain': [],    # 建议的替代卦元链
            'confidence': 0.0,      # 对当前链的信心
        }

        all_matches = []
        for pool_name, entries in results.items():
            all_matches.extend(entries)

        if not all_matches:
            return adjustments

        # 统计经验中的常见词和规则
        word_freq = {}
        rule_freq = {}
        chain_votes = {}

        for e in all_matches:
            e.reuse += 1  # 复用计数
            for w in e.words:
                word_freq[w] = word_freq.get(w, 0) + 1
            for r in e.rules:
                rule_freq[r] = rule_freq.get(r, 0) + 1
            ch = e.chain_hash()
            chain_votes[ch] = chain_votes.get(ch, 0) + e.reuse

        # 去掉当前已有的
        boost_words = [w for w, c in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
                       if w not in current_words][:5]
        boost_rules = [r for r, c in sorted(rule_freq.items(), key=lambda x: x[1], reverse=True)
                       if r not in current_rules][:3]

        # 信心 = 匹配经验数 / 总经验池
        total_entries = sum(p.size() for p in self.pools.values())
        confidence = min(1.0, len(all_matches) / max(1, total_entries) * 5)

        # 建议替代链（被复用最多的）
        if chain_votes:
            best_chain_hash = max(chain_votes, key=chain_votes.get)
            for e in all_matches:
                if e.chain_hash() == best_chain_hash:
                    adjustments['suggest_chain'] = e.gua_chain
                    break

        adjustments['boost_words'] = boost_words
        adjustments['boost_rules'] = boost_rules
        adjustments['confidence'] = round(confidence, 3)

        return adjustments

    # ── 固化经验 ──

    def solidify(self, min_reuse: int = 3) -> int:
        """固化高复用经验（标记为永久保留）"""
        count = 0
        for pool in self.pools.values():
            for e in pool.entries:
                if e.reuse >= min_reuse and not e.success:
                    e.success = True
                    count += 1
        return count

    # ── 快照 ──

    def snapshot(self) -> dict:
        return {
            'total': sum(p.size() for p in self.pools.values()),
            'pools': {k: p.size() for k, p in self.pools.items()},
            'solidified': sum(1 for p in self.pools.values()
                            for e in p.entries if e.success),
        }

    # ── 自我收割：insight签名管理 ──

    def __init_insight_tracker(self):
        if not hasattr(self, '_insights'):
            self._insights: dict[str, dict] = {}  # sig → {count, data, crystallized}

    def add_insight(self, sig: str, data: dict):
        """记录碰撞签名→insight池"""
        self.__init_insight_tracker()
        if sig in self._insights:
            self._insights[sig]['count'] += 1
            self._insights[sig]['data'] = data
            # 累积输入
            all_inputs = self._insights[sig].get('all_inputs', [])
            all_inputs.append(data.get('input', ''))
            self._insights[sig]['all_inputs'] = all_inputs
        else:
            self._insights[sig] = {
                'count': 1,
                'data': data,
                'crystallized': False,
                'all_inputs': [data.get('input', '')],
            }

    def count_insight(self, sig: str) -> int:
        """签名出现次数"""
        self.__init_insight_tracker()
        entry = self._insights.get(sig, {})
        return entry.get('count', 0)

    def mark_crystallized(self, sig: str):
        """标记已结晶"""
        self.__init_insight_tracker()
        if sig in self._insights:
            self._insights[sig]['crystallized'] = True

    def get_insight_inputs(self, sig: str) -> list[str]:
        """获取某个签名下的所有输入文本"""
        self.__init_insight_tracker()
        entry = self._insights.get(sig, {})
        # all_inputs 在顶层，不在 data 内
        return entry.get('all_inputs', [])

    def set_insight_attr(self, sig: str, key: str, value):
        """设置insight属性"""
        self.__init_insight_tracker()
        if sig in self._insights:
            self._insights[sig][key] = value

    def is_crystallized(self, sig: str) -> bool:
        """是否已结晶"""
        self.__init_insight_tracker()
        return self._insights.get(sig, {}).get('crystallized', False)
