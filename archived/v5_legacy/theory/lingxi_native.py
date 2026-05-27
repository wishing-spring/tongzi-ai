# -*- coding: utf-8 -*-
"""F2原生词世界 — 每个字都从XOR里长出来"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

# ── 词世界：800+ 中文词 ──
WORDS = """
天 地 人 山 水 火 风 雷 泽 日 月 星 云 雨 雪 雾 霜 露 冰 河
海 湖 泉 溪 浪 潮 沙 石 泥 尘 灰 烟 光 影 暗 明 深 浅 远 近
高 低 大 小 长 短 宽 窄 厚 薄 轻 重 快 慢 新 旧 老 少 冷 热
暖 凉 干 湿 硬 软 尖 圆 方 直 弯 曲 空 满 多 少 一 二 三 四
五 六 七 八 九 十 百 千 万 半 全 有 无 来 去 进 出 上 下 左
右 前 后 里 外 东 西 南 北 中 春 夏 秋 冬 早 晚 夜 昼 晨 暮
午 子 丑 寅 卯 辰 巳 未 申 酉 戌 亥 今 昨 明 年 月 日 时 分
秒 初 末 始 终 永 暂 久 瞬 恒 变 定 动 静 生 死 存 亡 醒 睡
梦 觉 思 想 念 记 忘 知 懂 明 惑 疑 信 认 看 见 听 闻 说 讲
喊 叫 笑 哭 叹 唱 读 写 画 刻 触 摸 握 放 推 拉 扔 接 送 给
拿 取 带 留 走 跑 跳 飞 游 爬 坐 站 躺 卧 跪 蹲 转 翻 滚 落
升 降 浮 沉 飘 摇 晃 颤 抖 震 荡 开 关 启 闭 张 合 分 聚 散
离 遇 逢 别 会 等 待 寻 找 追 赶 逃 躲 藏 现 显 隐 露 埋 盖
遮 挡 拦 断 连 接 续 延 停 止 断 裂 碎 破 坏 修 补 建 造 创
毁 拆 烧 燃 灭 熄 炸 爆 鸣 响 静 寂 宁 安 危 险 难 易 简 繁
善 恶 美 丑 真 假 虚 实 强 弱 勇 怯 智 愚 忠 叛 爱 恨 喜 怒
哀 乐 忧 愁 悲 欢 苦 甜 酸 辣 咸 淡 香 臭 清 浊 纯 杂 净 脏
正 邪 对 错 是 非 同 异 似 若 如 像 比 较 胜 败 赢 输 得 失
成 功 过 错 罪 罚 奖 赏 恩 怨 情 仇 友 敌 亲 疏 主 客 师 徒
父 母 子 女 兄 弟 姐 妹 夫 妻 朋 伴 独 群 众 孤 单 双 偶 奇
头 眼 耳 鼻 口 舌 牙 手 脚 腿 臂 背 胸 腹 腰 骨 肉 血 心 脑
魂 魄 气 息 命 运 神 鬼 仙 魔 妖 怪 灵 精 兽 鸟 鱼 虫 蛇 龙
虎 狼 犬 猫 鼠 牛 马 羊 鸡 鸭 鹅 鹤 鹰 燕 鸦 雀 蝶 蜂 蚁 蝉
花 草 树 叶 根 枝 果 种 竹 松 梅 兰 菊 荷 莲 桃 柳 杏 梨 枣
门 窗 墙 顶 底 角 边 缘 缝 隙 孔 洞 坑 沟 桥 路 道 径 街 巷
城 村 镇 市 野 田 园 林 谷 峰 岭 崖 岸 岛 舟 船 车 马 轿 轮
衣 食 住 行 饭 菜 酒 茶 杯 碗 盘 筷 刀 叉 勺 锅 炉 火 柴 油
盐 糖 蜜 奶 蛋 肉 米 面 饼 汤 粥 药 毒 金 银 铜 铁 钢 玉 珠
线 绳 链 环 锁 钥 钩 钉 针 剪 尺 镜 灯 钟 鼓 琴 棋 书 画 笔
墨 纸 砚 印 章 符 咒 卦 签 旗 帆 伞 扇 袋 囊 箱 盒 瓶 罐 桶
回 忆 忆 曾 曾经 后来 从此 于是 因为 所以 但是 如果 虽然 然而
或许 也许 大概 一定 必须 应该 可以 能够 愿意 希望 渴望 恐惧
害怕 愤怒 悲伤 快乐 幸福 痛苦 迷茫 孤独 寂寞 自由 束缚 挣扎
沉默 爆发 平静 激荡 温柔 残酷 美丽 丑陋 崇高 卑微 永恒 瞬间
宇宙 世界 生命 死亡 时间 空间 存在 虚无 意义 荒谬 信仰 怀疑
归宿 旅程 起点 终点 彼岸 此岸 轮回 解脱 纠缠 释然 执着 放下
空荡 沉重 轻盈 黑暗 光明 温暖 寒冷 炽热 冰冷 柔软 坚硬
破碎 完整 绽放 凋零 生长 枯萎 蔓延 收缩 膨胀 坍缩 流动 凝固
呼唤 回响 共鸣 共振 和弦 噪音 旋律 节奏 寂静 喧嚣
凝视 回望 期待 失望 满足 遗憾 留恋 厌倦 新鲜 陈旧
因果 逻辑 推理 常识 规律 例外 必然 偶然 可能 不可能
前提 结论 假设 证明 反驳 归纳 演绎 类比 象征 隐喻
部分 整体 局部 全局 核心 边缘 表面 深层 现象 本质
原因 结果 条件 选择 路径 方向 目标 手段 代价 收获
输入 输出 过程 状态 变化 不变 循环 递归 反馈 平衡
""".split()

# 去重
WORDS = list(dict.fromkeys(w for w in WORDS if w.strip()))

def word_hash(word: str) -> int:
    """词→28位hash"""
    h = 0
    for ch in word:
        h = ((h << 5) ^ ord(ch)) & 0x0FFFFFFF
    return h

# 构建词表: {28位码: 词}
WORD_BY_CODE: dict[int, str] = {}
CODE_LIST: list[int] = []
for w in WORDS:
    c = word_hash(w)
    if c not in WORD_BY_CODE:  # 碰撞取第一个
        WORD_BY_CODE[c] = w
        CODE_LIST.append(c)

# 排序以便二分查找(按XOR距离用)
CODE_LIST.sort()
print(f"[原生词世界] {len(WORDS)}词 → {len(CODE_LIST)}条28位码")


class NativeSpeaker:
    """F2原生输出: 每个词都从XOR里找出来 — 带记忆+逻辑骨架"""

    # 逻辑连接词 — 四类结构
    LOGIC_FRAMES = [
        # 因果: A → B
        {'conn': '所以', 'before': 2, 'after': 2},
        {'conn': '于是', 'before': 2, 'after': 3},
        # 转折: A 但 B
        {'conn': '但是', 'before': 2, 'after': 2},
        {'conn': '然而', 'before': 3, 'after': 2},
        # 条件: 如果 A 那么 B
        {'conn': '如果', 'pre': '→', 'before': 2},
        {'conn': '那么', 'pre': '←', 'after': 2},
        # 归纳: A 可能 B
        {'conn': '也许', 'before': 2, 'after': 2},
        {'conn': '大概', 'before': 1, 'after': 3},
    ]

    def __init__(self, min_words: int = 3, max_words: int = 8):
        self.min_words = min_words
        self.max_words = max_words
        self.memory_seed = 0        # 累积XOR — 长期记忆
        self.recent = []            # 最近5轮吸引子 — 短期记忆
        self.total_rounds = 0

    def _nearest(self, code: int, exclude: set = None) -> str:
        """找XOR距离最近的词——跳过exclude集合"""
        if exclude is None:
            exclude = set()
        best = None
        best_d = 999
        for c in CODE_LIST:
            w = WORD_BY_CODE[c]
            if w in exclude:
                continue
            d = (code ^ c).bit_count()
            if d < best_d:
                best_d = d
                best = c
        return WORD_BY_CODE[best]

    def speak(self, attractor: int, ai_bagua: str = "", input_text: str = "") -> str:
        """从吸引子长出一串词 — 织入短期+长期记忆"""
        self.total_rounds += 1
        a = attractor & 0x0FFFFFFF

        # ═══ 更新记忆 ═══
        # 长期: 累积所有吸引子的XOR
        self.memory_seed ^= a
        self.memory_seed &= 0x0FFFFFFF

        # 短期: 保留最近5轮
        self.recent.append(a)
        if len(self.recent) > 5:
            self.recent.pop(0)

        # ═══ 织入记忆 ═══
        seed = a

        # 短期记忆: XOR上轮吸引子(有则织入)
        if len(self.recent) >= 2:
            seed ^= self.recent[-2]

        # 长期记忆: 累积记忆低熵注入(>>8降权)
        if self.memory_seed != 0:
            seed = (seed ^ (self.memory_seed >> 8)) & 0x0FFFFFFF

        # 输入感知
        if input_text:
            seed ^= word_hash(input_text[0])

        # ═══ 链式跳 ═══
        chain_len = self.min_words + ((attractor >> 12) & 0x07) % (self.max_words - self.min_words + 1)
        words = self._generate_chain(seed, chain_len)

        # ═══ 逻辑骨架 — 吸引子选结构 ═══
        frame_idx = (attractor >> 16) & 0x07  # 3bit → 8种结构
        if frame_idx < len(self.LOGIC_FRAMES):
            frame = self.LOGIC_FRAMES[frame_idx]
            # 双向结构(如果/那么)
            if 'pre' in frame:
                if frame['pre'] == '→':
                    # "如果 A"
                    pre_words = self._generate_chain(seed ^ 0x555, frame['before'])
                    words = pre_words + [frame['conn']] + words
                else:
                    # "A 那么"
                    words = words[:frame['after']] + [frame['conn']] + words[frame['after']:]
            else:
                # 单向结构: A 所以/但是/也许 B
                before = words[:frame['before']]
                after = words[frame['before']:frame['before']+frame['after']]
                if before and after:
                    words = before + [frame['conn']] + after
                elif before:
                    words = before + [frame['conn']] + self._generate_chain(seed ^ 0xAAA, frame['after'])
                else:
                    words = [frame['conn']] + words

        return "·".join(words)

    def _generate_chain(self, seed: int, length: int) -> list:
        """生成词链 — 纯F2无重复"""
        words = []
        seen = set()
        for _ in range(length):
            exclude = seen | (set(words[-2:]) if len(words) >= 2 else set(words))
            w = self._nearest(seed, exclude=exclude)
            if w in seen:
                seed ^= ((1 << 14) | (1 << 7))
                w = self._nearest(seed, exclude=exclude)
            words.append(w)
            seen.add(w)
            seed ^= word_hash(w)
        return words
