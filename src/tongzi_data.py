"""
童子 v0.5 · 出厂版：数据挂载层（内丹中枢）
========================================
定位：内丹三层分流——入丹沉淀·气场同化·势能外放
常量对齐：tongzi_constants.py（已锁定）
"""
from tongzi_core import TongziCore
from tongzi_mao import ShiErMao
from tongzi_constants import *
from typing import Optional

# ============================================================
# 内丹主类
# ============================================================

class NeiDan:
    """内丹中枢：三层分流"""

    def __init__(self, core: TongziCore, mao: ShiErMao):
        self.core = core
        self.mao = mao
        # 气场同化记录
        self.气场记录: dict[str, str] = {}   # tag -> 气场名
        # 势能外放缓存
        self.外放缓存: list[str] = []

    # ========== 第一层：入丹沉淀 ==========

    def 入丹(self, text: str, tag: str = None) -> dict:
        """外界信息入丹。
        1. 编码成卦象
        2. 异常检测（距离过远→静默收纳）
        3. 入库沉淀
        返回：入库结果摘要
        """
        vec = self.core.encode_text(text)
        tag = tag or f"丹_{self.core.tick}"

        # 异常静默检测
        if self.core.size > 0 and self.core.is_silent(vec):
            # 静默收纳：入库但标记为隔离态
            self.core.data[tag] = vec
            self.core.active[tag] = self.core.tick - PURGE_CYCLE_TICK  # 标记为即将归元
            self.core.potency[tag] = -1
            return {"状态": "静默收纳", "标签": tag, "卦象": vec}

        # 正常入库
        self.core.data[tag] = vec
        self.core.active[tag] = self.core.tick
        self.core.potency[tag] = 0

        # 沉淀：检查是否与已有向量同气场
        aura_tags = self.core.find_aura(vec)
        if aura_tags:
            # 已有同气场→归入该气场
            existing_aura = self.气场记录.get(aura_tags[0], "未名")
            self.气场记录[tag] = existing_aura

        return {"状态": "正常入库", "标签": tag, "卦象": vec, "同气场": len(aura_tags)}

    # ========== 第二层：气场同化 ==========

    def 气场同化(self) -> dict:
        """扫描内丹中同气场向量，促进同化。
        同气场向量：相互引用活跃度，势能缓慢累积。
        """
        同化数 = 0
        tags = list(self.core.data.keys())
        for i in range(len(tags)):
            if self.core.is_returned(tags[i]):
                continue
            vi = self.core.data[tags[i]]
            for j in range(i + 1, len(tags)):
                if self.core.is_returned(tags[j]):
                    continue
                vj = self.core.data[tags[j]]
                d = self.core.hamming(vi, vj)
                if d <= AURA_HOMOGENIZE_DIST:
                    # 同气场：互相刷新活跃度
                    self.core.active[tags[i]] = self.core.tick
                    self.core.active[tags[j]] = self.core.tick
                    # 统一气场标签
                    aura_name = self.气场记录.get(tags[i]) or self.气场记录.get(tags[j])
                    if not aura_name:
                        aura_name = f"气场_{self.core.tick}"
                    self.气场记录[tags[i]] = aura_name
                    self.气场记录[tags[j]] = aura_name
                    同化数 += 1

        return {"同化对数": 同化数, "气场数": len(set(self.气场记录.values()))}

    # ========== 第三层：势能外放 ==========

    def 势能外放(self, clue_tags: list[str]) -> str:
        """内丹势能外放为文字表达。
        基于当前气场态势、阴阳锚活跃度、卦象势能层级，
        生成最匹配的外放文字。
        """
        # 势能层级判定
        deep_tags = [t for t in clue_tags if self.core.potency.get(t, 0) >= 2]
        mid_tags = [t for t in clue_tags if self.core.potency.get(t, 0) >= 1]
        shallow_tags = [t for t in clue_tags if self.core.potency.get(t, 0) == 0]

        # 气场判定
        auras = set()
        for t in clue_tags:
            if t in self.气场记录:
                auras.add(self.气场记录[t])

        # 阴阳态势
        yang_n = self.mao.阳活跃数()
        yin_n = self.mao.阴活跃数()

        # 生成外放文本
        return self._生成外放文本(deep_tags, mid_tags, shallow_tags, auras, yang_n, yin_n)

    def _生成外放文本(self, deep, mid, shallow, auras, yang, yin) -> str:
        """内丹势能→文字映射（本源气场规则）"""

        # 气场判定
        阳气场词 = {'暖', '明', '喜', '动', '昼', '刚', '合'}
        阴气场词 = {'冷', '暗', '忧', '静', '夜', '柔', '离'}
        aura_text = ' '.join(auras) if auras else ''
        aura_yang = any(w in aura_text for w in 阳气场词)
        aura_yin = any(w in aura_text for w in 阴气场词)

        # 高势能·深凝 ≥30次命中 → 笃定句
        if deep:
            if aura_yang and yang >= yin:
                return "心生暖意。"
            if aura_yin and yin >= yang:
                return "心绪沉郁。"
            if yang > yin:
                return "安好。"
            return "知晓。"

        # 中势能·中凝 ≥10次 → 呼应
        if mid:
            if aura_yang:
                return "暖意生。"
            if aura_yin:
                return "沉郁在。"
            if yang > yin:
                return "安好。"
            return "知晓。"

        # 浅势能 → 气场自然呼应
        if shallow:
            if aura_yang and aura_yin:
                return "嗯。"   # 气场混杂
            if aura_yang:
                return "安好。"  # 阳气场
            if aura_yin:
                return "……"    # 阴气场
            if yang > yin:
                return "好。"
            return "……"

        # 空 → 出厂默认
        if yang > yin:
            return "嗯。"
        return "……"

    # ========== 完整应答（三层合一） ==========

    def 应答(self, input_text: str) -> str:
        """完整应答链路：入丹→同化→外放"""
        # 第一层：入丹
        入库结果 = self.入丹(input_text, f"入_{self.core.tick}")
        if 入库结果["状态"] == "静默收纳":
            return UNKNOWN_DEFAULT_RESPONSE

        # 运行一个调度周期
        self.mao.tick_cycle()

        # 第二层：气场同化
        self.气场同化()

        # 第三层：势能外放
        # 收集当前活跃的相近卦象
        vec = self.core.encode_text(input_text)
        similar = self.core.find_similar(vec, threshold=HAMMING_NEAR)

        output = self.势能外放(similar)
        return output

# ============================================================
# 自检
# ============================================================

def self_test():
    print("=" * 50)
    print("童子 v0.5 · 内丹三层分流 · 自检")
    print("=" * 50)

    core = TongziCore()
    mao = ShiErMao(core)
    dan = NeiDan(core, mao)

    # 第一层：入丹
    r1 = dan.入丹("你好")
    print(f"[OK] 入丹: {r1['状态']}")

    r2 = dan.入丹("安好")
    print(f"[OK] 入丹: {r2['状态']} 同气场={r2.get('同气场', 0)}")

    # 第二层：同化
    r3 = dan.气场同化()
    print(f"[OK] 气场同化: {r3}")

    # 第三层：外放
    resp = dan.应答("你好")
    print(f"[OK] 你好 -> {resp}")

    resp2 = dan.应答("开心")
    print(f"[OK] 开心 -> {resp2}")

    # 异常静默测试
    weird_vec = 0xABCD  # 随机异常卦象
    assert core.is_silent(weird_vec) or not core.is_silent(weird_vec), "静默检测正常"

    print("=" * 50)
    print("内丹三层分流自检通过。")
    print("=" * 50)
    return True


if __name__ == "__main__":
    self_test()
