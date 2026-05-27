# -*- coding: utf-8 -*-
"""三界天庭管理系统 — 天界七官·地界三司 · 零浮点"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from dataclasses import dataclass


@dataclass
class Decree:
    """调度指令"""
    target: str
    action: str
    value: any = None
    reason: str = ""
    tick: int = 0


class TianTing:
    """三界天庭管理: 天界七官·地界三司"""

    def __init__(self):
        self.tick = 0
        self.tongzi = None
        self.lingxi = None

        # ── 天界七官 ──
        # 玉帝·总管 Jade Emperor / Overseer
        self.alert_level = 0            # 0=正常 1=关注 2=警戒 3=危机
        self.decrees: list[Decree] = []

        # 王母·生息 Queen Mother / Vitality
        self.life_quota = 32
        self.ripen_rate = 1.0
        self.harvest_cycle = 100

        # 太上·观察 Laojun / Observer
        self.observe_log: list[str] = []

        # 雷部·应急 Thunder / Emergency
        self.emergency_count = 0
        self.emergency_cd = 0

        # 紫微·轨迹 Ziwei / Trajectory
        self.track_path: list[str] = []

        # 太岁·节律 Taisui / Rhythm
        self.season = 0
        self.season_ticks = 0

        # 财部·调度 Wealth / Dispatch
        self.surge_budget = 4096
        self.eco_budget = 1024

        # ── 地界三司 ──
        # 阎罗·裁断 Yama / Verdict
        self.death_list: list[int] = []

        # 孟婆·清理 Mengpo / Cleanup
        self.ghost_cleaned = False

    def bind(self, tongzi, lingxi):
        self.tongzi = tongzi
        self.lingxi = lingxi

    # ════════════════════════════════
    #  玉帝·总管 Jade Emperor / Overseer
    # ════════════════════════════════

    def oversee(self) -> int:
        """收集各层指标 → 定警戒等级"""
        if not self.lingxi or not self.tongzi:
            return 0

        lx = self.lingxi
        alerts = 0

        if lx.l1.coherence() > 0.8:
            alerts += 1
        total = len(lx.l2.pool)
        if total > 0 and lx.l2.active_count() / total < 0.1:
            alerts += 1
        if lx.phi.size() > 300:
            alerts += 1
        if lx.yj.trigger_count >= 5:
            alerts += 1

        self.alert_level = min(3, alerts)
        return self.alert_level

    def issue_decrees(self) -> list[Decree]:
        """根据警戒等级发布指令"""
        decrees = []
        level = self.alert_level

        if level >= 3:
            decrees.append(Decree('surge', 'shrink', 0.5, '危机收缩', self.tick))
            decrees.append(Decree('eco', 'purge', 0.3, '清除三成', self.tick))
            decrees.append(Decree('yj', 'force_quench', None, '强制骤冷', self.tick))
        elif level >= 2:
            decrees.append(Decree('surge', 'shrink', 0.7, '警戒收缩', self.tick))
            decrees.append(Decree('phi', 'prune', 0.5, '剪除弱连接', self.tick))
        elif level >= 1:
            decrees.append(Decree('eco', 'slow_grow', None, '减缓增长', self.tick))

        self.decrees = decrees
        return decrees

    # ════════════════════════════════
    #  王母·生息 Queen Mother / Vitality
    # ════════════════════════════════

    def vitality_manage(self):
        """生态池生命周期调节"""
        if not self.tongzi:
            return

        for pool in self.tongzi.eco:
            size = len(pool)
            solid = sum(1 for d in pool.values() if d['solid'])
            if size > 0 and solid / size < 0.3:
                self.ripen_rate = 2.0
            elif size > 0 and solid / size > 0.9:
                self.ripen_rate = 0.8

        if self.tick % self.harvest_cycle == 0:
            self._harvest()

    def _harvest(self):
        """蟠桃会·收割: 淘汰最不活跃的未固化卦元"""
        if not self.tongzi:
            return
        for pool in self.tongzi.eco:
            unsolid = [(g, d['hits']) for g, d in pool.items() if not d['solid']]
            if len(unsolid) > self.life_quota:
                unsolid.sort(key=lambda x: x[1])
                remove = unsolid[:len(unsolid) // 4]
                for g, _ in remove:
                    del pool[g]

    # ════════════════════════════════
    #  太上·观察 Laojun / Observer
    # ════════════════════════════════

    def observe(self):
        """定期采样系统状态"""
        if self.tick % 50 != 0 or not self.lingxi:
            return

        lx = self.lingxi
        entry = (
            f"t{self.tick}: L1={lx.l1.bias()}({lx.l1.coherence():.2f}) "
            f"L2={lx.l2.active_count()}活 "
            f"Φ={lx.phi.size()}连 "
            f"L3={lx.l3.current_hex_name()}"
        )
        self.observe_log.append(entry)
        if len(self.observe_log) > 100:
            self.observe_log = self.observe_log[-100:]

    def observe_last(self, n: int = 3) -> list[str]:
        return self.observe_log[-n:] if self.observe_log else []

    # ════════════════════════════════
    #  雷部·应急 Thunder / Emergency
    # ════════════════════════════════

    def emergency_check(self):
        """异常检测: 必要时强制介入"""
        if self.emergency_cd > 0:
            self.emergency_cd -= 1
            return

        if not self.lingxi:
            return

        yj = self.lingxi.yj
        if yj.trigger_count >= 5:
            yj._quench(self.lingxi.l2.pool)
            self.emergency_count += 1
            self.emergency_cd = 50
            return

        if self.lingxi.phi.size() > 500:
            self._prune_phi()
            self.emergency_cd = 30

    def _prune_phi(self):
        """剪除Φ场弱连接"""
        phi = self.lingxi.phi
        weak = [(k, w) for k, w in phi.connections.items() if w <= 2]
        for k, _ in weak:
            del phi.connections[k]
            phi._last_active.pop(k, None)

    # ════════════════════════════════
    #  紫微·轨迹 Ziwei / Trajectory
    # ════════════════════════════════

    def track_hexagram(self):
        """记录八卦跃迁轨迹"""
        if not self.lingxi:
            return
        name = self.lingxi.l3.current_hex_name()
        if not self.track_path or self.track_path[-1] != name:
            self.track_path.append(name)
            if len(self.track_path) > 64:
                self.track_path = self.track_path[-64:]

    def track_recent(self, n: int = 5) -> str:
        return ' → '.join(self.track_path[-n:]) if self.track_path else '-'

    # ════════════════════════════════
    #  太岁·节律 Taisui / Rhythm
    # ════════════════════════════════

    def rhythm_cycle(self):
        """季节轮转 春生夏长秋收冬藏 (每250tick换季)"""
        self.season_ticks += 1
        if self.season_ticks >= 250:
            self.season = (self.season + 1) % 4
            self.season_ticks = 0

        configs = {
            0: {'diffuse': 32, 'dream': 60, 'noise': 4},
            1: {'diffuse': 48, 'dream': 40, 'noise': 6},
            2: {'diffuse': 24, 'dream': 80, 'noise': 2},
            3: {'diffuse': 16, 'dream': 50, 'noise': 8},
        }
        self.season_config = configs[self.season]

    @property
    def season_name(self) -> str:
        return ['春生', '夏长', '秋收', '冬藏'][self.season]

    # ════════════════════════════════
    #  财部·调度 Wealth / Dispatch
    # ════════════════════════════════

    def resource_manage(self):
        """根据负载自动调节资源配额"""
        if not self.tongzi:
            return

        usage = len(self.tongzi.surge) / max(1, self.tongzi.surge_cap)
        if usage > 0.95:
            self.surge_budget = min(8192, int(self.tongzi.surge_cap * 1.2))
        elif usage < 0.5:
            self.surge_budget = max(2048, int(self.tongzi.surge_cap * 0.8))
        if usage > 0.98:
            self.tongzi.surge_cap = self.surge_budget

    # ════════════════════════════════
    #  地界三司
    # ════════════════════════════════

    def verdict(self):
        """阎罗·裁断 Yama / Verdict: 评估卦元生死"""
        if not self.tongzi or self.tick < 50:
            return
        self.death_list = []
        for pool in self.tongzi.eco:
            for g, d in list(pool.items()):
                if d['hits'] == 0 and not d['solid']:
                    self.death_list.append(g)

    def reclaim(self) -> int:
        """无常·回收 Wuchang / Reclaim: 执行卦元删除"""
        if not self.death_list:
            return 0
        executed = 0
        for g in self.death_list[:50]:
            for pool in self.tongzi.eco:
                if g in pool and not pool[g]['solid']:
                    del pool[g]
                    executed += 1
                    break
        self.death_list = []
        return executed

    def cleanup(self):
        """孟婆·清理 Mengpo / Cleanup: 定期清空ghost"""
        if not self.lingxi or self.tick % 200 != 0:
            self.ghost_cleaned = False
            return False
        self.lingxi.packet.ghost = 0
        self.lingxi.packet.ctx = 0
        self.ghost_cleaned = True
        return True

    # ════════════════════════════════
    #  总控帧
    # ════════════════════════════════

    def tick_once(self) -> dict:
        """天庭一帧: 天界巡查 → 地界回收"""
        self.tick += 1

        self.oversee()
        decrees = self.issue_decrees()
        self.vitality_manage()
        self.observe()
        self.emergency_check()
        self.track_hexagram()
        self.rhythm_cycle()
        self.resource_manage()

        self.verdict()
        executed = self.reclaim()
        forgot = self.cleanup()

        return {
            'tick': self.tick,
            'alert': self.alert_level,
            'season': self.season_name,
            'decrees': len(decrees),
            'executed': executed,
            'forgot': forgot,
            'track': self.track_recent(),
        }

    def full_report(self) -> str:
        """天庭全览"""
        lines = [
            f"═══ 三界天庭 t={self.tick} ═══",
            f"太岁·节律: {self.season_name}({self.season_ticks}/250)",
            f"玉帝·总管: 警戒{self.alert_level} | 指令{len(self.decrees)}条",
            f"王母·生息: 配额{self.life_quota} 熟速{self.ripen_rate}",
            f"雷部·应急: 介入{self.emergency_count}次",
            f"紫微·轨迹: {self.track_recent()}",
            f"财部·调度: 涌{self.surge_budget} 生{self.eco_budget}",
            f"阎罗·裁断: 待回收{len(self.death_list)}",
            f"孟婆·清理: {'已执行' if self.ghost_cleaned else '-'}",
            f"─── 太上·丹录(末3) ───",
        ]
        for entry in self.observe_log[-3:]:
            lines.append(f"  {entry}")
        if not self.observe_log:
            lines.append("  (空)")
        return "\n".join(lines)


if __name__ == '__main__':
    from tongzi_f2 import TongziPool
    from lingxi_fusion import LingxiFusion

    tt = TianTing()
    tz = TongziPool(surge_cap=4096, eco_cap=1024)
    lx = LingxiFusion(l1_capacity=128, l2_capacity=1024)
    tt.bind(tz, lx)

    print("三界天庭就绪\n")
    for i in range(10):
        chain = tz.encode("天地玄黄") if i < 3 else []
        attr = tz.tick_once(inject_guas=chain if chain else None)
        lx.receive(attr, text="天地玄黄" if i < 3 else "")
        st = tt.tick_once()
        print(f"t{i+1}: 警戒{st['alert']} {st['season']} "
              f"指令{st['decrees']} 回收{st['executed']} 清理{st['forgot']}")

    print("\n" + tt.full_report())
