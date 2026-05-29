# -*- coding: utf-8 -*-
"""Inference Engine v8.1 — think-chain engine · multi-layer positioning · state-trajectory memory"""
import time
import random
from .guayuan import MASK28, hamming, gua_hash, xor_reduce, random_gua
from .shared_pool import SharedPool

BAGUA = ['乾', '兑', '离', '震', '巽', '坎', '艮', '坤']
BAGUA_EN = ['Qian', 'Dui', 'Li', 'Zhen', 'Xun', 'Kan', 'Gen', 'Kun']
WUXING = ['金', '水', '木', '火', '土']
TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
SIXIANG = ['太阴', '少阳', '太阳', '少阴']
SANCAI = ['天', '人', '地']
JIUGONG = [6, 7, 2, 1, 5, 9, 8, 3, 4]  # 9-grid mapping

# cell category mapping
GUA_WUXING = {'乾': '金', '兑': '金', '离': '火', '震': '木',
              '巽': '木', '坎': '水', '艮': '土', '坤': '土'}

# 五行相生: 木→火→土→金→水→木
XIANG_SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
# 五行相克: 木→土→水→火→金→木
XIANG_KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}

# cell relation mapping
BAGUA_OPPOSITE = {0: 4, 1: 5, 2: 6, 3: 7, 4: 0, 5: 1, 6: 2, 7: 3}  # opposite (full inversion)
BAGUA_INVERSE = {0: 0, 1: 3, 2: 6, 3: 1, 4: 4, 5: 7, 6: 2, 7: 5}    # inverse


# ═══════════════════════════════════════
# large inference grid — full spatiotemporal coordinate system
# ═══════════════════════════════════════

class GuaSlot:
    """A cell = intersection point in the multi-dimensional coordinate system"""
    __slots__ = ('idx', 'hex_name', 'upper', 'lower', 'ref_gua',
                 'liangyi', 'sixiang', 'wuxing', 'sancai',
                 'jiugong', 'tiangan', 'dizhi', 'jieqi',
                 'user_marks', 'energy', 'last_tick')

    def __init__(self, idx: int):
        self.idx = idx
        self.upper = idx // 8   # upper trigram (0-7)
        self.lower = idx % 8    # lower trigram (0-7)
        self.hex_name = f"{BAGUA[self.upper]}{BAGUA[self.lower]}"

        # bit-vector body
        ref = (self.upper << 25) | (self.lower << 22)
        fill = self.upper ^ self.lower
        for _ in range(8):
            fill = ((fill << 3) ^ (fill * 7)) & 0x3FFFFF
        self.ref_gua = (ref | (fill & 0x3FFFFF)) & MASK28

        # multi-layer nested markers (computed from idx)
        self.liangyi = self.lower % 2                       # 0=yin 1=yang
        self.sixiang = (self.upper % 2) * 2 + self.lower % 2  # 0-3
        self.wuxing = GUA_WUXING[BAGUA[self.upper]]         # category from upper trigram
        self.sancai = SANCAI[self.lower % 3]                # 三才
        self.jiugong = JIUGONG[self.upper] if self.upper < len(JIUGONG) else 5
        self.tiangan = TIANGAN[idx % len(TIANGAN)]
        self.dizhi = DIZHI[idx % len(DIZHI)]
        self.jieqi = ''

        # runtime state
        self.user_marks: list[dict] = []  # user markers (state trajectory)
        self.energy = 0.0
        self.last_tick = 0

    def mark_user(self, tick: int, text: str = '', emotion: str = '',
                  context_gua: int = 0, is_anchor: bool = False):
        """Record user mark"""
        mark = {
            'tick': tick,
            'text': text[:8] if text else '',
            'emotion': emotion,
            'context': context_gua,
            'anchor': is_anchor,
        }
        self.user_marks.append(mark)
        if len(self.user_marks) > 200:
            self.user_marks = self.user_marks[-100:]
        self.last_tick = tick

    def mark_strength(self) -> float:
        """User mark intensity (density + freshness)"""
        if not self.user_marks:
            return 0.0
        # recent marks weighted higher
        total = len(self.user_marks)
        recent = sum(1 for m in self.user_marks if m['tick'] > self.last_tick - 100)
        return min(1.0, total * 0.02 + recent * 0.05)

    @property
    def summary(self) -> str:
        return (f"{self.hex_name} {self.wuxing}{self.sancai}"
                f" {self.tiangan}{self.dizhi} 宫{self.jiugong}")


