# -*- coding: utf-8 -*-
"""BitVector Factory v8.3 — Radical-structure encoding: single CJK char = Unicode radical Gray code, multi-char = LFSR hash"""
import os, sys, time
MASK28 = 0x0FFFFFFF
WIDTH = 28

CJK_BEGIN = 0x4E00
CJK_END   = 0x9FFF
CJKA_BEGIN = 0x3400
CJKA_END   = 0x4DBF

def gua_hash(s: str) -> int:
    """Radical-structure encoding: single CJK char uses Unicode radical position + Gray code; multi-char/non-CJK uses LFSR hash"""
    if len(s) == 1:
        n = ord(s)
        if CJK_BEGIN <= n <= CJK_END:
            pos = n - CJK_BEGIN
            return (pos ^ (pos >> 1)) & MASK28
        if CJKA_BEGIN <= n <= CJKA_END:
            pos = n - CJKA_BEGIN + 0x5200
            return (pos ^ (pos >> 1)) & MASK28
    h = 0
    for ch in s:
        h = ((h << 5) ^ ord(ch)) & MASK28
    return h

def hamming(a: int, b: int) -> int:
    return ((a ^ b) & MASK28).bit_count()

def xor_reduce(vals: list) -> int:
    r = 0
    for v in vals:
        r ^= v
    return r & MASK28

def get_bits(g: int, hi: int, lo: int) -> int:
    return (g >> lo) & ((1 << (hi - lo)) - 1)

def set_bits(g: int, hi: int, lo: int, val: int) -> int:
    mask = ((1 << (hi - lo)) - 1) << lo
    return (g & ~mask) | ((val & ((1 << (hi - lo)) - 1)) << lo)

def random_gua(seed: int = 0) -> int:
    t = int(time.time() * 1000) if seed == 0 else seed
    h = t & MASK28
    for _ in range(4):
        h = ((h << 7) ^ (h >> 5) ^ (h << 13)) & MASK28
    return h


# ═══════════════ Source Library — 9 Categories ═══════════════

class SourceGuaLib:
    GEOMETRY = {}
    PHYSICS = {}
    CHEMISTRY = {}
    BIOLOGY = {}
    PSYCHOLOGY = {}
    MATH = {}
    LANGUAGE = {}
    TIME_SPACE = {}
    SOCIETY = {}

    def __init__(self):
        self._seed_all()

    def _seed_all(self):
        for k, v in {
            '点': 'dot', '线': 'line', '面': 'plane', '体': 'solid', '角': 'angle',
            '圆': 'circle', '方': 'square', '上': 'up', '下': 'down', '前': 'front',
            '后': 'back', '左': 'left', '右': 'right', '中': 'center',
            '直': 'straight', '曲': 'curve', '螺旋': 'spiral', '对称': 'symmetry'
        }.items(): self.GEOMETRY[k] = gua_hash(v)

        for k, v in {
            '力': 'force', '热': 'heat', '光': 'light', '声': 'sound', '电': 'electric',
            '磁': 'magnetic', '重力': 'gravity', '摩擦': 'friction', '能量': 'energy',
            '熵': 'entropy', '波': 'wave', '速度': 'speed', '惯性': 'inertia',
            '压强': 'pressure', '温度': 'temperature', '质量': 'mass'
        }.items(): self.PHYSICS[k] = gua_hash(v)

        for k, v in {
            '化合': 'combine', '分解': 'decompose', '氧化': 'oxidize', '还原': 'reduce',
            '酸': 'acid', '碱': 'base', '盐': 'salt', '反应': 'reaction',
            '溶液': 'solution', '沉淀': 'precipitate', '金属': 'metal'
        }.items(): self.CHEMISTRY[k] = gua_hash(v)

        for k, v in {
            '加': 'add', '减': 'sub', '乘': 'mul', '除': 'div', '等于': 'equal',
            '大于': 'gt', '小于': 'lt', '如果': 'if', '则': 'then', '否则': 'else',
            '且': 'and', '或': 'or', '非': 'not', '推导': 'derive', '因果': 'cause',
            '包含': 'contain', '属于': 'member'
        }.items(): self.MATH[k] = gua_hash(v)

        for k, v in {
            '快乐': 'happy', '悲伤': 'sad', '愤怒': 'angry', '恐惧': 'fear',
            '惊讶': 'surprise', '厌恶': 'disgust', '信任': 'trust', '平静': 'calm',
            '渴望': 'desire', '好奇': 'curious', '满足': 'satisfied', '焦虑': 'anxiety',
            '后悔': 'regret', '愧疚': 'guilt', '期待': 'expect'
        }.items(): self.PSYCHOLOGY[k] = gua_hash(v)

        for k, v in {
            '春': 'spring', '夏': 'summer', '秋': 'autumn', '冬': 'winter',
            '早晨': 'morning', '傍晚': 'dusk', '深夜': 'midnight',
            '过去': 'past', '现在': 'now', '未来': 'future',
            '东': 'east', '南': 'south', '西': 'west', '北': 'north',
            '瞬间': 'instant', '永恒': 'eternal'
        }.items(): self.TIME_SPACE[k] = gua_hash(v)

        for k, v in {
            '名词': 'noun', '动词': 'verb', '形容词': 'adj', '副词': 'adv',
            '主语': 'subject', '谓语': 'predicate', '宾语': 'object',
            '陈述': 'statement', '疑问': 'question', '感叹': 'exclamation'
        }.items(): self.LANGUAGE[k] = gua_hash(v)

        for k, v in {
            '善': 'good', '恶': 'evil', '公平': 'fair', '正义': 'justice',
            '自由': 'freedom', '责任': 'duty', '诚实': 'honest', '尊重': 'respect'
        }.items(): self.SOCIETY[k] = gua_hash(v)

        for k, v in {
            '生长': 'grow', '呼吸': 'breathe', '繁殖': 'reproduce', '死亡': 'die',
            '细胞': 'cell', '进化': 'evolve', '基因': 'gene'
        }.items(): self.BIOLOGY[k] = gua_hash(v)

    def get(self, cat: str, key: str) -> int:
        lib = getattr(self, cat.upper(), {})
        return lib.get(key, gua_hash(key))

    def all_in(self, cat: str) -> dict:
        return getattr(self, cat.upper(), {})

    def closest(self, target: int, cat: str, n: int = 3) -> list:
        lib = getattr(self, cat.upper(), {})
        scored = [(k, v, hamming(target, v)) for k, v in lib.items()]
        scored.sort(key=lambda x: x[2])
        return scored[:n]

    def all(self) -> dict:
        result = {}
        for cat in dir(self):
            if cat.isupper():
                result.update(getattr(self, cat, {}))
        return result


