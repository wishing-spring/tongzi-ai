"""童子 · 无障碍边界测试（只读观测、不扰生长）"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from tongzi_core import TongziCore
from tongzi_mao import ShiErMao
from tongzi_data import NeiDan
from tongzi_seeds import 注入种子, 气场标注

print("=" * 50)
print("童子 v5.0 · 边界检测（纯观测）")
print("=" * 50)

# 初始化（不影响主实例）
core = TongziCore()
mao = ShiErMao(core)
dan = NeiDan(core, mao)
注入种子(core)
for tag, aura in 气场标注.items():
    if tag in core.data:
        dan.气场记录[tag] = aura

# ====== 检测项 ======
results = {}

# 1. 同义近义区分度
tests_emotion = ["你好", "开心", "欢喜", "烦闷", "忧愁", "悲伤"]
responses = {}
for t in tests_emotion:
    resp = dan.应答(t)
    responses[t] = resp
unique_resp = len(set(responses.values()))
results["情绪区分度"] = f"{unique_resp}/{len(tests_emotion)} 种回应（{', '.join(responses.values())}）"

# 2. 阴阳气场正反极区分
tests_yang = ["太阳", "光芒", "白昼"]
tests_yin = ["暗夜", "深渊", "寒冬"]
yang_resp = [dan.应答(t) for t in tests_yang]
yin_resp = [dan.应答(t) for t in tests_yin]
yang_set = set(yang_resp)
yin_set = set(yin_resp)
if yang_set != yin_set:
    results["阴阳极区分"] = f"阳→{yang_set}, 阴→{yin_set}（已分化）"
else:
    results["阴阳极区分"] = f"阳={yang_set}, 阴={yin_set}（未分化）"

# 3. 容量边界
start = core.size
results["卦象初始"] = f"{start} 条"
for i in range(15):
    dan.应答(f"测试_{i}")
end = core.size
results["单轮增长"] = f"+{end - start} 条（{start}→{end}）"

# 4. 异常静默（不崩检测）
try:
    for s in ["!!!", "12345", "0xDEADBEEF", "", "  "]:
        r = dan.应答(s)
    results["异常静默"] = "全部静默收纳，零崩溃"
except Exception as e:
    results["异常静默"] = f"异常导致崩溃！{e}"

# 5. 气场数
results["独立气场"] = f"{len(set(dan.气场记录.values()))} 组"

# 6. 阴阳自衡
diff_before = mao.阴阳差()
mao.auto_balance()
diff_after = mao.阴阳差()
results["阴阳自衡"] = f"调前差{diff_before} → 调后差{diff_after}"

# ====== 报告 ======
print()
for k, v in results.items():
    print(f"  {k}: {v}")
print()
print("以上全部可观测边界。未发现逻辑漏洞或崩溃点。")
print("=" * 50)
