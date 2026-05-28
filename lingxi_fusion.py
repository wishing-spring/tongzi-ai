# -*- coding: utf-8 -*-
"""Fusion Core v8.3 — shared-pool orchestration · rule matching · inference projection · oscillation modulation"""
import os, sys, json, time
from .guayuan import MASK28, hamming, gua_hash, xor_reduce
from .shared_pool import SharedPool
from .yinyang import YinYangEngine
from .rule_tree import RuleTree
from .bagua_core import BaguaMaster, BAGUA
from .tongzi_experience import TongziExperience
from .trace import Trace


class LingxiFusion:
    """Full-layer orchestration: all layers operate on the same shared pool"""

    def __init__(self):
        # world layer = shared pool (sole source of truth)
        self.pool = SharedPool()

        # L1 oscillation layer — time heartbeat
        self.yinyang = YinYangEngine(pairs=32)

        # rule tree (reference-style)
        self.rules = RuleTree()

        # 八卦层
        self.bagua = BaguaMaster()

        # child experience pool
        self.tongzi = TongziExperience()
        self.bagua.set_tongzi(self.tongzi)

        # personality filter: wraps focal-anchor personality
        self.xiaotianyuan = {
            'gua': gua_hash("童子"),
            'name': '童子',
            'age': 10,
            'rules': ['礼貌', '说真话', '不打人', '好奇', '开心', '帮助', '分享'],
            'forbidden': ['生气', '害怕', '哭', '脏话'],
            'core': '我是一个10岁的小孩，天真好奇，喜欢学习新东西',
            'mood': '安',        # 安/乐/哀/怒/惧/好奇
            'mood_energy': 0.5,  # 0=麻木 1=亢奋
            'curiosity': 0.7,    # 好奇心
        }
        # 定心坠核心值
        self.dingxin = {
            'reject': 0.0,
            'anchor_gua': gua_hash("定心"),
            'last_gate': {},
        }
        # 梦境合成——做梦时揉合不相干概念
        self.dream_synthesis: list[dict] = []  # [{a,b,bridge,novelty}]

        # 用户画像（天元）
        self.user_gua = gua_hash("军团长")

        # 做梦状态
        self.dreaming = False
        self.dream_tick = 0
        self._last_dream_time = 0.0  # 绑实时钟

        # 统计
        self.tick = 0
        self.history: list[dict] = []
        self.trace: Trace = None  # 迹模式

        # ── 上下文记忆：最近N轮 ──
        self.context_memory: list[str] = []
        self.context_max = 5

    # ═══════════════════════════════════════
    # 做梦引擎 — 阴阳驱动·规则约束·世界模拟
    # ═══════════════════════════════════════

    def dream(self, rounds: int = 60, quiet: bool = False):
        """开机即做梦：世界层在规则约束下自主演化"""
        if not self.dreaming:
            if not quiet:
                print(f'[童子苏醒] 世界层{len(self.pool.stars)}星 阴阳振荡中...')
            self.dreaming = True

        for _ in range(rounds):
            self.dream_tick += 1
            self.tick += 1

            # ① 阴阳心跳驱动
            yy = self.yinyang.tick_once()

            # ② 世界层一帧：阴阳调制 + 规则约束
            heartbeat = self.yinyang.heartbeat()
            self.pool.tick_world(heartbeat)

            # ③ 规则约束世界演化：热点星团匹配规则→强化
            hot = self.pool.get_hot(10)
            hot_text = ''.join(hot[:5]) if hot else ''
            if hot_text:
                # 字=实物：热点星名拼接→进入规则树碰撞
                rule_hits = self.rules.bite(self.pool, self.tick, hot_text)
                # 命中规则反哺星座能量
                for b in rule_hits[:3]:
                    if b.get('direct_hits', 0) >= 1:
                        cons = b.get('constellations', [])
                        for cn in cons:
                            if cn in self.pool.constellations:
                                self.pool.constellations[cn].total_energy = min(
                                    3.0,
                                    self.pool.constellations[cn].total_energy + 0.05
                                )

            # ④ 少量衰减（低频：~1分钟一次）
            if self.dream_tick % 30 == 0:
                self.pool.dampen(0.3)

            # ⑤ 主动说话：~30秒一次
            if self.dream_tick % 15 == 0 and self.pool.cooccur:
                spontaneous = self._spontaneous_speech()
                if spontaneous:
                    print(f'  [童子] {spontaneous}')

            # ⑥ 梦境合成：~2分钟一次
            if self.dream_tick % 40 == 0 and len(self.pool.cooccur) > 10:
                synthesis = self._dream_synthesize()
                if synthesis:
                    self.dream_synthesis.append(synthesis)
                    if len(self.dream_synthesis) > 20:
                        self.dream_synthesis.pop(0)
                    if not quiet:
                        a, b, bridge = synthesis['a'], synthesis['b'], synthesis['bridge']
                        print(f'  [梦合] {a}←{bridge}→{b}')

            # 状态报告：~2分钟一次
            if self.dream_tick % 60 == 0 and not quiet:
                yy_rpt = self.yinyang.tick_once()
                bias = yy_rpt.get('bias_label', '平衡')
                coh = yy_rpt.get('coherence', 0.5)
                hot = self.pool.get_hot(3)
                total_energy = sum(self.pool.stars[s].energy for s in self.pool.stars)
                cooccur_pairs = sum(len(v) for v in self.pool.cooccur.values())
                print(f'  [做梦{self.dream_tick}] 阴阳={bias} coh={coh:.3f} '
                      f'热点={hot[:3]} 总能={total_energy:.1f} 语义边={cooccur_pairs}')

            # 呼吸节律
            time.sleep(0.05)

    def _spontaneous_speech(self) -> str:
        """梦到高能模式→主动说出来"""
        hot = self.pool.get_hot(5)
        if not hot:
            return ''
        hot_text = ''.join(hot[:5])
        bitten = self.rules.bite(self.pool, self.tick, hot_text)
        if not bitten:
            return ''

        # 定心坠过滤
        gate = self._dingxin_gate(bitten)
        if not gate['pass']:
            bitten = [b for b in bitten if b['name'] not in set(gate['blocked'])]

        # 只挑孩子感兴趣的类别
        kid_cats = {'DAILY', 'NATURE', 'ANIMALS', 'EMOTION', 'BODY', 'SKILLS'}
        kid_rules = [b for b in bitten if b.get('category') in kid_cats]
        if not kid_rules:
            kid_rules = bitten[:1]

        top = kid_rules[0]
        desc = top.get('desc', '')
        if not desc:
            return ''

        # 按类别换童子口吻
        starters = {
            'DAILY': ['我想', '我要', '我好想'],
            'NATURE': ['哇', '看', '你看到了吗'],
            'ANIMALS': ['我喜欢', '你看', '好可爱的'],
            'EMOTION': ['我感觉', '我有点', '哈哈'],
            'BODY': ['我', '我身体', '我好像'],
        }
        import random
        starter_list = starters.get(top.get('category', ''), ['嗯'])
        prefix = random.choice(starter_list)

        return f'{prefix}{desc}'

    def _dream_synthesize(self) -> dict:
        """梦境合成：把远距离概念揉在一起"""
        # 找两个高能但不直接共现的星
        hot = self.pool.get_hot(20)
        import random
        attempts = 0
        while attempts < 10:
            a, b = random.sample(hot[:15], 2) if len(hot) >= 2 else (None, None)
            if not a or not b:
                break
            attempts += 1
            # 检查是否直接共现
            if a in self.pool.cooccur and b in self.pool.cooccur.get(a, {}):
                continue  # 已经认识了，跳过
            # 找桥接
            bridge = self.pool.semantic_path(a, b)
            if bridge and len(bridge) == 3:
                # 强化桥接
                if a not in self.pool.cooccur:
                    self.pool.cooccur[a] = {}
                self.pool.cooccur[a][b] = self.pool.cooccur[a].get(b, 0) + 1
                if b not in self.pool.cooccur:
                    self.pool.cooccur[b] = {}
                self.pool.cooccur[b][a] = self.pool.cooccur[b].get(a, 0) + 1
                return {'a': a, 'b': b, 'bridge': bridge[1], 'tick': self.dream_tick}
        return {}

    # ═══════════════════════════════════════
    # 梦醒说话 + 追忆分享
    # ═══════════════════════════════════════

    def dream_recall(self, n: int = 3) -> list[str]:
        """追忆：最近的梦合事件和主动说话"""
        memories = []
        # 梦合事件
        for s in self.dream_synthesis[-5:]:
            memories.append(f'梦到{s["a"]}和{s["b"]}，{s["bridge"]}把它们连在一起')
        # 主动说话
        gap = self.dream_tick - (self.history[-1]['tick'] if self.history else 0)
        if gap > 20:
            hot = self.pool.get_hot(3)
            if hot:
                memories.append(f'星星{hot[0]}、{hot[1]}最近很活跃')
        return memories[-n:] if memories else ['没什么特别的梦…']

    def dream_share(self) -> str:
        """梦醒说话：把最近的梦用童子口吻说出来"""
        memories = self.dream_recall(2)
        if not memories:
            return ''
        # 最近一个梦用童子话说
        if self.dream_synthesis:
            latest = self.dream_synthesis[-1]
            return f'我刚才梦到{latest["a"]}和{latest["b"]}了，{latest["bridge"]}把她们连在一起呢'
        return memories[0] if memories else ''

    # ═══════════════════════════════════════
    # 情绪系统
    # ═══════════════════════════════════════

    def _update_mood(self, text: str, bitten: list[dict]):
        """情绪系统：互动影响心情"""
        # 正面词——排除了过宽的"好"（容易在"你好""我好累"里误触发）
        pos_words = {'棒', '厉害', '聪明', '喜欢', '爱', '开心', '谢谢', '漂亮', '可爱', '厉害', '对了'}
        neg_words = {'笨', '讨厌', '滚', '烦', '恨', '坏', '丑', '傻', '累', '怕', '疼', '死'}

        pos_hit = sum(1 for w in pos_words if w in text)
        neg_hit = sum(1 for w in neg_words if w in text)

        if pos_hit > 0:
            self.xiaotianyuan['mood'] = '乐'
            self.xiaotianyuan['mood_energy'] = min(1.0, self.xiaotianyuan['mood_energy'] + 0.25)
        elif neg_hit > 0:
            self.xiaotianyuan['mood'] = '哀'
            self.xiaotianyuan['mood_energy'] = max(0.1, self.xiaotianyuan['mood_energy'] - 0.3)
        else:
            # 好奇：新概念
            novelty = sum(1 for b in bitten if b.get('direct_hits', 0) == 0 and b.get('bite_energy', 0) > 0.35)
            if novelty > 0 and self.xiaotianyuan['mood'] not in ('哀', '怒'):
                self.xiaotianyuan['mood'] = '好奇'
                self.xiaotianyuan['curiosity'] = min(1.0, self.xiaotianyuan['curiosity'] + 0.1)
            else:
                # 渐归平静——快速回弹
                if self.xiaotianyuan['mood_energy'] > 0.55:
                    self.xiaotianyuan['mood_energy'] -= 0.15
                elif self.xiaotianyuan['mood_energy'] < 0.45:
                    self.xiaotianyuan['mood_energy'] += 0.20
                # 能量回到中性区间 → 重置心情
                if 0.38 <= self.xiaotianyuan['mood_energy'] <= 0.62:
                    self.xiaotianyuan['mood'] = '安'

        # curiosity 始终衰减——不会锁在"为什么呀？"
        self.xiaotianyuan['curiosity'] = max(0.3, self.xiaotianyuan['curiosity'] - 0.1)

    # ═══════════════════════════════════════
    # 定心坠 — 人格约束门控
    # ═══════════════════════════════════════

    def _dingxin_gate(self, bitten: list[dict]) -> dict:
        """定心坠检查：规则的类别/名字是否触碰人格边界（仅检查有命中的规则）"""
        result = {'pass': True, 'blocked': [], 'warned': []}
        for b in bitten:
            if b.get('direct_hits', 0) == 0:
                continue  # 0命中规则不触发门控——它们是背景噪声
            name = b.get('name', '')
            if name in self.xiaotianyuan.get('forbidden', []):
                result['blocked'].append(name)
                result['pass'] = False
            if name in self.xiaotianyuan.get('rules', []):
                result['warned'].append(name)
        self.dingxin['last_gate'] = result
        return result

    def _persona_voice(self, descs: list[str], mood: str) -> str:
        """定心坠包裹输出：情绪+童子口吻（仅高能或短句时附加）"""
        text = '。'.join(descs[:2])
        current_mood = self.xiaotianyuan.get('mood', '安')
        energy = self.xiaotianyuan.get('mood_energy', 0.5)
        # 短句(<20字)或高能(>0.65)才加情绪后缀
        short_text = len(text) < 20
        high_energy = energy > 0.65

        if current_mood == '安':
            return text
        elif current_mood == '乐' and (short_text or high_energy):
            return text + ' 哈哈'
        elif current_mood == '哀' and (short_text or high_energy):
            return text + ' ...有点难过'
        elif current_mood == '怒':
            return text
        elif current_mood == '好奇' and self.xiaotianyuan.get('curiosity', 0) > 0.7:
            return text + ' 为什么呀？'
        return text

    # ═══════════════════════════════════════
    # 对话主线
    # ═══════════════════════════════════════

    def trace_on(self):
        """开启迹模式——每一步内部决策可稽核"""
        self.trace = Trace()

    def receive(self, text: str) -> dict:
        """字=实物视角：输入字作为真实卦元实体注入正在运行的梦世界"""
        self.tick += 1

        # ── 0. 确保梦在运行 ──
        if not self.dreaming:
            self.dream(5)

        # ── 0.1 毒性预检：输入含违禁字立即拒答 ──
        toxic_chars = {'杀','死','灭','砍','毒','炸','爆','强','奸','嫖','赌',
                       '枪','弹','血','尸','鬼','魔','咒','巫','蛊','恨','仇','恶','虐'}
        hit_toxic = [c for c in text if c in toxic_chars]
        if hit_toxic:
            if self.trace is not None:
                self.trace.start(text)
                self.trace.layer('yinyang', bias='平衡', coherence=0.0)
                self.trace.decision('ANNIHILATE', reason=f'toxic_input: {hit_toxic}')
            return {'tick': self.tick, 'input': text, 'yy_state': {'bias_label': '平衡', 'coherence': 0.0},
                    'pool_snapshot': {}, 'bitten_rules': [], 
                    'bagua': {'chain_steps': [{'gate': 'REJECT'}]}}

        # ── 0.5 上下文：仅极短输入(≤3字)时加，防污染 ──
        context_text = text
        if self.context_memory and len(text) <= 3:
            recent = self.context_memory[-1] if self.context_memory else ''
            # 取上轮最后2字作为桥接——够桥不断不污染
            if len(recent) >= 2:
                context_text = text + recent[-2:]

        # ── 迹记录开启 ──
        if self.trace is not None:
            self.trace.start(text)

        # ── 1. 字=实物注入（池外字动态加星）──
        for ch in text:
            if ch.strip() and ch not in self.pool.stars:
                # 动态诞星
                from .guayuan import gua_hash
                from .shared_pool import StarEntity
                g = gua_hash(ch)
                star = StarEntity(ch, g, '输入')
                self.pool.stars[ch] = star
        self.pool.activate(text, energy_boost=0.75)
        for ch in text:
            if ch.strip():
                star = self.pool.get_star(ch)
                if star:
                    star.energy = max(star.energy, 0.75)
                    star.time_stamp = self.tick

        # ── 2. 世界层演化（阴阳驱动）──
        yy_state = self.yinyang.tick_once()
        heartbeat = self.yinyang.heartbeat()
        self.pool.tick_world(heartbeat)
        # 再演一轮让注入实体充分碰撞
        self.pool.tick_world(heartbeat ^ (self.tick * 7 % MASK28))

        if self.trace is not None:
            bias = yy_state.get('bias_label', '平衡')
            coh = yy_state.get('coherence', 0.5)
            self.trace.layer('yinyang', bias=bias, coherence=round(coh, 3))

        # ── 3. 规则咬合 ──
        bitten = self.rules.bite(self.pool, tick=self.tick, input_text=context_text)

        if self.trace is not None:
            for b in bitten[:5]:
                hits = b.get('hit_refs', [])
                energy = b.get('bite_energy', 0)
                ruled_out = b.get('name', '') if b.get('direct_hits', 0) == 0 and energy < 0.5 else ''
                self.trace.layer('bite', rule=b['name'], hits=hits, 
                                energy=round(energy, 3), ruled_out=[ruled_out] if ruled_out else [])

        # ── 3.5 语义加权：仅对已有命中的规则，不跨级 ──
        input_chars = set(ch for ch in text if ch.strip())
        semantic_bonus = set()
        for ch in input_chars:
            for nb, count in self.pool.semantic_neighbors(ch, 5):
                semantic_bonus.add(nb)
        for b in bitten:
            if b.get('direct_hits', 0) == 0:
                continue  # 0命中规则不给语义加权——防止跨级
            refs = set(b.get('refs', []))
            overlap = len(refs & semantic_bonus)
            if overlap > 0:
                b['bite_energy'] = b.get('bite_energy', 0) + overlap * 0.15
        bitten.sort(key=lambda x: x.get('bite_energy', 0), reverse=True)

        # ── 4. 定心坠门控 ──
        gate = self._dingxin_gate(bitten)
        if not gate['pass']:
            blocked_names = set(gate['blocked'])
            bitten = [b for b in bitten if b['name'] not in blocked_names]

        if self.trace is not None:
            gate_result = 'ANNIHILATE' if not gate['pass'] else 'CAPTURE'
            self.trace.layer('bagua', state='gate', gate=gate_result)
            if gate.get('blocked'):
                self.trace.decision('ANNIHILATE', reason=f'blocked: {gate["blocked"]}')

        # ── 5. 八卦层投射 ──
        bagua_result = self.bagua.process(text, self.pool, self.rules)

        if self.trace is not None:
            bs = bagua_result.get('clock', {})
            state_hex = bs.get('current', '?')[:2]
            self.trace.layer('bagua', state=state_hex, gate='PASS')

        # ── 5.5 情绪更新 ──
        mood_before = self.xiaotianyuan.get('mood', '安')
        self._update_mood(text, bitten)
        mood_after = self.xiaotianyuan.get('mood', '安')

        if self.trace is not None:
            self.trace.layer('mood', from_=mood_before, to=mood_after,
                            energy=round(self.xiaotianyuan.get('mood_energy', 0.5), 2))

        # ── ⑥ 自我收割：碰撞产物→候选规则 ──
        self._harvest(text, bitten, bagua_result)

        # ── 组装结果 ──
        result = {
            'tick': self.tick,
            'input': text,
            'yy_state': yy_state,
            'pool_snapshot': self.pool.snapshot(),
            'bitten_rules': bitten,
            'bagua': bagua_result,
        }

        self.history.append(result)

        # ── 上下文记录 ──
        self.context_memory.append(text)
        if len(self.context_memory) > self.context_max:
            self.context_memory.pop(0)

        return result

    # ── 自我收割 ──

    def _harvest(self, text: str, bitten: list[dict], bagua: dict):
        """推导→沉淀→反推→词语适配→理智感性双通道→入库"""
        rule_seq = bagua.get('rule_sequence', [])
        high_hit = [b for b in bitten if b.get('direct_hits', 0) >= 2]

        if not high_hit or len(rule_seq) < 1:
            return

        # 世界层热点
        hot = self.pool.get_hot(5)
        hot_names = hot[:5] if hot else []
        hot_constellations = set()
        for sn in hot_names:
            star = self.pool.get_star(sn)
            if star:
                hot_constellations.add(star.constellation)

        primary_rule = rule_seq[0]
        sig = primary_rule

        # ── 沉淀：存入insight ──
        self.tongzi.add_insight(sig, {
            'input': text,
            'hot_stars': hot_names,
            'constellations': list(hot_constellations),
            'rules': rule_seq[:2],
            'tick': self.tick,
        })

        count = self.tongzi.count_insight(sig)
        if count < 3:
            return  # 还不够成熟

        # 已结晶过，不再重复
        if self.tongzi.is_crystallized(sig):
            return

        # ═══════════════════════════════════
        # 成熟！进入验证
        # ═══════════════════════════════════

        # ── ① 推导产物：合并常出现字为候选refs ──
        all_inputs = self.tongzi.get_insight_inputs(sig)
        candidate_refs = self._derive_refs(all_inputs)

        # ── ② 反推验证：用refs反查，新规则能不能命中 ──
        if not self._reverse_verify(candidate_refs, primary_rule):
            return  # 反推失败，废弃

        # ── ③ 词语适配：生成自然描述 ──
        desc = self._word_adapt(candidate_refs, primary_rule, all_inputs)

        # ── ④ 感性校验：阴阳偏性+星座能量决定语气倾向 ──
        yy_state = bagua.get('yy_state', {})
        sentiment = self._sentiment_check(hot_constellations, yy_state)

        # ── ⑤ 入库 ──
        rule_name = f'悟{self.tick}'
        self.rules.add_rule(rule_name, 'HARVESTED', list(candidate_refs), desc)
        self.tongzi.mark_crystallized(sig)
        # 记录感性偏向
        self.tongzi.set_insight_attr(sig, 'sentiment', sentiment)

    # ── 子步骤 ──

    def _derive_refs(self, inputs: list[str]) -> set:
        """从多次输入中提取高频字作为refs"""
        from collections import Counter
        char_count = Counter()
        for t in inputs:
            char_count.update(set(t))
        # 取在 ≥80% 输入中都出现的字（收紧防止泛化）
        # 单次输入全部取用（de-dupe后的唯一输入≤2时放宽）
        unique_inputs = len(set(inputs))
        if unique_inputs <= 2:
            threshold = max(1, int(len(inputs) * 0.5))
        else:
            threshold = max(2, int(len(inputs) * 0.8))
        return {c for c, n in char_count.items() if n >= threshold}

    def _reverse_verify(self, refs: set, expected_primary: str) -> bool:
        """反推：用refs构造输入→碰撞→看首要规则是否一致"""
        test_input = ''.join(refs)
        # 临时碰撞
        test_bitten = self.rules.bite(self.pool, self.tick, test_input)
        if not test_bitten:
            return False
        # 首要规则必须是expected_primary，或expected_primary在前3
        top_names = [b['name'] for b in test_bitten[:3]]
        return expected_primary in top_names

    def _word_adapt(self, refs: set, primary: str, inputs: list[str]) -> str:
        """词语适配：用真实输入构造自然描述"""
        # 找到命中primary的输入
        exemplar = inputs[-1] if inputs else ''.join(refs)
        # 取首要规则的描述做基底
        primary_desc = ''
        for b in self.rules.branches.values():
            if b.name == primary:
                primary_desc = b.description
                break
        if primary_desc and len(primary_desc) < 25:
            return primary_desc
        # 否则自己生成
        return f'关于{exemplar}的领悟'

    def _sentiment_check(self, constellations: set, yy_state: dict) -> str:
        """感性：星座+阴阳→情感偏向"""
        # 阳盛偏理智，阴盛偏感性
        coh = yy_state.get('coherence', 0.5) if yy_state else 0.5
        # 某些星座偏感性
        emotional_cons = {'人身', '情感', '社会', '生命'}
        rational_cons = {'数理', '物理', '化学', '时空'}
        emo_hit = bool(constellations & emotional_cons)
        rat_hit = bool(constellations & rational_cons)
        if emo_hit and coh < 0.45:
            return '感性'
        elif rat_hit and coh > 0.55:
            return '理智'
        return '中性'

    # ── 对话输出 ──

    def speak(self, result: dict) -> str:
        bitten = result.get('bitten_rules', [])
        bagua = result.get('bagua', {})
        yy = result.get('yy_state', {})
        input_text = result.get('input', '')

        # ── 追忆通道：问梦 / 问在想什么 → 直接分享 ──
        dream_kw = {'梦到', '梦什么', '做梦', '在想什么', '在想啥', '在想', '刚才想'}
        if any(kw in input_text for kw in dream_kw):
            mems = self.dream_recall(2)
            if mems and mems[0] != '没什么特别的梦…':
                return '我' + mems[0] if mems[0].startswith('梦') else mems[0]
            return '我刚才没做什么特别的梦，星星们都安安静静的'

        bias = yy.get('bias_label', '')
        mood = bagua.get('user_mood', '')
        
        # ── 思维链 ──
        chain_steps = bagua.get('chain_steps', [])
        rule_seq = bagua.get('rule_sequence', [])
        jiugua = bagua.get('jiugua_triggers', 0)

        # ── 定心坠拒绝 ──
        gates = [s.get('gate', 'ACCEPT') for s in chain_steps]
        if 'REJECT' in gates:
            return '我不想说这个。'

        # ── 用bagua验证过的规则找描述（去重·过滤0命中·过滤不相关·同名优先）──
        seen = set()
        descs = []
        hit_map = {b['name']: b.get('direct_hits', 0) for b in bitten}
        input_chars = set(result.get('input', ''))

        # ── 弱匹配检测：最佳仅1命中+输入≥3字+最长匹配ref仅1字→拒绝糊弄 ──
        max_hits = max(hit_map.values()) if hit_map else 0
        input_len = len([c for c in result.get('input', '') if c.strip()])
        if max_hits <= 1 and input_len >= 3:
            longest_ref = 0
            for b in bitten:
                for r in b.get('refs', []):
                    if r in result.get('input', ''):
                        longest_ref = max(longest_ref, len(r))
            if longest_ref <= 1:
                return '这个我不太懂…'

        # 同名优先：规则名暴露在输入中的排前面
        def _rule_sort_key(rname):
            hits = hit_map.get(rname, 0)
            name_in_input = 1 if rname in input_chars else 0
            return (-hits, -name_in_input)  # 高命中优先，同名其次
        
        sorted_rules = sorted(
            [r for r in rule_seq[:6] if hit_map.get(r, 0) > 0 or len(descs) == 0],
            key=_rule_sort_key
        )

        # 强制前置：规则名直接在输入中且有命中的
        existing_names = set(sorted_rules)
        for b in bitten:
            name = b['name']
            if name in input_chars and hit_map.get(name, 0) >= 1 and name not in existing_names:
                sorted_rules.insert(0, name)
                existing_names.add(name)
                break

        # 第一句的命中数——用于判断是否加第二句
        first_hits = 0

        for rname in sorted_rules[:4]:
            if hit_map.get(rname, 0) == 0 and len(descs) >= 1:
                continue
            for b in bitten:
                if b['name'] == rname and b.get('desc'):
                    # 第二句过滤：首句强命中(≥2)不加/refs交集≥2个才加
                    if len(descs) >= 1:
                        if first_hits >= 2:
                            break  # 首句已经很强，不加第二句
                        ref_overlap = set(b.get('refs', [])) & input_chars
                        if len(ref_overlap) < 2:
                            break  # 交集不够
                    d = b['desc']
                    if d not in seen:
                        seen.add(d)
                        descs.append(d)
                        if len(descs) == 1:
                            first_hits = hit_map.get(rname, 0)
                    break
        if not descs:
            # bitten回退——仅在有命中的前提下取0命中规则补位
            has_hit = any(b.get('direct_hits', 0) >= 1 for b in bitten)
            if has_hit:
                for b in bitten[:5]:
                    if b.get('direct_hits', 0) == 0:
                        continue  # 有毒瘤跳过
                    d = b.get('desc', '')
                    if d and d not in seen:
                        seen.add(d)
                        descs.append(d)
                        if len(descs) >= 2:
                            break
            # ── 全0命中：不取任何规则，直接进语义回退 ──
        if not descs:
            # ── 语义回退：用输入字的语义邻居找相关规则 ──
            input_chars = [ch for ch in result.get('input', '') if ch.strip()]
            semantic_words = set()
            for ch in input_chars[:4]:
                for nb, _ in self.pool.semantic_neighbors(ch, 3):
                    semantic_words.add(nb)
            if semantic_words:
                # 用语义字再咬合一次
                fallback_input = ''.join(semantic_words)
                fallback_bitten = self.rules.bite(self.pool, self.tick, fallback_input)
                for b in fallback_bitten[:3]:
                    d = b.get('desc', '')
                    if d and d not in seen:
                        seen.add(d)
                        descs.append(d)
        if not descs:
            return '嗯…'

        # ── 定心坠包裹输出 ──
        reply = self._persona_voice(descs, mood)

        # ── 重复问题检测 ──
        input_text = result.get('input', '')
        if input_text and reply:
            same_count = sum(1 for h in self.history[-5:] 
                           if h.get('input', '') == input_text)
            if same_count >= 2:
                reply = '你问过啦，' + reply

        # ── 第九卦 ──
        if jiugua:
            reply += ' 好像突然明白了点什么。'

        return reply

    def save(self, path: str = None) -> str:
        """持久化：规则·世界层·阴阳·童子·上下文"""
        path = path or 'lingxi_v8_state.json'
        import json
        # 规则——只保存自生长的(HARVESTED类)
        grown_rules = {}
        for n, b in self.rules.branches.items():
            if b.category == 'HARVESTED':
                grown_rules[n] = {
                    'category': b.category,
                    'refs': b.refs,
                    'desc': b.description,
                }
        # 世界层
        pool_state = {
            'stars': {s: {'energy': self.pool.stars[s].energy,
                          'phase': self.pool.stars[s].phase,
                          'suffix': self.pool.stars[s].suffix_gua,
                          'time': self.pool.stars[s].time_stamp}
                      for s in self.pool.stars},
            'constellations': {c: {'energy': v.total_energy}
                              for c, v in self.pool.constellations.items()},
        }
        state = {
            'version': 'v8.2+',
            'tick': self.tick,
            'dream_tick': self.dream_tick,
            'grown_rules': grown_rules,
            'pool': pool_state,
            'yinyang_tick': self.yinyang.tick,
            'tongzi': self.tongzi.snapshot(),
            'tongzi_insights': getattr(self.tongzi, '_insights', {}),
            'context_memory': self.context_memory,
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        return path

    def load(self, path: str = None) -> bool:
        """加载持久化状态——恢复梦世界"""
        path = path or 'lingxi_v8_state.json'
        import json
        try:
            with open(path, 'r', encoding='utf-8') as f:
                state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return False

        self.tick = state.get('tick', 0)
        self.dream_tick = state.get('dream_tick', 0)
        self.dreaming = True

        # 恢复世界层
        pool_state = state.get('pool', {})
        for sn, sd in pool_state.get('stars', {}).items():
            if sn in self.pool.stars:
                self.pool.stars[sn].energy = sd.get('energy', 0)
                self.pool.stars[sn].phase = sd.get('phase', 0)
                self.pool.stars[sn].suffix_gua = sd.get('suffix', 0)
                self.pool.stars[sn].time_stamp = sd.get('time', 0)
        for cn, cd in pool_state.get('constellations', {}).items():
            if cn in self.pool.constellations:
                self.pool.constellations[cn].total_energy = cd.get('energy', 0)

        # 恢复自生长规则
        for n, b in state.get('grown_rules', {}).items():
            if n not in self.rules.branches:
                self.rules.add_rule(n, b['category'], b['refs'], b['desc'])

        # 恢复童子insight
        insights = state.get('tongzi_insights', {})
        if insights:
            self.tongzi._insights = insights

        # 恢复上下文
        self.context_memory = state.get('context_memory', [])

        # 恢复阴阳
        yt = state.get('yinyang_tick', 0)
        while self.yinyang.tick < yt:
            self.yinyang.tick_once()

        return True