# ═══════════════ Morpher — 9 Transformations ═══════════════

class GuaMorpher:
    @staticmethod
    def stretch(g: int, factor: int = 3) -> int:
        """Stretch: interleave gaps"""
        r, pos = 0, 0
        for i in range(28):
            bit = (g >> i) & 1
            r |= (bit << min(pos, 27))
            pos += 1
            if (i + 1) % factor == 0 and pos < 27:
                pos += 1
        return r & MASK28

    @staticmethod
    def fold(g: int, at: int = 14) -> int:
        """Fold: XOR halves together"""
        m = (1 << at) - 1
        lo = g & m
        hi = (g >> at) & m
        return ((lo ^ hi) ^ ((lo & hi) << 1)) & MASK28

    @staticmethod
    def mirror(g: int) -> int:
        """Mirror: bit-reverse"""
        r = 0
        for i in range(28):
            if g & (1 << i):
                r |= (1 << (27 - i))
        return r

    @staticmethod
    def rotate(g: int, n: int = 1) -> int:
        """Rotate: cyclic shift"""
        n = n % 28
        return ((g << n) | (g >> (28 - n))) & MASK28

    @staticmethod
    def derive(g: int, n: int = 1) -> int:
        """Derive: nth phase"""
        d = g
        for i in range(n + 1):
            d = ((d << 3) ^ (d >> 5) ^ (i * 0x9E3779B9)) & MASK28
        return d

    @staticmethod
    def fuse(a: int, b: int) -> int:
        """Fuse: interleave odd/even bits"""
        r = 0
        for i in range(14):
            r |= (((a >> i) & 1) << (i * 2))
            r |= (((b >> i) & 1) << (i * 2 + 1))
        return r & MASK28

    @staticmethod
    def split(g: int) -> tuple:
        """Split: deinterleave into even/odd"""
        e = sum(((g >> (i*2)) & 1) << i for i in range(14))
        o = sum(((g >> (i*2+1)) & 1) << i for i in range(14))
        return e & MASK28, o & MASK28

    @staticmethod
    def crystallize(g: int, seed: int = 0) -> int:
        """Crystallize: freeze upper bits, XOR lower with seed"""
        hi = (g >> 14) & 0x3FFF
        lo = (g & 0x3FFF) ^ (seed & 0x3FFF)
        return ((hi << 14) | lo) & MASK28

    @staticmethod
    def dissolve(g: int, solvent: int = 0) -> int:
        """Dissolve: erase bits matching solvent"""
        d = g & ~solvent
        return (d if d != 0 else g ^ solvent) & MASK28