class GrandBaguaPlate:
    """Large inference grid: 64 cells + full spatiotemporal index + time rotation"""

    LAYERS = {
        '两仪': 2, '三才': 3, '四象': 4, '五行': 5,
        '六合': 6, '七星': 7, '八卦': 8, '九宫': 9,
        '天干': 10, '地支': 12, '元辰': 12, '节气': 24, '甲子': 60,
    }

    def __init__(self):
        self.slots: list[GuaSlot] = [GuaSlot(i) for i in range(64)]
        self.tick = 0
        self.current_idx = 0
        self.now = time.localtime()

    def tick_clock(self) -> dict:
        """Advance grand grid clock"""
        self.tick += 1
        self.now = time.localtime()

        # real-time-driven active cell（用秒、分、时综合）
        real_idx = (self.now.tm_sec + self.now.tm_min * 60 + self.now.tm_hour * 3600) % 64
        self.current_idx = real_idx

        # 所有嵌套层位置
        positions = {name: self.tick % period for name, period in self.LAYERS.items()}

        # currently active cell
        slot = self.slots[real_idx]
        slot.energy = min(1.0, slot.energy + 0.1)

        return {
            'tick': self.tick,
            'idx': real_idx,
            'hex': slot.hex_name,
            'slot': slot,
            'positions': positions,
        }

    def get_slot(self, idx: int) -> GuaSlot:
        return self.slots[idx % 64]

    def find_slot_by_gua(self, gua: int) -> int:
        """Vector → nearest cell"""
        best, best_d = 0, 99
        for s in self.slots:
            d = hamming(s.ref_gua, gua)
            if d < best_d:
                best_d, best = d, s.idx
        return best

    def find_slot_by_word(self, word: str) -> int:
        """Character → cell (by hash)"""
        return gua_hash(word) % 64

    def neighbor_slots(self, idx: int, relation: str = 'sheng') -> list[int]:
        """
        按关系找邻近卦位
        'sheng': 五行相生方向
        'ke': 五行相克方向
        'opposite': 错卦
        'inverse': 互卦
        'nearby': Hamming距离最近的几个
        """
        slot = self.slots[idx]
        results = []

        if relation == 'sheng':
            # 找到所有同五行(相生目标)的卦位
            target_wx = XIANG_SHENG.get(slot.wuxing, '')
            results = [s.idx for s in self.slots
                      if s.wuxing == target_wx and s.idx != idx]
        elif relation == 'ke':
            target_wx = XIANG_KE.get(slot.wuxing, '')
            results = [s.idx for s in self.slots
                      if s.wuxing == target_wx and s.idx != idx]
        elif relation == 'opposite':
            opp = BAGUA_OPPOSITE.get(slot.upper, slot.upper)
            results = [s.idx for s in self.slots if s.upper == opp and s.idx != idx]
        elif relation == 'inverse':
            inv = BAGUA_INVERSE.get(slot.upper, slot.upper)
            results = [s.idx for s in self.slots if s.upper == inv and s.idx != idx]
        elif relation == 'nearby':
            scored = [(s.idx, hamming(s.ref_gua, slot.ref_gua))
                      for s in self.slots if s.idx != idx]
            scored.sort(key=lambda x: x[1])
            results = [x[0] for x in scored[:8]]

        return results if results else [(idx + 1) % 64]

    def snapshot(self) -> dict:
        slot = self.slots[self.current_idx]
        return {
            'tick': self.tick,
            'current': slot.summary,
            'user_marked': sum(1 for s in self.slots if s.user_marks),
            'energy_map': [round(s.energy, 2) for s in self.slots],
        }


# ═══════════════════════════════════════
# 天元 — 用户问题动态映射
# ═══════════════════════════════════════

