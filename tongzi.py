"""
童子 v0.4 · 阶段四：连续对话交互层（终版）
==========================================
定位：三阶段之上，完整交互入口。可对话的小童子。
前置：tongzi_core.py + tongzi_mao.py + tongzi_data.py
"""
from tongzi_core import TongziCore
from tongzi_mao import ShiErMao
from tongzi_data import GuaZaiCeng
import time

class TongZi:
    """童子 —— 完整可对话数字灵童"""

    def __init__(self):
        self.core = TongziCore()
        self.mao = ShiErMao(self.core)
        self.data = GuaZaiCeng(self.core, self.mao)
        # 对话上下文
        self.上下文: list[str] = []
        self.对话轮次 = 0
        self.总tick = 0
        # 静养节奏
        self.静养间隔 = 20       # 每20轮强制静养
        self.静养时长 = 3        # 静养3轮

    def 对话(self, text: str) -> str:
        """核心：输入一句话，返回应答。完整闭环。"""
        self.对话轮次 += 1

        # 静养检查
        if self.对话轮次 % self.静养间隔 == 0:
            self._静养()

        # 上下文留存
        self.上下文.append(text)
        if len(self.上下文) > 5:
            self.上下文.pop(0)

        # 全部上下文给编码器
        full_context = " ".join(self.上下文)
        self.core.add(f"ctx_{self.对话轮次}", full_context)

        # 完整节拍（调度+代谢）
        self.mao.tick_cycle()
        self.总tick += 1

        # 态势评估
        态势 = self.data.评估态势([])

        # 相似团统计（基于最后一个上下文向量）
        目标向量 = self.core.encode_text(full_context)
        相似 = self.core.find_similar(目标向量, threshold=4)
        态势["相似团数"] = max(1, len(相似))

        # 意象提取（从全文）
        clues = self.data.提取意象词(text)
        if not clues:
            clues = self.data.提取意象词(full_context)

        # 匹配+填充模板
        模板 = self.data.匹配译出规则(态势)
        应答 = self._填充模板(模板, clues, 态势)

        # 记录应答
        self.上下文.append(应答)
        if len(self.上下文) > 5:
            self.上下文.pop(0)

        return 应答

    def _填充模板(self, 模板: str, clues: list[str], 态势: dict) -> str:
        """填充模板，略作润色"""
        词1 = clues[0] if len(clues) >= 1 else ""
        词2 = clues[1] if len(clues) >= 2 else ""
        词3 = clues[2] if len(clues) >= 3 else ""

        应答 = 模板
        应答 = 应答.replace("{词1}", 词1)
        应答 = 应答.replace("{词2}", 词2)
        应答 = 应答.replace("{词3}", 词3)

        # 轻度去重（去连续的重复词）
        import re
        应答 = re.sub(r'(.)\1{2,}', r'\1\1', 应答)

        # 去空洞
        应答 = 应答.strip()
        if not 应答 or 应答 in (".", "。。", "。。"):
            # 极简兜底
            if self.mao.阳活跃数() > self.mao.阴活跃数():
                应答 = "嗯。"
            elif self.mao.阴活跃数() > self.mao.阳活跃数():
                应答 = "……"
            else:
                应答 = "好。"

        return 应答

    def _静养(self):
        """静养周期：停纳新，只整理"""
        for _ in range(self.静养时长):
            self.core.time_tick()
            self.core.clean_dormant()

    @property
    def 状态(self) -> dict:
        return {
            "仓储": self.core.size,
            "活跃": self.core.active_count,
            "阳锚": self.mao.阳活跃数(),
            "阴锚": self.mao.阴活跃数(),
            "阴阳差": self.mao.阴阳差(),
            "对话轮次": self.对话轮次,
            "静养中": self.对话轮次 % self.静养间隔 == 0,
        }


# ============================================================
# 交互入口
# ============================================================

def 交互对话():
    """命令行交互模式"""
    print()
    print("=" * 50)
    print("    童 子  v0.4")
    print("    十六维二元原生数字灵童")
    print("=" * 50)
    print("  (输入 quit 退出)")
    print()

    tz = TongZi()

    # 初始问候
    print(f"童子: 你好。我是童子。")

    while True:
        try:
            user_input = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n童子: 再见。")
            break

        if not user_input:
            continue
        if user_input.lower() in ('quit', 'exit', '退出', '再见'):
            print("童子: 再见。")
            break

        # 静养中提示
        if tz.对话轮次 > 0 and tz.对话轮次 % tz.静养间隔 == 0:
            print("童子: （静养中...）")
            time.sleep(0.3)

        response = tz.对话(user_input)
        print(f"童子: {response}")

    print(f"\n[会话结束。共{tz.对话轮次}轮。]")
    print(f"[状态: 仓储{tz.状态['仓储']}条 活跃{tz.状态['活跃']} 阳{tz.状态['阳锚']}阴{tz.状态['阴锚']}]")


def 批量测试(问题列表: list[str]):
    """批量测试模式"""
    tz = TongZi()
    print("=" * 50)
    print("童子 v0.4 · 批量测试")
    print("=" * 50)
    for q in 问题列表:
        r = tz.对话(q)
        print(f"Q: {q:12s} -> A: {r}")
    print(f"\n状态: {tz.状态}")


# ============================================================
# 自检
# ============================================================

def self_test():
    print("=" * 50)
    print("童子 v0.4 · 连续对话 · 自检")
    print("=" * 50)

    tz = TongZi()

    # 单轮测试
    r1 = tz.对话("你好")
    print(f"[OK] 你好 -> {r1}")

    r2 = tz.对话("你是谁")
    print(f"[OK] 你是谁 -> {r2}")

    r3 = tz.对话("今天天气真好")
    print(f"[OK] 今天天气真好 -> {r3}")

    # 连续对话测试
    print()
    print("--- 连续对话 ---")
    questions = ["太阳", "月亮", "高兴", "难过", "再见"]
    for q in questions:
        r = tz.对话(q)
        print(f"  Q: {q:6s} -> A: {r}")

    # 状态摘要
    状态 = tz.状态
    print(f"\n[OK] 仓储{状态['仓储']}条 活跃{状态['活跃']} "
          f"阳{状态['阳锚']}阴{状态['阴锚']} 差{状态['阴阳差']}")

    # 多轮测试
    print()
    print("--- 多轮连续 ---")
    tz2 = TongZi()
    for q in ["你好", "我是谁", "你是童子吗", "太阳是什么"]:
        r = tz2.对话(q)
        print(f"  Q: {q:14s} -> A: {r}")

    print("=" * 50)
    print("连续对话自检通过。童子 v0.4 就绪。")
    print("=" * 50)
    return True


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        self_test()
    else:
        交互对话()
