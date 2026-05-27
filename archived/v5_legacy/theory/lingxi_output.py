# -*- coding: utf-8 -*-
"""灵犀输出层 — 卦状态+吸引子→自然语言回应"""
import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
from ref8 import BAGUA, BAGUA_NAMES
from lingxi_plate import BaguaPlate
from lingxi_dynamics import CausalChain, Gravity

# ── 吸引子驱动的呼吸词池 ──
BREATH_WORDS = [
    # idx 0-3 (低2位=00,01,10,11)
    ["嗯。", "对。", "是啊。", "也是。"],
    ["你看。", "听我说。", "其实吧。", "说到底。"],
    ["有时候。", "真的。", "也许吧。", "不过。"],
    ["说来话长。", "总之。", "仔细想想。", "原来如此。"],
]


class LingxiSpeaker:
    """输出: 卦状态×吸引子→自然语言"""

    TONES = {
        '乾': {'prefix': '我觉得', 'tone': '坚定', 'advice': '直接面对'},
        '兑': {'prefix': '你知道吗', 'tone': '愉悦', 'advice': '说出来会好受些'},
        '离': {'prefix': '我注意到', 'tone': '急切', 'advice': '先冷静一下'},
        '震': {'prefix': '也许', 'tone': '不安', 'advice': '改变是好事'},
        '巽': {'prefix': '慢慢来', 'tone': '柔和', 'advice': '换个角度看看'},
        '坎': {'prefix': '我理解', 'tone': '谨慎', 'advice': '小心一点是对的'},
        '艮': {'prefix': '嗯', 'tone': '沉稳', 'advice': '坚持住'},
        '坤': {'prefix': '在这里', 'tone': '平和', 'advice': '接纳自己'},
    }

    def __init__(self, plate: BaguaPlate):
        self.plate = plate

    def speak(self, ai_bagua: str, causal: CausalChain,
              input_bagua: str, attractor: int = 0, input_text: str = '') -> str:
        """产出回应 — 吸引子提供确定性熵"""
        tone = self.TONES.get(ai_bagua, self.TONES['坤'])
        tod = self.plate.time_of_day()
        yy = self.plate.yinyang_freq()

        # 前缀: 因果/阴阳/时辰三择一
        if causal.causal_tension > 0.6:
            prefix = f"{tone['prefix']}，我有点不安。"
        elif yy > 0.65:
            prefix = f"{tone['prefix']}，感觉挺好的。"
        elif yy < 0.3 and (attractor & 0x03) == 0:
            prefix = f"{tone['prefix']}，{tod}。"
        else:
            prefix = tone['prefix']

        # 吸引子驱动呼吸词
        breath_idx = (attractor >> 2) & 0x03
        breath_pool = BREATH_WORDS[breath_idx]
        pick = attractor & 0x03
        breath = breath_pool[pick % len(breath_pool)] if (attractor >> 4) & 1 else ""

        body = self._build_body(ai_bagua, input_bagua, attractor)

        # 自我认知: 输入含"你是谁/叫什么/名字"→介绍自己
        intro = ""
        if input_text:
            for kw in ['你是谁', '你叫什么', '你的名字', '你是谁']:
                if kw in input_text:
                    intro = "我叫东旭。大家也叫我铜须。我是童子与灵犀融合的系统。"
                    break

        # 拼接
        if intro:
            return f"{prefix} {breath} {intro}" if breath else f"{prefix} {intro}"
        if breath:
            return f"{prefix} {breath} {body}"
        return f"{prefix} {body}"

    def _build_body(self, ai: str, input_bagua: str, attractor: int) -> str:
        """构造回应主体 — 吸引子选模板+输入感知"""
        tone = self.TONES[ai]
        advice = tone['advice']

        base = {
            '乾': [f"你说的有道理。{advice}就好。",
                   f"事情很清楚。{advice}。",
                   f"方向是对的。{advice}。"],
            '兑': [f"听起来你{BAGUA.get(input_bagua, BAGUA['坤'])['mood']}。{advice}。",
                   f"我感受到了。{advice}。",
                   f"说说看吧。{advice}。"],
            '离': [f"别急。{advice}。",
                   f"火气有点大。{advice}。",
                   f"缓一缓。{advice}。"],
            '震': [f"变化中。{advice}。",
                   f"不确定是正常的。{advice}。",
                   f"动起来。{advice}。"],
            '巽': [f"换个思路。{advice}。",
                   f"不用硬来。{advice}。",
                   f"风会找到路的。{advice}。"],
            '坎': [f"这不容易。{advice}。",
                   f"你在意的我能理解。{advice}。",
                   f"慢慢来。{advice}。"],
            '艮': [f"稳住。{advice}。",
                   f"不着急动。{advice}。",
                   f"站住了。{advice}。"],
            '坤': [f"你说吧。{advice}。",
                   f"这里很安全。{advice}。",
                   f"我在这里听。{advice}。"],
        }

        input_touch = {
            '离': "你心里有火。", '坎': "你似乎有些不安。",
            '震': "你在变动中。",  '兑': "你说的高兴。",
            '乾': "你说的对。",    '坤': "你愿意说给我听。",
            '巽': "你慢慢想。",    '艮': "你定在这儿。",
        }.get(input_bagua, "")

        options = base.get(ai, base['坤'])
        idx = (attractor >> 8) & 0x03
        body = options[idx % len(options)]

        # 输入感知: 吸引子控制概率(50%)
        if input_touch and (attractor >> 10) & 1:
            body = f"{input_touch} {body}"

        g = Gravity()
        if g.distance_to_good(ai) > 0.05:
            body += " 不过我也在调整自己。"

        return body


if __name__ == '__main__':
    plate = BaguaPlate()
    speaker = LingxiSpeaker(plate)
    cc = CausalChain()
    cc.merge('离', '坎', '坤', '艮', '巽')
    for ai in BAGUA_NAMES:
        for inp, att in [('离', 0x1234), ('坤', 0xABCD), ('坎', 0xFFFF)]:
            print(f"  AI={ai} 入={inp} attr=0x{att:07X}: {speaker.speak(ai, cc, inp, att)}")