# ═══════════════ Factory ═══════════════

class GuaFactory:
    def __init__(self):
        self.sources = SourceGuaLib()
        self.morpher = GuaMorpher()
        self.produced: list[int] = []
        self.recycled: list[int] = []
        self.archives: dict[str, int] = {}

    def make(self, text: str) -> int:
        g = gua_hash(text)
        self.produced.append(g)
        return g

    def make_chain(self, text: str) -> list[int]:
        chain, prev, shift = [], 0, 0
        for ch in text:
            h = gua_hash(ch)
            linked = ((h << (shift % 8)) ^ prev ^ (prev >> 3)) & MASK28
            chain.append(linked)
            prev = linked
            shift = (shift + 1) % 8
        return chain

    def make_from_source(self, cat: str, key: str) -> int:
        return self.sources.get(cat, key)

    def make_variant(self, base: int, nth: int) -> int:
        return self.morpher.derive(base, nth)

    def morph(self, g: int, op: str, *args) -> int:
        ops = {
            'stretch': lambda: self.morpher.stretch(g, args[0] if args else 3),
            'fold': lambda: self.morpher.fold(g, args[0] if args else 14),
            'mirror': lambda: self.morpher.mirror(g),
            'rotate': lambda: self.morpher.rotate(g, args[0] if args else 1),
            'derive': lambda: self.morpher.derive(g, args[0] if args else 1),
            'fuse': lambda: self.morpher.fuse(g, args[0]) if args else g,
            'crystallize': lambda: self.morpher.crystallize(g, args[0] if args else 0),
            'dissolve': lambda: self.morpher.dissolve(g, args[0] if args else 0),
        }
        return ops.get(op, lambda: g)()

    def morph_chain(self, g: int, ops: list) -> int:
        for op in ops:
            if isinstance(op, tuple):
                g = self.morph(g, op[0], *op[1:])
            else:
                g = self.morph(g, op)
        return g

    def split(self, g: int) -> tuple:
        return self.morpher.split(g)

    def recycle(self, g: int):
        self.recycled.append(g)
        if len(self.recycled) > 5000:
            self.recycled = self.recycled[-2500:]

    def rebirth(self, g: int, seed: int) -> int:
        return ((g ^ seed ^ (seed << 7)) >> 3) & MASK28

    def archive(self, name: str, g: int):
        self.archives[name] = g

    def recall(self, name: str) -> int:
        return self.archives.get(name, 0)

    def as_geometry(self, g: int) -> dict:
        return {
            'x': get_bits(g, 28, 19),
            'y': get_bits(g, 19, 10),
            'z': get_bits(g, 10, 1),
            'scale': get_bits(g, 1, 0),
        }

    def as_color(self, g: int) -> tuple:
        return (get_bits(g, 28, 18), get_bits(g, 18, 9), get_bits(g, 9, 0))

    def as_freq(self, g: int) -> float:
        return get_bits(g, 14, 0) / 16383.0 * 20000.0

    def report(self) -> str:
        cats = [k for k in dir(self.sources) if k.isupper()]
        total = sum(len(getattr(self.sources, c, {})) for c in cats)
        return (f"factory: produced={len(self.produced)} recycled={len(self.recycled)} "
                f"archived={len(self.archives)} sources={total}")


# ═══════════════ GuaStore ═══════════════

class GuaStore:
    def __init__(self):
        self.entries: dict[str, int] = {}
        self.tick = 0

    def encode(self, text: str, attractor: int):
        self.entries[text] = attractor & MASK28
        self.tick += 1

    def size(self) -> int:
        return len(self.entries)

    def recall(self, text: str) -> int:
        return self.entries.get(text, 0)

    @property
    def latest(self) -> int:
        if not self.entries:
            return 0
        return list(self.entries.values())[-1]


Transformer = GuaMorpher

print(f"[guayuan] v8.3 · radical-Gray encode · 28-bit")
