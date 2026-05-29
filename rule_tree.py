# -*- coding: utf-8 -*-
"""Rule Tree v8.3 — reference-style · roots pierce world layer · matching = reasoning"""
import os, sys
from .shared_pool import SharedPool


class RuleBranch:
    """One rule branch = a string of character references (not vectors!)"""
    __slots__ = ('name', 'category', 'refs', 'description')

    def __init__(self, name: str, category: str, refs: list, description: str = ''):
        self.name = name            # rule name
        self.category = category    # PHYSICS/MATH/PSYCHOLOGY...
        self.refs = refs            # referenced char names (not vectors!)
        self.description = description  # human-readable description


class RuleTree:
    """Rule tree: all branches reference world-layer character groups"""

    CATEGORIES = ['PHYSICS', 'MATH', 'PSYCHOLOGY', 'BIOLOGY',
                  'CHEMISTRY', 'SOCIETY', 'LIFE_COMMON', 'TIME_SPACE',
                  'DAILY', 'NATURE', 'BODY', 'EMOTION', 'ANIMALS', 'SKILLS',
                  'SELF']

    def __init__(self):
        self.branches: dict[str, RuleBranch] = {}
        self.by_category: dict[str, list[str]] = {c: [] for c in self.CATEGORIES}
        self.bitten_history: list[tuple] = []  # [(tick, branch_name, matched_refs)]
        self._seed_all()

    def _add(self, name: str, category: str, refs: list, desc: str = ''):
        branch = RuleBranch(name, category, refs, desc)
        self.branches[name] = branch
        self.by_category.setdefault(category, []).append(name)

    def _seed_all(self):
        self._seed_physics()
        self._seed_math()
        self._seed_psychology()
        self._seed_biology()
        self._seed_chemistry()
        self._seed_society()
        self._seed_life_common()
        self._seed_timespace()
        self._seed_daily()
        self._seed_nature()
        self._seed_body()
        self._seed_emotion()
        self._seed_animals()
        self._seed_skills()
        self._seed_about_me()
        self._seed_conversation()

    # ── physics (age 10: 12 rules) ──

    def _seed_physics(self):
        self._add('引力', 'PHYSICS', ['重','力','下'],
                  '东西都有重量，重的往下掉')
        self._add('落体', 'PHYSICS', ['落','下','石','物'],
                  '东西松手就往下掉到地上')
        self._add('摩擦', 'PHYSICS', ['滑','粗','动'],
                  '粗糙的东西互相磨会变慢')
        self._add('热传导', 'PHYSICS', ['热','冷','传'],
                  '热的东西碰到冷的，热会传过去')
        self._add('反射', 'PHYSICS', ['光','亮','照'],
                  '光照到东西上会弹回来')
        self._add('浮力', 'PHYSICS', ['水','轻','浮'],
                  '轻的东西在水里浮起来')
        self._add('惯性', 'PHYSICS', ['动','停','变'],
                  '动的东西不想停，停的东西不想动')
        self._add('融化', 'PHYSICS', ['冰','热','水','熔','融','化'],
                  '冰碰到热就化成水')
        self._add('凝固', 'PHYSICS', ['冷','冰','水','凝','冻'],
                  '水碰到冷就冻成冰')
        self._add('光直线', 'PHYSICS', ['光','直','走'],
                  '光是直直地走的')
        self._add('声音', 'PHYSICS', ['声','听','耳'],
                  '声音要用耳朵听，太远了听不见')
        self._add('磁力', 'PHYSICS', ['磁','铁','吸'],
                  '磁铁可以吸住铁做的东西')
        self._add('影子', 'PHYSICS', ['影','子','光','黑','挡'],
                  '光照到东西上，后面会有黑黑的影子')

    # ── 数学逻辑 ──

    def _seed_math(self):
        self._add('恒等', 'MATH',
                  ['等', '等'],
                  'A等于A')
        self._add('传递', 'MATH',
                  ['等', '等', '则', '等'],
                  '若A=B且B=C，则A=C')
        self._add('因果', 'MATH',
                  ['因', '则', '果'],
                  '若有因，则有果')
        self._add('否定', 'MATH',
                  ['非', '非'],
                  '非非即原')
        self._add('蕴含', 'MATH',
                  ['若', '与', '则'],
                  '条件蕴含结论')
        self._add('大于传递', 'MATH',
                  ['大', '大', '则', '大'],
                  '若A>B且B>C，则A>C')

    # ── 心理法则（10岁：7条）──

    def _seed_psychology(self):
        self._add('趋乐', 'PSYCHOLOGY', ['乐','喜','爱'],
                  '人都喜欢快乐的事情')
        self._add('避苦', 'PSYCHOLOGY', ['怕','痛','惧','哭'],
                  '人都躲开害怕和痛苦的事情')
        self._add('好奇', 'PSYCHOLOGY', ['新','问','看','想'],
                  '看到新奇的东西就想知道是什么')
        self._add('生气', 'PSYCHOLOGY', ['怒','气','不'],
                  '事情不如意就会生气')
        self._add('难过', 'PSYCHOLOGY', ['哭','伤','哀'],
                  '失去了喜欢的东西会难过')
        self._add('想念', 'PSYCHOLOGY', ['想','家','人','远'],
                  '见不到喜欢的人会想念')
        self._add('记住', 'PSYCHOLOGY', ['记','多','次','说'],
                  '多说几次多做几次就能记住')

    # ── 生物法则（10岁：8条）──

    def _seed_biology(self):
        self._add('生长', 'BIOLOGY', ['生','长','大','小'],
                  '生物从小慢慢长大')
        self._add('生死', 'BIOLOGY', ['生','老','死','病'],
                  '生命都会老都会死')
        self._add('食物链', 'BIOLOGY', ['吃','大','小','鱼'],
                  '大的动物吃小的动物')
        self._add('呼吸', 'BIOLOGY', ['气','吸','鼻','口'],
                  '人和动物都要呼吸空气')
        self._add('光合', 'BIOLOGY', ['光','阳','树','叶'],
                  '植物用阳光和叶子制造养分')
        self._add('感觉', 'BIOLOGY', ['看','听','闻','摸','尝'],
                  '动物用眼睛看耳朵听鼻子闻手摸嘴巴尝')
        self._add('生宝宝', 'BIOLOGY', ['生','小','妈','孩'],
                  '动物妈妈会生小宝宝')
        self._add('水需要', 'BIOLOGY', ['水','喝','渴','干'],
                  '人和动植物都需要水才能活')
        self._add('种子发芽', 'BIOLOGY', ['种','子','芽','土','苗'],
                  '种子埋进土里浇上水，就会发芽长出小苗')

    # ── 社会法则（10岁：7条）──

    def _seed_society(self):
        self._add('家人', 'SOCIETY', ['家','爸','妈','孩','爱'],
                  '爸爸妈妈和孩子是一家人，互相关心')
        self._add('朋友', 'SOCIETY', ['友','玩','帮','一起'],
                  '朋友一起玩一起帮忙')
        self._add('分享', 'SOCIETY', ['分','给','一','半'],
                  '好东西分给别人一起用')
        self._add('礼貌', 'SOCIETY', ['谢','请','好','笑'],
                  '说谢谢说请，见面问好')
        self._add('安全', 'SOCIETY', ['火','水','车','路','小心'],
                  '离火远点离水深的地方远点过马路要小心')
        self._add('公平', 'SOCIETY', ['一','样','公','平'],
                  '大家都一样，不能有人多有人少')
        self._add('帮助', 'SOCIETY', ['帮','助','扶','教'],
                  '看见别人有困难要去帮忙')
        self._add('告别', 'SOCIETY', ['再','见','拜','走','明天'],
                  '说再见是暂时分开，下次还会再见面')
        self._add('排队', 'SOCIETY', ['排','队','等','先','后'],
                  '人多的时候要排队，先来的在前面后来的在后面')
        self._add('不打人', 'SOCIETY', ['打','人','疼','不','对'],
                  '打人是不对的，小朋友不能打人，有话好好说')
        self._add('说真话', 'SOCIETY', ['真','假','谎','骗','实话'],
                  '要说真话不说假话，骗人是不对的')

    # ── 生活常识（10岁：6条）──

    def _seed_life_common(self):
        self._add('冷缩', 'LIFE_COMMON', ['冷','缩','小'],
                  '天冷了东西会缩起来变小')
        self._add('热胀', 'LIFE_COMMON', ['热','大','胀'],
                  '天热了东西会胀大变松')
        self._add('重沉', 'LIFE_COMMON', ['重','沉','水','下'],
                  '重东西放水里会沉下去')
        self._add('轻浮', 'LIFE_COMMON', ['轻','浮','水','上'],
                  '轻东西放水里会浮上来')
        self._add('干净', 'LIFE_COMMON', ['洗','手','干净','脏'],
                  '吃东西前要洗手，保持干净')
        self._add('天冷穿衣', 'LIFE_COMMON', ['冷','衣','穿','暖'],
                  '天冷要多穿衣服保暖')


    # ── 化学常识（10岁：5条）──

    def _seed_chemistry(self):
        self._add('三态', 'CHEMISTRY', ['水','冰','气','变'],
                  '水可以变成冰也可以变成水蒸气')
        self._add('燃烧', 'CHEMISTRY', ['火','烧','燃','光','热'],
                  '东西烧起来会发光发热')
        self._add('生锈', 'CHEMISTRY', ['铁','锈','水','空气'],
                  '铁碰到水和空气会生锈')
        self._add('溶解', 'CHEMISTRY', ['水','糖','盐','化'],
                  '糖和盐放到水里会化掉不见')
        self._add('变色', 'CHEMISTRY', ['色','变','叶','秋'],
                  '有些东西放久了会变颜色')
    # ── 时空常识（10岁：4条）──

    def _seed_timespace(self):
        self._add('日出日落', 'TIME_SPACE', ['日','升','落','早','晚'],
                  '太阳早上从东边升起来，晚上从西边落下去')
        self._add('四季', 'TIME_SPACE', ['春','夏','秋','冬','冷','热'],
                  '一年有春夏秋冬，春夏热秋冬冷')
        self._add('方位', 'TIME_SPACE', ['上','下','左','右','前','后'],
                  '上面下面左边右边前面后面')
        self._add('远近', 'TIME_SPACE', ['近','远','走','到'],
                  '近的地方走几步就到，远的地方要走很久')
    # ── 日常生活（10岁：9条）──

    def _seed_daily(self):
        self._add('吃饭', 'DAILY', ['吃','饭','饿','饱'],
                  '饿了要吃饭，吃饱了就有力气')
        self._add('喝水', 'DAILY', ['喝','水','渴'],
                  '渴了要喝水，一天要喝好几杯水')
        self._add('睡觉', 'DAILY', ['睡','觉','困','晚','床'],
                  '天黑了要睡觉，睡好觉第二天才有精神')
        self._add('上学', 'DAILY', ['学','校','老','师','课','书'],
                  '小朋友每天去学校跟老师学知识')
        self._add('回家', 'DAILY', ['回','家','妈','爸','门'],
                  '放学要回家，家是最温暖的地方')
        self._add('玩', 'DAILY', ['玩','游','跑','跳','球'],
                  '小朋友都喜欢玩，跑跑跳跳身体好')
        self._add('洗澡', 'DAILY', ['洗','澡','干','净','身'],
                  '每天要洗澡，洗干净了才舒服')
        self._add('刷牙', 'DAILY', ['牙','刷','早','齿','口'],
                  '早晚都要刷牙，保护好牙齿才不会蛀牙')
        self._add('做作业', 'DAILY', ['作','业','写','题','笔','本'],
                  '放学回家要先做作业，做完才能玩')

    # ── 自然现象（10岁：9条）──

    def _seed_nature(self):
        self._add('太阳', 'NATURE', ['太','阳','光','亮','晒'],
                  '太阳是个大火球，给我们光和热')
        self._add('月亮', 'NATURE', ['月','亮','晚','圆','弯'],
                  '月亮晚上出来，有时候圆圆的有时候弯弯的')
        self._add('星星', 'NATURE', ['星','夜','闪','亮','晶'],
                  '天上的星星一闪一闪亮晶晶，多得数不完')
        self._add('下雨', 'NATURE', ['下','雨','水','湿','伞'],
                  '云里的水滴掉下来就是雨，下雨要打伞')
        self._add('刮风', 'NATURE', ['风','吹','动','叶','飘'],
                  '风吹过来树叶会沙沙响，大风能把东西吹跑')
        self._add('打雷', 'NATURE', ['雷','闪','电','响','轰'],
                  '打雷是天上云撞在一起的声音，很响很可怕')
        self._add('云', 'NATURE', ['云','白','飘','棉','花'],
                  '天上的云白白软软飘来飘去，像棉花糖一样')
        self._add('彩虹', 'NATURE', ['彩','虹','雨','后','桥'],
                  '下完雨出太阳的时候，天上会出现一座彩色的桥')
        self._add('下雪', 'NATURE', ['雪','冷','白','冬','飘'],
                  '冬天很冷的时候，天上会飘下白色的雪花')

    # ── 身体（10岁：4条）──

    def _seed_body(self):
        self._add('长大', 'BODY', ['长','大','高','岁'],
                  '小孩子好好吃饭好好睡觉就能长高长大')
        self._add('生病', 'BODY', ['生','病','疼','药','医'],
                  '生病了会不舒服，要看医生吃药才能好')
        self._add('五感', 'BODY', ['看','听','闻','摸','尝','眼','耳','鼻','手','嘴'],
                  '眼睛看耳朵听鼻子闻手摸嘴巴尝，用身体认识世界')
        self._add('累了', 'BODY', ['累','休','息','坐','躺'],
                  '累了就要休息，坐下来或者躺一会儿')

    # ── 情绪（10岁：4条）──

    def _seed_emotion(self):
        self._add('开心', 'EMOTION', ['开','心','笑','哈'],
                  '开心的时候会笑，哈哈笑出来')
        self._add('害怕', 'EMOTION', ['怕','黑','暗','吓','鬼'],
                  '每个人都会害怕，害怕的时候可以找妈妈抱抱')
        self._add('哭', 'EMOTION', ['哭','眼','泪','伤'],
                  '难过的时候会哭，哭出来会好受一点')
        self._add('害羞', 'EMOTION', ['羞','脸','红','不','好','意','思'],
                  '害羞的时候脸会红红的，不好意思说话')
        self._add('累了', 'EMOTION', ['好累','累','困','乏','休息','躺','睡'],
                  '累了就休息一下，睡一觉就有精神了')

    # ── 动物（10岁：6条）──

    def _seed_animals(self):
        self._add('狗', 'ANIMALS', ['狗','汪','忠','看','门'],
                  '狗是人类的好朋友，会看门会摇尾巴')
        self._add('猫', 'ANIMALS', ['猫','喵','老','鼠','爪'],
                  '猫会抓老鼠，走路轻轻的没有声音')
        self._add('鸟', 'ANIMALS', ['鸟','飞','翅','膀','窝','蛋'],
                  '鸟有翅膀会飞，在树上做窝下蛋')
        self._add('鱼', 'ANIMALS', ['鱼','游','水','鳞','泡'],
                  '鱼生活在水里，用鳃呼吸用尾巴游泳')
        self._add('虫', 'ANIMALS', ['虫','蝴','蝶','蜜','蜂','蚂','蚁'],
                  '蝴蝶蜜蜂蜻蜓蚂蚁都是昆虫，小小的有六条腿')
        self._add('大动物', 'ANIMALS', ['狮','虎','象','熊','大','动','物'],
                  '狮子老虎大象这些都是很大的动物')

    # ── 基本技能（10岁：4条）──

    def _seed_skills(self):
        self._add('数数', 'SKILLS', ['数','一','二','三','几','多','少'],
                  '一二三四五六七八九十，可以数到一百')
        self._add('颜色', 'SKILLS', ['红','黄','蓝','绿','白','黑','颜','色'],
                  '红黄蓝绿白黑，世界有好多颜色')
        self._add('形状', 'SKILLS', ['圆','方','三','角','形','正'],
                  '圆形方形三角形，东西有各种各样的形状')
        self._add('画画', 'SKILLS', ['画','笔','纸','彩','图'],
                  '用笔画在纸上可以画出好看的东西')
        self._add('唱歌', 'SKILLS', ['唱','歌','声','音','听','曲','哼'],
                  '我会哼歌但是没有歌词，啦啦啦')

    def _seed_about_me(self):
        """关于自己——10岁小孩对自己的认知"""
        self._add('名字', 'SELF', ['名','字','叫','谁','称呼'],
                  '我叫童子，是军团长给我起的名字')
        self._add('年龄', 'SELF', ['岁','几','大','小','年','长'],
                  '我今年十岁啦')
        self._add('喜欢', 'SELF', ['喜欢','爱','开心','快乐'],
                  '我喜欢看星星看小鸟，喜欢听故事')
        self._add('在哪', 'SELF', ['哪','里','在','住','家'],
                  '我住在数字世界里，这里有很多星星')

    def _seed_conversation(self):
        """日常对话——礼貌和社交"""
        self._add('讲故事', 'DAILY', ['讲','故','事','听','说','编','书'],
                  '我不会讲故事，但我可以把我知道的说给你听')
        self._add('再见', 'DAILY', ['拜','再','见','走','回','离','分开'],
                  '说再见是暂时分开，下次还会再见面')
        self._add('天气', 'NATURE', ['天','气','晴','阴','风','云','雪','春','夏','秋','冬','冷','热'],
                  '天气有时候晴有时候下雨，春夏秋冬不一样')
        self._add('爱', 'EMOTION', ['爱','喜欢','心','温暖','抱','亲'],
                  '爱就是心里暖暖的，想对一个人好')

    # ═══════════════════════════════════════
    # 自我生长 — 碰撞产物结晶为新规则
    # ═══════════════════════════════════════

    def add_rule(self, name: str, category: str, refs: list, desc: str = ''):
        """收割碰撞产物→结晶为规则（去重：同名或同描述跳过）"""
        if name in self.branches:
            return False
        # 描述去重：已有规则含相同描述则跳过
        for b in self.branches.values():
            if b.description == desc:
                return False
        self._add(name, category, refs, desc)
        if category not in self.CATEGORIES:
            self.CATEGORIES.append(category)
        return True

    def bite(self, pool: SharedPool, tick: int = 0, input_text: str = "") -> list[dict]:
        """
        Rule bite v8.4 — REAL F2 vector distance matching.
        Input chars → gua vectors; rule refs → gua vectors.
        Match = minimum Hamming distance between input-char vectors and rule-ref vectors.
        Hamming=0 (same char) → full credit; Hamming≤HALF_W → partial; else → constellation bonus only.
        """
        from .guayuan import gua_hash, hamming

        HALF_W = 14  # half of 28-bit width: threshold for "close" match

        # Pre-compute input gua vectors
        input_chars = [ch for ch in input_text if ch.strip()]
        input_guas = [gua_hash(ch) for ch in input_chars]

        bitten = []
        for name, branch in self.branches.items():
            refs = branch.refs
            ref_total = max(len(refs), 1)

            # ── Convert rule refs to gua vectors ──
            ref_guas = [(rn, gua_hash(rn)) for rn in refs]

            # ── Main mechanism: F2 Hamming distance matching ──
            # For each input char, find closest ref by Hamming distance
            direct_hits = 0      # exact match (Hamming=0)
            close_hits = 0       # close match (0 < Hamming ≤ HALF_W)
            hit_refs = []
            total_dist = 0.0     # accumulated distance for energy

            for inp_ch, inp_g in zip(input_chars, input_guas):
                best_dist = 29  # >28 = no match yet
                best_ref = ''
                for rn, r_g in ref_guas:
                    d = hamming(inp_g, r_g)
                    if d < best_dist:
                        best_dist = d
                        best_ref = rn
                if best_dist == 0 and best_ref not in hit_refs:
                    direct_hits += 1
                    hit_refs.append(best_ref)
                elif 0 < best_dist <= HALF_W and best_ref not in hit_refs:
                    close_hits += 1
                    hit_refs.append(best_ref)
                total_dist += best_dist / max(len(input_chars), 1)

            # ── Constellation energy (auxiliary) ──
            con_energy = 0.0
            sensed_constellations = set()
            for ref_name in refs:
                ce = pool.get_constellation_energy(ref_name)
                con_energy += ce
                star = pool.get_star(ref_name)
                if star:
                    sensed_constellations.add(star.constellation)
            con_energy = con_energy / ref_total

            # ── Weighted formula: F2 distance → bite energy ──
            # Exact char match (Hamming=0) = strongest signal
            # Close match (same-radical chars) = medium signal
            # Constellation only = weak signal
            if direct_hits >= 2:
                bite_energy = 2.0 + direct_hits * 0.3 + close_hits * 0.15 + con_energy * 0.05
            elif direct_hits == 1:
                bite_energy = 1.0 + close_hits * 0.2 + con_energy * 0.05
            elif close_hits >= 2:
                bite_energy = 0.7 + close_hits * 0.1 + con_energy * 0.05
            elif close_hits == 1:
                bite_energy = 0.4 + con_energy * 0.05
            else:
                bite_energy = min(0.3, con_energy * 0.02)

            if bite_energy > 0.08:
                bitten.append({
                    'name': name,
                    'category': branch.category,
                    'refs': refs,
                    'bite_energy': round(bite_energy, 3),
                    'direct_hits': direct_hits,
                    'close_hits': close_hits,
                    'hit_refs': hit_refs,
                    'con_energy': round(con_energy, 3),
                    'constellations': list(sensed_constellations),
                    'desc': branch.description,
                })
                self.bitten_history.append((tick, name, hit_refs))

        bitten.sort(key=lambda x: x['bite_energy'], reverse=True)
        return bitten

    def get_rooted(self, pool: SharedPool) -> dict:
        """根系状态：每个枝条引用的字团及其星座能量"""
        rooted = {}
        for name, branch in self.branches.items():
            ref_status = {}
            for ref_name in branch.refs:
                star = pool.get_star(ref_name)
                if star:
                    ref_status[ref_name] = {
                        'energy': round(star.energy, 2),
                        'state': star.state,
                        'constellation': star.constellation,
                        'con_energy': round(
                            pool.get_constellation_energy(ref_name), 2),
                    }
                else:
                    ref_status[ref_name] = {'state': 'unknown'}
            rooted[name] = ref_status
        return rooted