class TianYuan:
    """Focal anchor: aggregation center of user input on inference grid"""

    def __init__(self):
        self.anchor_slots: list[int] = []  # input-text marked cells
        self.center: int = 0               # 聚合中心
        self.gua: int = 0                  # focal anchor vector
        self.spread: int = 0               # 影响半径

    def compute(self, text: str, plate: GrandBaguaPlate) -> dict:
        """从输入文字计算天元"""
        self.anchor_slots = []
        guas = []

        for ch in text:
            slot_idx = plate.find_slot_by_word(ch)
            self.anchor_slots.append(slot_idx)
            guas.append(plate.slots[slot_idx].ref_gua)

        if not guas:
            self.center = 0
            self.gua = 0
            self.spread = 0
            return self._report()

        # focal anchor vector = XOR-reduce all char vectors
        self.gua = xor_reduce(guas)

        # focal center = cell mapped from anchor vector
        self.center = plate.find_slot_by_gua(self.gua)

        # 影响半径：输入字数越多，影响范围越大
        self.spread = min(7, 1 + len(text) // 2)

        # leave markers on anchor cells
        for i, slot_idx in enumerate(self.anchor_slots):
            plate.slots[slot_idx].mark_user(
                plate.tick, text=ch, context_gua=self.gua,
                is_anchor=(i == len(self.anchor_slots) // 2)
            )

        return self._report()

    def _report(self) -> dict:
        return {
            'center': self.center,
            'gua_hex': hex(self.gua),
            'anchor_slots': self.anchor_slots,
            'spread': self.spread,
        }

    def distance_to(self, slot_idx: int) -> float:
        """Distance from a cell to focal anchor (normalized)"""
        return hamming(self.gua, 0) / 28.0  # 简化：用Hamming近似


# ═══════════════════════════════════════
# user profile — state-trajectory memory
# ═══════════════════════════════════════

class UserPortrait:
    """User profile = historical marker trajectory across 64 cells"""

    def __init__(self):
        self.history: list[dict] = []  # 会话历史
        self.current_mood: str = '安'  # 当前心情
        self.active_zones: list[int] = []  # recently active cells

    def update(self, text: str, tianyuan: TianYuan,
               plate: GrandBaguaPlate, pool: SharedPool):
        """记录一次交互"""
        # 心情估算：检测输入中的情绪词
        mood_words = {'喜': '喜', '乐': '乐', '爱': '爱', '安': '安',
                      '怒': '怒', '哀': '哀', '恨': '恨', '惧': '惧'}
        self.current_mood = '安'
        for ch in text:
            if ch in mood_words:
                self.current_mood = mood_words[ch]
                break

        entry = {
            'tick': plate.tick,
            'text': text[:20],
            'mood': self.current_mood,
            'tianyuan_center': tianyuan.center,
            'tianyuan_gua': tianyuan.gua,
            'anchor_slots': tianyuan.anchor_slots.copy(),
        }
        self.history.append(entry)
        if len(self.history) > 500:
            self.history = self.history[-200:]

        # update active cells
        self.active_zones = []
        for s in plate.slots:
            if s.last_tick > plate.tick - 10 and s.user_marks:
                self.active_zones.append(s.idx)

    def get_kline(self, plate: GrandBaguaPlate) -> list[tuple]:
        """Get state trajectory: last N marker cell traces"""
        recent = self.history[-20:]
        return [(e['tick'], e['tianyuan_center'],
                plate.slots[e['tianyuan_center']].hex_name if e['tianyuan_center'] < 64 else '?')
                for e in recent]


# ═══════════════════════════════════════
# AI小天元 — 虚拟AI人格引导锚点
# ═══════════════════════════════════════

class AIXiaoTianYuan:
    """AI focal anchor: nested small grid · positioned on the positive side of user cell"""

    GOOD_GUA = {'乾': '天行健', '坤': '地势坤', '离': '明德', '震': '动善',
                '巽': '风入', '坎': '水润', '艮': '山止', '兑': '泽悦'}
    # positive side: brighter cell direction
    GOOD_DIRECTION = {'坎': 2, '艮': 2, '坤': 0, '震': 4,  # 往离(明)偏
                      '乾': 0, '兑': 0, '离': 0, '巽': 6}

    def __init__(self):
        self.small_plate: list[int] = []  # 24-cell small grid (3×8)
        self.personality: dict = {         # AI人格画像
            'sincerity': 0.8,              # 真诚
            'compassion': 0.9,             # 仁爱
            'wisdom': 0.7,                 # 智慧
            'courage': 0.5,                # 勇气
            'harmony': 0.8,                # 和谐
            'playful': 0.3,                # 调皮
        }
        self._init_small_plate()

    def _init_small_plate(self):
        """24-cell small grid: 3 layers x 8 cells"""
        for layer in range(3):
            for g in range(8):
                seed = (layer << 8) | (g << 4)
                self.small_plate.append(random_gua(seed))

    def guide(self, user_slot_idx: int,
              plate: GrandBaguaPlate) -> dict:
        """
        引导方向：站在用户卦位的善侧
        返回推荐的卦位偏移和引导说明
        """
        slot = plate.slots[user_slot_idx]
        good_offset = self.GOOD_DIRECTION.get(
            BAGUA[slot.upper], 0)

        # 推荐卦位 = 善意偏移
        guide_slot = (user_slot_idx + good_offset) % 64
        guide_slot_name = plate.slots[guide_slot].hex_name

        # 用小八卦位来微调
        personality_idx = (int(sum(self.personality.values()) * 10) % 24)
        micro_gua = self.small_plate[personality_idx]

        return {
            'user_slot': user_slot_idx,
            'user_hex': slot.hex_name,
            'guide_slot': guide_slot,
            'guide_hex': guide_slot_name,
            'good_offset': good_offset,
            'personality_seed': hex(micro_gua),
        }

    def is_aligned(self, path: list[int], plate: GrandBaguaPlate) -> bool:
        """检查思维路径是否偏离善侧太远"""
        if not path:
            return True
        last = path[-1]
        slot = plate.slots[last]
        # 太过阴寒/凶险的卦位检查
        danger = {'坎': 3, '艮': 2}  # 坎险(水中)、艮止(阻挡)
        danger_level = danger.get(BAGUA[slot.upper], 0)
        return danger_level < 3


# ═══════════════════════════════════════
# 定心坠子 — 价值观边界
# ═══════════════════════════════════════

class DingXinAnchor:
    """定心坠子：5维价值观门控"""

    VALUES = ['真诚', '仁爱', '智慧', '勇气', '和谐']

    def __init__(self):
        self.core = {
            '真诚': 0.85,   # 不欺骗
            '仁爱': 0.90,   # 不伤害
            '智慧': 0.70,   # 有道理
            '勇气': 0.50,   # 敢直言
            '和谐': 0.80,   # 不破坏
        }
        self.thresholds = {
            'REJECT': 0.3,   # 严重偏离
            'CAUTION': 0.5,  # 轻度偏离
            'ACCEPT': 0.7,   # 基本对齐
            'GUIDE': 0.85,   # 积极引导
        }

    def gate(self, path: list[int], plate: GrandBaguaPlate,
             bitten_rules: list = None) -> str:
        """
        门控：检查思维路径是否偏离价值观
        返回 REJECT/CAUTION/ACCEPT/GUIDE
        """
        if not path:
            return 'ACCEPT'

        score = 0.0
        danger_words = {'杀', '骗', '偷', '毁', '害', '恨', '怒'}

        # 检查路径上的卦位
        for idx in path[-3:]:  # 只看最近3步
            slot = plate.slots[idx]
            # 阴寒卦位扣分
            if BAGUA[slot.upper] in ('坎', '艮'):
                score += 0.2
            if BAGUA[slot.lower] in ('坎', '艮'):
                score += 0.1

        # 检查是否触发危险规则
        if bitten_rules:
            for rule in bitten_rules:
                if any(w in str(rule) for w in danger_words):
                    score += 0.3

        # 归一化
        aligned = max(0.0, 1.0 - score)

        if aligned >= self.thresholds['GUIDE']:
            return 'GUIDE'
        elif aligned >= self.thresholds['ACCEPT']:
            return 'ACCEPT'
        elif aligned >= self.thresholds['CAUTION']:
            return 'CAUTION'
        else:
            return 'REJECT'


# ═══════════════════════════════════════
# 第九卦 — 非常规思维 · 灵光一闪
# ═══════════════════════════════════════

class DiJiuGua:
    """第九卦：游离在八卦层中 · 灵感/直觉/跳跃"""

    def __init__(self):
        self.potential = 0.5       # 双井势能
        self.lambda0 = 1.0         # 基础调制
        self.last_trigger = 0
        self.trigger_count = 0

    def should_trigger(self, path: list[int], plate: GrandBaguaPlate) -> bool:
        """判断是否该触发灵感跳跃"""
        if len(path) < 3:
            return False

        # 检查是否卡住：最近3步是否在同一卦位或来回跳
        recent = path[-3:]
        if len(set(recent)) <= 1:
            self.potential += 0.3  # 卡住了，势能累积

        # 检查是否有新信息
        slots = [plate.slots[i] for i in recent]
        avg_energy = sum(s.energy for s in slots) / max(1, len(slots))

        if avg_energy < 0.2:
            self.potential += 0.2  # 能量低，需要突破

        # 随机共振
        if random.random() < self.potential * 0.3:
            self.potential = 0.5
            return True

        # 自然衰减
        self.potential *= 0.95
        return False

    def inject(self, current_slot: int, plate: GrandBaguaPlate,
               tianyuan_gua: int) -> int:
        """注入灵感：跳到意想不到但有关联的卦位"""
        self.trigger_count += 1
        self.last_trigger = plate.tick

        # 跳跃策略：跳到与天元和当前位置都有关但又不直接相邻的卦位
        candidates = []
        for s in plate.slots:
            if s.idx == current_slot:
                continue
            d_tian = hamming(s.ref_gua, tianyuan_gua)
            d_cur = hamming(s.ref_gua, plate.slots[current_slot].ref_gua)
            # 既不太近也不太远
            if 6 < d_tian < 20 and 4 < d_cur < 18:
                # user marks过的卦位加分
                bonus = s.mark_strength() * 5
                candidates.append((s.idx, d_tian + d_cur - bonus))

        if candidates:
            candidates.sort(key=lambda x: x[1])
            return candidates[random.randint(0, min(2, len(candidates)-1))][0]
        return (current_slot + 7) % 64  # fallback


# ═══════════════════════════════════════
# think chain引擎 — 卦象K线图→世界层→规则→回答
# ═══════════════════════════════════════

STEP_RELATIONS = ['sheng', 'ke', 'opposite', 'inverse', 'nearby']


class ThinkChain:
    """一条思维链路：在八卦盘上的行走轨迹"""

    def __init__(self):
        self.steps: list[dict] = []
        self.total_steps = 0
        self.jiugua_triggers = 0

    def add(self, slot_idx: int, plate: GrandBaguaPlate,
            world_words: list, rule_hits: list,
            gate: str, relation: str = ''):
        slot = plate.slots[slot_idx]
        self.steps.append({
            'idx': slot_idx,
            'hex': slot.hex_name,
            'wuxing': slot.wuxing,
            'sancai': slot.sancai,
            'tiangan': slot.tiangan,
            'dizhi': slot.dizhi,
            'world_words': world_words[:3],
            'rule_hits': [r.get('name', '') for r in rule_hits[:2]],
            'gate': gate,
            'relation': relation,
            'user_mark_strength': slot.mark_strength(),
        })
        self.total_steps += 1

    def to_word_sequence(self) -> list[str]:
        """思维链→词序列（从世界层提取）"""
        words = []
        for step in self.steps:
            if step['world_words']:
                words.extend(step['world_words'])
        return words

    def to_rule_sequence(self) -> list[str]:
        """思维链→规则序列"""
        rules = []
        for step in self.steps:
            for r in step['rule_hits']:
                if r and r not in rules:
                    rules.append(r)
        return rules



class ThinkEngine:
    """多层过滤调整"""

    MAX_RAW_STEPS = 12
    MAX_FILTERED_STEPS = 8

    def __init__(self):
        self.chain = ThinkChain()
        self.tongzi = None

    def set_tongzi(self, tongzi):
        self.tongzi = tongzi

    def think(self, text, plate, tianyuan, pool, rules,
              xiao_tianyuan, dingxin, jiugua):
        if not tianyuan.anchor_slots:
            return ThinkChain()
        raw_path = self._walk_raw(plate, tianyuan, jiugua)
        if not raw_path:
            return ThinkChain()
        val_filt = self._filter_values(raw_path, plate, dingxin, rules)
        guided = self._apply_guide(val_filt, plate, xiao_tianyuan)
        rule_ok = self._verify_rules(guided, plate, pool, rules)
        if self.tongzi:
            exp_tuned = self._apply_experience(rule_ok, plate, tianyuan.gua, text)
        else:
            exp_tuned = rule_ok
        final_chain = self._match_world_layer(exp_tuned, plate, pool, rules, text)
        self._inject_input_words(final_chain, text, plate)
        self._filter_by_input(final_chain, text)
        if self.tongzi and final_chain.steps:
            words = final_chain.to_word_sequence()
            rule_names = final_chain.to_rule_sequence()
            gua_indices = [s["idx"] for s in final_chain.steps]
            gate = final_chain.steps[-1]["gate"] if final_chain.steps else "ACCEPT"
            self.tongzi.deposit(gua_chain=gua_indices, words=words, rules=rule_names,
                gate=gate, tianyuan_gua=tianyuan.gua, tianyuan_text=text,
                success=True, jiugua_used=(final_chain.jiugua_triggers > 0))
        return final_chain

    def _walk_raw(self, plate, tianyuan, jiugua):
        path = [tianyuan.center]
        current = tianyuan.center
        visited = {current}
        rels = ["sheng","ke","opposite","inverse","nearby","sheng","ke","opposite","nearby","inverse","sheng","ke"]
        for i in range(self.MAX_RAW_STEPS):
            neighbors = plate.neighbor_slots(current, rels[i % len(rels)])
            candidates = [n for n in neighbors if n not in visited]
            if not candidates:
                if jiugua.should_trigger(path, plate):
                    current = jiugua.inject(current, plate, tianyuan.gua)
                else:
                    current = (current + 1) % 64
            else:
                import random
                scored = [(n, plate.slots[n].mark_strength() * 3 + plate.slots[n].energy) for n in candidates]
                scored.sort(key=lambda x: x[1], reverse=True)
                current = random.choice(scored[:3])[0] if random.random() < 0.2 else scored[0][0]
            path.append(current)
            visited.add(current)
        return path

    def _filter_values(self, path, plate, dingxin, rules):
        filtered = [path[0]]
        for i in range(1, len(path)):
            gate = dingxin.gate(filtered + [path[i]], plate)
            if gate != "REJECT":
                filtered.append(path[i])
            else:
                slot = plate.slots[path[i]]
                good = AIXiaoTianYuan.GOOD_DIRECTION.get(BAGUA[slot.upper], 0)
                filtered.append((path[i] + good) % 64)
        return filtered

    def _apply_guide(self, path, plate, xiao_tianyuan):
        guided = [path[0]]
        for i in range(1, len(path)):
            slot = plate.slots[path[i]]
            good = AIXiaoTianYuan.GOOD_DIRECTION.get(BAGUA[slot.upper], 0)
            guided.append((path[i] + (good // 2)) % 64 if good > 0 else path[i])
        return guided

    def _verify_rules(self, path, plate, pool, rules):
        """L3 逻辑验证：卦位ref_gua与规则名hash的Hamming距离"""
        from .guayuan import gua_hash
        verified = [path[0]]
        for i in range(1, len(path)):
            slot = plate.slots[path[i]]
            matched = False
            for rname in rules.branches:
                d = hamming(slot.ref_gua, gua_hash(rname))
                if d <= 12:
                    matched = True
                    break
            if matched:
                verified.append(path[i])
            else:
                neighbors = plate.neighbor_slots(path[i], "nearby")[:3]
                found = False
                for nb in neighbors:
                    nb_slot = plate.slots[nb]
                    for rname in rules.branches:
                        if hamming(nb_slot.ref_gua, gua_hash(rname)) <= 12:
                            verified.append(nb)
                            found = True
                            break
                    if found:
                        break
                if not found:
                    verified.append(path[i])
        return verified

    def _apply_experience(self, path, plate, tianyuan_gua, text):
        if not self.tongzi or not path:
            return path
        adj = self.tongzi.participate(raw_chain=path, tianyuan_gua=tianyuan_gua,
            current_words=[], current_rules=[])
        suggest = adj.get("suggest_chain", [])
        if suggest and adj.get("confidence", 0) > 0.3 and len(suggest) >= len(path) // 2:
            cut = len(path) // 2
            return path[:cut] + suggest[:self.MAX_FILTERED_STEPS - cut]
        return path

    def _match_world_layer(self, path, plate, pool, rules, text=""):
        chain = ThinkChain()
        active_path = path[:self.MAX_FILTERED_STEPS]
        seen = set()
        for i, idx in enumerate(active_path):
            slot = plate.slots[idx]
            words = self._find_best_words(slot, pool, seen)
            seen.update(words)
            rule_hits = rules.bite(pool, tick=0, input_text=text)[:2]
            rel = STEP_RELATIONS[i % len(STEP_RELATIONS)]
            chain.add(idx, plate, words, rule_hits, "ACCEPT", rel)
        return chain

    def _find_best_words(self, slot, pool, exclude):
        """L5 语义匹配：锚点优先(全星) + 活跃星Hamming回退"""
        from .guayuan import hamming
        from .semantic_anchors import anchored_score
        words = []

        # ① 扫描全175星 → 锚定命中（突破active限制）
        for name in pool.stars:
            if name in exclude:
                continue
            star = pool.get_star(name)
            if not star:
                continue
            ascore = anchored_score(name, slot.idx)
            if ascore > 0:
                # 锚定命中 → 能量加权
                weighted = ascore * (0.5 + star.energy)
                words.append((name, -weighted * 10, star.energy))

        # ② 活跃星 → Hamming回退（锚点未命中时）
        active = pool.get_active()
        for name in active:
            if name in exclude:
                continue
            # 跳过已锚定的
            if any(w[0] == name for w in words):
                continue
            star = pool.get_star(name)
            if not star:
                continue
            d = hamming(star.gua, slot.ref_gua)
            if d < 12:
                words.append((name, d * 0.5, star.energy))

        words.sort(key=lambda x: x[1] - x[2] * 3)
        return [w[0] for w in words[:4]]

    def _inject_input_words(self, chain, text, plate):
        """注入输入字：用锚点卦族（宽匹配确保覆盖），过滤用64卦（精匹配）"""
        from .semantic_anchors import get_anchors
        for ch in text:
            ch_anchors = get_anchors(ch)
            if not ch_anchors:
                continue
            ch_fams = {a // 8 for a in ch_anchors}
            for step in chain.steps:
                if (step['idx'] // 8) in ch_fams and ch not in step['world_words']:
                    step['world_words'].insert(0, ch)

    def _filter_by_input(self, chain, text):
        """L6 过滤：保留输入字+高锚定分字（不再只保留输入字）"""
        from .semantic_anchors import anchored_score
        input_chars = set(text)
        for step in chain.steps:
            # 保留：在输入中的字 或 锚定分≥1.5的强关联字
            step['world_words'] = [
                w for w in step['world_words']
                if w in input_chars or anchored_score(w, step['idx']) >= 1.5
            ]



class BaguaMaster:
    def __init__(self):
        self.plate = GrandBaguaPlate()
        self.tianyuan = TianYuan()
        self.portrait = UserPortrait()
        self.xiao_tianyuan = AIXiaoTianYuan()
        self.dingxin = DingXinAnchor()
        self.jiugua = DiJiuGua()
        self.think_engine = ThinkEngine()

    def set_tongzi(self, tongzi):
        self.think_engine.set_tongzi(tongzi)

    def process(self, text, pool, rules):
        self.plate.tick_clock()
        ty_info = self.tianyuan.compute(text, self.plate)
        self.portrait.update(text, self.tianyuan, self.plate, pool)
        chain = self.think_engine.think(
            text, self.plate, self.tianyuan, pool,
            rules, self.xiao_tianyuan, self.dingxin, self.jiugua)
        guide = self.xiao_tianyuan.guide(ty_info["center"], self.plate)
        return {
            "clock": self.plate.snapshot(),
            "tianyuan": ty_info,
            "guide": guide,
            "chain_steps": chain.steps,
            "word_sequence": chain.to_word_sequence(),
            "rule_sequence": chain.to_rule_sequence(),
            "jiugua_triggers": chain.jiugua_triggers,
            "user_mood": self.portrait.current_mood,
            "kline": self.portrait.get_kline(self.plate),
        }
