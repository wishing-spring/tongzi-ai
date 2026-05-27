# -*- coding: utf-8 -*-
"""八字参考码 — 灵犀童子桥的语义底座"""

# 源卦₀/层3 → 2³=8卦 → 一一对应八卦
# 格式: 4位标识符(0000) + 3位展开体 → 取后28位

BAGUA = {
    '乾': {'index': 0, 'ref3': (0,0,0), 'meaning': '天·刚健',  'mood': '坚定', 'act': '直接·主导'},
    '兑': {'index': 1, 'ref3': (0,0,1), 'meaning': '泽·愉悦',  'mood': '开心', 'act': '分享·交流'},
    '离': {'index': 2, 'ref3': (0,1,0), 'meaning': '火·急躁',  'mood': '激动', 'act': '行动·冲突'},
    '震': {'index': 3, 'ref3': (0,1,1), 'meaning': '雷·动荡',  'mood': '不安', 'act': '变化·突破'},
    '巽': {'index': 4, 'ref3': (1,0,0), 'meaning': '风·渗透',  'mood': '柔和', 'act': '适应·迂回'},
    '坎': {'index': 5, 'ref3': (1,0,1), 'meaning': '水·危险',  'mood': '忧惧', 'act': '防御·谨慎'},
    '艮': {'index': 6, 'ref3': (1,1,0), 'meaning': '山·静止',  'mood': '沉稳', 'act': '坚持·不动'},
    '坤': {'index': 7, 'ref3': (1,1,1), 'meaning': '土·包容',  'mood': '平和', 'act': '接纳·滋养'},
}

# 八个28位参考码——全空间展开，Hamming距离决定归属
# 用互质乘法+模运算产8个均匀分布的28位码
REF_28BIT = {
    '乾': 0x0000000,  # 全零
    '兑': 0xFFFFFFF,  # 全壹
    '离': 0x5555555,  # 0101...
    '震': 0xAAAAAAA,  # 1010...
    '巽': 0x3333333,  # 0011...
    '坎': 0xCCCCCCC,  # 1100...
    '艮': 0x6666666,  # 0110...
    '坤': 0x9999999,  # 1001...
}

# 八个卦名列表（按索引）
BAGUA_NAMES = ['乾', '兑', '离', '震', '巽', '坎', '艮', '坤']

if __name__ == '__main__':
    print("八字参考码:")
    for name in BAGUA_NAMES:
        info = BAGUA[name]
        print(f"  {name} 索引{info['index']} 低3位={info['ref3']} "
              f"28bit=0x{REF_28BIT[name]:07X} "
              f"{info['meaning']} · {info['mood']} · {info['act']}")
