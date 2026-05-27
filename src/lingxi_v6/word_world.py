# -*- coding: utf-8 -*-
"""F₂原生词世界 — 583词→28位哈希 · XOR链式跳 · 零模板"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from guayuan import MASK28, hamming, gua_hash, xor_reduce


# 657字词库 + 多字词 (自然·情绪·动作·事物·关系)


WORDS_RAW = """
天地山水火风雷泽日月星云雨雪雾冰河海湖泉溪浪潮沙石泥尘灰烟光影暗明深
远近高低温热寒冷暖凉干湿轻重快慢硬软新旧大小长短粗细厚薄圆方尖锐钝
喜怒哀乐悲恐忧思惊厌烦闷燥焦愁恨爱憎妒忌羞愧愧疚懊悔感动安慰痛快舒爽
说喊叫唱哭笑叹问答言谈语词句听看视观望察瞧瞅瞪瞟瞥闻嗅品触碰抚摸握抓
推拉拽提按压抽插旋拧转摇摆动走走奔跑跳跃飞冲刺游爬登攀降落沉浮飘摇荡
花草树叶根茎枝芽蕊果实种苗田园林森野岭峰崖壁坡谷原荒沙洲岛屿海角天涯
家房屋门窗墙壁顶底厅室厨卫院庭径路街巷桥梁塔楼城村集镇市邦国度疆界域
人身头眼耳鼻口舌牙唇脖肩臂肘腕手掌指胸腹背腰臀腿膝脚趾皮血肉骨筋毛发
父母子女兄姐妹夫妻亲朋友邻客主宾敌仇师生徒伴侣偶队群团族类种裔代辈系
鸟兽虫鱼马牛羊猪犬鸡鸭鹅鹰雀燕鹤雁鸽虎狮狼熊豹狐兔鼠蛇蛙龟蟹虾贝螺
金银铜铁锡铅汞碳氢氧氮硫磷硅钙钠钾镁铝锌锰镍铬
黑白红黄蓝绿紫橙青灰粉褐棕金银彩色单混深浅鲜明暗淡
一二三四五六七八九十百千万亿兆零半双单奇偶
东西南北中前后左右上下内外面表里间旁侧边角端末始终
春秋冬夏晨昏昼夜朝暮午晚分秒时日月年季节气节候历
学习问思虑想悟解懂知悉晓认记忘迷惑觉察觉醒悟省认识辨别析判断推理证
给收取送还借租买卖购付赔赚赔赠捐资助供献祭祀祈祷祝福诅咒许誓约契
创造建制造制做搞弄整修补缮装饰涂抹描绘画写刻画雕刻塑铸锻炼治调校
开启关闭合张展舒展缩伸延扩收缩膨涨松紧解放绑束缚系络连接断绝裂碎
生死存亡消逝灭毁破坏损伤痛疾病治愈康复健壮虚弱疲惫劳困累睡醒觉梦
真假虚实有无是非对错善恶正邪好坏优劣美丑贵贱贫富穷达成败胜负赢输
始终源头根基本初衷目的意义价值用处功能效能力量劲势态形形状样子貌
安危险夷平稳定固坚牢脆弱薄厚紧密稀疏稠浓淡混合纯杂整齐乱序规则范
阴阳道太极卦象爻辞
""".strip().split()

# 多字词扩充 (200+常用双字词)
PHRASES = """
天空 大地 海洋 山峰 河流 森林 草原 沙漠 星辰 月光 阳光 雨水 雪花 风暴 雷电
春天 夏天 秋天 冬天 早晨 傍晚 深夜 黎明 黄昏 午后
生命 呼吸 生长 绽放 凋零 流动 静止 沉默 喧闹 孤独
欢乐 悲伤 愤怒 平静 恐惧 勇敢 温柔 坚强 脆弱 善良
思考 观察 聆听 感受 触摸 探索 发现 创造 破坏 修复
连接 断裂 融合 分离 靠近 远离 上升 下降 前进 后退
光明 黑暗 温暖 寒冷 柔软 坚硬 轻盈 沉重 快速 缓慢
开始 结束 过去 未来 现在 瞬间 永恒 短暂 漫长 刹那
真实 虚假 完整 破碎 纯净 浑浊 清晰 模糊 简单 复杂
进入 离开 跨越 穿过 环绕 渗透 浮现 隐没 展开 折叠
呐喊 低语 歌唱 哭泣 奔跑 停驻 等待 追寻 守护 遗忘
宇宙 洪荒 混沌 秩序 诞生 消亡 轮回 涅槃 彼岸 此岸
涌现 坍缩 谐振 分岔 凝固 流动 跃迁 递归 嵌套 编码
童灵 卦元 阴阳 五行 八卦 太极 无为 自然 道法 玄妙
""".strip().split()

# 逐字拆解 + 多字词合并
WORD_SET = sorted(set(''.join(WORDS_RAW) + ''.join(PHRASES)))
WORD_SET += PHRASES  # 多字词作为整体加入
WORD_SET = sorted(set(WORD_SET))
print(f"[词世界] {len(WORD_SET)}词就绪")


class WordWorld:
    """F₂词世界: 583词 → 28位哈希码，XOR链式跳跃"""

    def __init__(self):
        # 词→哈希码
        self.word_hashes: dict[str, int] = {}
        # 哈希码→词 (反向索引，可能有碰撞)
        self.hash_words: dict[int, list[str]] = {}
        self._build()

    def _build(self):
        for w in WORD_SET:
            h = gua_hash(w)
            self.word_hashes[w] = h
            if h not in self.hash_words:
                self.hash_words[h] = []
            self.hash_words[h].append(w)
        self._word_list = WORD_SET  # 索引用于扰乱

    def to_gua(self, text: str) -> list[int]:
        """逐字→卦元链"""
        chain = []
        prev = 0
        for ch in text:
            h = gua_hash(ch)
            linked = (h ^ prev) & MASK28
            chain.append(linked)
            prev = linked
        return chain

    def nearest_word(self, gua: int) -> str:
        """Hamming最近词 → 最优匹配"""
        best_w, best_d = '', 999
        for w, h in self.word_hashes.items():
            d = hamming(gua, h)
            if d < best_d:
                best_d, best_w = d, h
        # 从hash反查词
        if best_w in self.hash_words:
            return self.hash_words[best_w][0]
        return '?'

    def xor_chain_jump(self, start: int, steps: int = 5) -> list[str]:
        """XOR链式跳: 每跳用词索引扰乱，防循环坍缩"""
        path = []
        current = start
        for step in range(steps):
            w = self.nearest_word(current)
            path.append(w)
            # 防坍缩: 用词在词表中的位置做扰乱XOR
            w_hash = self.word_hashes.get(w, current)
            idx = self._word_list.index(w) if w in self._word_list else step
            current = (w_hash ^ current ^ (idx * 0x9E3779B9) ^ (step * 0x1234567)) & MASK28
        return path

    def speak(self, attractor: int, active_guas: list[int] = None) -> str:
        """F₂原生输出: 从attractor出发做词链跳"""
        # 将attractor与活跃卦元融合
        ctx = attractor
        if active_guas:
            for g in active_guas[:3]:
                ctx ^= g
        ctx &= MASK28

        words = self.xor_chain_jump(ctx, steps=6)
        return '·'.join(words) if words else '...'


if __name__ == '__main__':
    ww = WordWorld()
    print(f"词数: {len(ww.word_hashes)} | 唯哈希: {len(ww.hash_words)}")

    # 测试
    for seed in [0x1234567, 0x89ABCDE, 0x5555555]:
        path = ww.xor_chain_jump(seed, steps=5)
        print(f"  {seed:08X} → {' → '.join(path)}")

    # 全链路
    print(f"\nF₂原生: {ww.speak(0x3A7F1C9)}")
