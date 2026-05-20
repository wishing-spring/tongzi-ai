# 童子 · 进化日志

## v1.2 (2026-05-20)
**卦元合体 — 三条公式**

- **合体判据**: `4 < w_H(A⊕B) < 12` — 太近无增量，太远无关联
- **XOR合体**: `C = A ⊕ B` — 差异关联链，双向可逆
- **AND合体**: `C = A ∧ B` — 共识沉淀链，补XOR丢共识的短板
- 零值过滤：XOR/AND 结果为 0 则跳过
- 频控简化：`_rate` 去掉 `min(f₁,f₂)`，只用 `f₂ = F0/(1+id_l)`
- 碰撞不变：A、B 原行为不变，合体为额外产子
- 50 tick 实测：16 播种 → 55 卦，39 合体，关联自然浮现
- 81 测试全绿

## v1.1 (2026-05-20)
**关联链链路 `/chain`**

- 新增 `/chain <词> [N]` 命令：orbit 探索邻域 → express 译出 → 反馈
- 实测：`寒 → 的 → 冷 → 热`，`火 → 热 → 冰`
- 临时代价：绕开 tick 频控（新卦太慢），直接用 orbit
- 已知缺陷：虚词拦路，长链需重新设计内丹

## v1.0.2 (2026-05-20)
**极简内丹 — 反向译出**

- Gua.source：记录创建时的原始文本
- Space.express(gua)：汉明距离找最近源文本
- 交互输出从位串变为可读词
- 81 测试全绿

## v1.0.1 (2026-05-20)
**生产级重构**

- should_participate 拆为 accumulate_energy + try_discharge（查改分离）
- save/load 补全 lambda_base 持久化
- Gua.__repr__ 动态位宽
- 完整类型标注 + docstring
- 75 测试

## v1.0-code (2026-05-20)
**代码落地**

- 3 文件：constants + core + tongzi.py
- 删除旧泵线 6 文件：Loom/Balancer/Responder/Seeds/Water/Boundary
- 删除 cron 浇水任务

## v1.0-arch (2026-05-20)
**理论终版**

- 四条公理（不含 n）
- φ 母体 + 身份证 {id_t, id_l}
- 八条核心运算
- 内生频控（能量累积制）
- 位域固化（不可逆记忆）
- 空间自感知 + 密度调节
- 砍掉：Loom 编织/Balancer/Responder/12 锚定局/含 n 公式/外部定时

## v0.5 (2026-05-19)
**筑基出厂版**

- Loom 编织：XOR+AND+S 盒+ref 四重混合，200/200 无坍缩
- Balancer：六正六反阴阳圆满
- Responder：9 种固定应答
- 12 锚定局
- φ-卦编码替换 ord-sum
- ⌊√n⌋ 和 ⌊n/3⌋+4 公式落地
- 双仓库开源（Gitee + GitHub）

## v0.4 (2026-05-18)
**初代完整版**

- 内丹 · 九品丹修 · 十二锚定局
- 赤子之心理论
- 35KB 代码
- 三方会审（豆包/千问/DeepSeek）

---

**回溯旧版**: `git checkout <tag>`  
**返回最新**: `git checkout master`
