# -*- coding: utf-8 -*-
"""chat.py — 童灵全链路对话 · 零浮点F₂管道"""
import os, sys, time
sys.path.insert(0, os.path.dirname(__file__))

from tongzi_f2 import TongziPool
from lingxi_fusion import LingxiFusion
from word_world import WordWorld
from tian_tian import TianTing


class TongLingChat:
    """童灵对话: 童子F₂碰撞 → attractor → 灵犀五层 → 词世界输出"""

    def __init__(self):
        self.tongzi = TongziPool(surge_cap=4096, eco_cap=1024)
        self.lingxi = LingxiFusion(l1_capacity=128, l2_capacity=1024)
        self.words = WordWorld()
        self.tianting = TianTing()
        self.tianting.bind(self.tongzi, self.lingxi)
        self.history: list[dict] = []
        self.total_ticks = 0
        print("童灵v6.1 — 卦元统一 · 五层全通 · 三界天庭 · 零浮点")
        print(f"词世界: {len(self.words.word_hashes)}词 | "
              f"童子池: {self.tongzi.surge_cap}涌 {self.tongzi.eco_cap}×4生态")
        print(f"灵犀: L1阴阳 L2世界 Φ脉络 L3八卦 定心 YongJiu")
        print(f"天庭: 玉帝·总管 王母·生息 太上·观察 雷部·应急 紫微·轨迹 太岁·节律 财部·调度")
        print(f"地界: 阎罗·裁断 无常·回收 孟婆·清理")
        print("输入'退出'结束 | '状态'看系统 | '天庭'看管理 | '长跑N'稳定性测试\n")

    def process(self, text: str) -> str:
        """处理一行输入 → 返回输出"""
        t0 = time.time()

        chain = self.tongzi.encode(text)
        attractor = 0
        for i in range(3):
            attr = self.tongzi.tick_once(inject_guas=chain if i == 0 else None)
            self.total_ticks += 1
            if i == 2:
                attractor = attr

        lx_state = self.lingxi.receive(attractor, text=text)
        tt_state = self.tianting.tick_once()

        active_guas = self.lingxi.l2.get_active_guas()[:8]
        output = self.words.speak(attractor, active_guas)

        elapsed = time.time() - t0
        entry = {
            'text': text[:30],
            'attractor': hex(attractor),
            'output': output,
            'lx': lx_state,
            'tt': tt_state,
            'elapsed_ms': int(elapsed * 1000),
        }
        self.history.append(entry)
        return output

    def report(self) -> str:
        """系统状态报告"""
        lx = self.lingxi
        tz = self.tongzi
        s = lx.history[-1] if lx.history else {}
        eco = [len(p) for p in tz.eco]
        solid = [sum(1 for d in p.values() if d['solid']) for p in tz.eco]

        return (
            f"\n═══ 系统状态 t={self.total_ticks} ═══\n"
            f"童子: 涌{len(tz.surge)}卦 eco={eco} 固={solid}\n"
            f"       attractor=0x{tz.attractor:07X}\n"
            f"灵犀: L1={lx.l1.bias()}({lx.l1.coherence():.2f}) "
            f"L2:活{s.get('l2_active','?')}流{s.get('l2_flowing','?')}眠{s.get('l2_dormant','?')}"
            f"{' 💤' if s.get('l2_dreaming') else ''}\n"
            f"       Φ:{s.get('phi_size','?')}连 "
            f"L3:{s.get('l3_hex','?')}({s.get('l3_trigram','?')}) "
            f"定心:{s.get('dxz_level','?')}\n"
            f"       YJ:分岔{s.get('yj_split','?')} L={s.get('yj_L',0):.2f}"
            f"{' 🔥' if s.get('yj_triggered') else ''}"
            f"{' ❄️' if s.get('yj_quench') else ''}"
        )

    def long_run(self, n_ticks: int):
        """长时间稳定性测试"""
        import random
        test_texts = [
            "你好", "天地玄黄", "宇宙洪荒", "日月盈昃", "辰宿列张",
            "寒来暑往", "秋收冬藏", "云腾致雨", "露结为霜",
        ]
        print(f"\n长跑 {n_ticks} tick...")
        results = []
        for i in range(n_ticks):
            if i % 10 == 0:
                text = random.choice(test_texts)
            else:
                text = ""
            chain = self.tongzi.encode(text) if text else []
            attr = self.tongzi.tick_once(inject_guas=chain if chain else None)
            lx_state = self.lingxi.receive(attr, text=text)
            self.tianting.tick_once()
            self.total_ticks += 1

            if (i + 1) % 200 == 0:
                s = self.lingxi.history[-1]
                eco = [len(p) for p in self.tongzi.eco]
                results.append(
                    f"  t{i+1:4d}: 涌{len(self.tongzi.surge)} eco={eco} "
                    f"Φ:{s.get('phi_size',0)} L3:{s.get('l3_hex','?')} "
                    f"YJ:s={s.get('yj_split',0)} L={s.get('yj_L',0):.2f} "
                    f"管:{self.tianting.alert_level}警 {self.tianting.season_name}"
                )

        print("\n".join(results))
        yj_trig = sum(1 for h in self.lingxi.history if h.get('yj_triggered'))
        yj_quench = sum(1 for h in self.lingxi.history if h.get('yj_quench'))
        print(f"\n长跑完成: {n_ticks}tick | YJ触发:{yj_trig} 骤冷:{yj_quench} "
              f"| 应急:{self.tianting.emergency_count} | {self.tianting.season_name}")


def main():
    chat = TongLingChat()

    while True:
        try:
            user = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见。")
            break

        if not user:
            continue

        if user == '退出':
            break
        elif user == '状态':
            print(chat.report())
        elif user == '天庭':
            print(chat.tianting.full_report())
        elif user.startswith('长跑'):
            try:
                n = int(user.split('长跑')[1].strip()) if len(user) > 2 else 1000
            except:
                n = 1000
            chat.long_run(n)
        else:
            output = chat.process(user)
            print(f"\n童灵: {output}")


if __name__ == '__main__':
    main()
