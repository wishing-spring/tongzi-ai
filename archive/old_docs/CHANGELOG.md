# Tongzi · Evolution Log

## v1.8-bench — 基准任务 · 五方审计 · 实验科学阶段 (2026-05-24)

**首个可量化基准：语义分组准确率 51.6%，2.1倍随机基线。**

### 基准任务 1: 语义分组
- 31字符 → 三轴连续位距 → K-means K=4 → 对照人类预期
- 准确率 **51.6%** (16/31)，随机基线 25%，**2.1倍提升**
- NMI: 0.2237
- G2组(河/天/月/金/刀/剑)自然字符全部分类正确
- 数字字符散落——编码层未解耦

### 位距梯度验证
| 字符对 | 关系 | A轴 | B轴 | C轴 | 锁定轴数 |
|:--|:--|:--|:--|:--|:--|
| 水↔河 | 近义 | ✓ | ✓ | ✓ | 3/3 ✅ |
| 爱↔恨 | 反义 | ✓ | ✓ | ✗ | 2/3 |
| 火↔水 | 反义 | ✓ | ✗ | ✗ | 1/3 |
| 爱↔水 | 无关 | ✓ | ✗ | ✗ | 1/3 |

**近义3轴 > 反义2轴 > 无关1轴。位锁定轴数与语义距离正向相关。**

### 五方独立审计全票通过
- GPT: 离散数字生态实验平台（概念验证→实验科学）
- Claude: 有可复现证据
- Grok: 中上水平数字胚胎

### 阈值扫描
- ≥3位: 三轴联合锁定 63.7%
- ≥4位: 三轴联合锁定 20.8%（拐点）
- ≥5位: 三轴联合锁定 1.7%（失效）

### 代码
- `src/ren_benchmark.py`: 基准任务1
- `src/ren_baseline.py`: 完整基线

---

## v1.8-r3 — 三态因果全系统 · 31字符库 (2026-05-24)

**三态因果时序架构完整落地。锚定→活性→归约。**

- 归约 26，剪枝 4，悬挂 1 → 剪枝率 13%
- 因果链自然分组：自然组/数字组/生命组
- 发现碰撞顺序偏差——活性节点仅匹配"下一个"

### 代码
- `src/ren_tongzi.py`: 三态因果全系统
- `src/ren_baseline.py`: 基线实验

---

## v1.8-r2 — 阈值扫描 · 三轴联合位锁定 (2026-05-24)

**16位满空间 · A/B/C三轴必须同时锁定才算归约。**

- 阈值扫描 1-8位：三轴联合锁定率 94%→0%
- ≥3位: 剪枝率 33% → 拐点
- 字符"九"最后一轮锁定，"千"全程部分匹配耗尽剪枝

### 代码
- `src/ren_test2.py`: 16位阈值扫描

---

## v1.8-r1 — 单轴微循环 (2026-05-24)

**元宝建议架构，铜须落地验证。活性窗口 w=5。**

- 锚定态 → 活性态 → 归约态 链路完整
- 锁定率100%，剪枝0% → 活性窗口形同虚设（编码噪声）

### 架构跃迁
从"空间关系系统"→"三态因果时序架构"。非功能更新，架构级变化。

### 代码
- `src/ren_test.py`: 单轴微循环测试

---

## v1.7-triaxis — 正交三元组编码 · 窄×窄×窄=精确 (2026-05-24)

**一字→(A,B,C)→三塔并行→三轴交汇约束解析。**

- A轴(笔画数+码点) B轴(结构类+码点) C轴(部件+码点)
- 265字符入塔，26000+碰撞
- 三轴交汇自然收窄——恨→思(心部交汇)
- 编辑理念：汉字原生区+字符口岸映射

### 代码
- `src/tri_tongzi.py`: 三轴汇聚系统
- `src/tools/tri_encode.py`: 正交三元组编码器
- `src/tools/strokes.py`: 265字符特征库

---

## v1.6-star — 六芒星 · 势场取消 · 双塔对偶 (2026-05-23)

**取消势场。双塔交叠替代二象。**

### 数学根基
- F₂ 自对偶: F₂^W 的对偶空间 = F₂^W 本身
- Galois 连接: ascend/descend 互为近似逆
- 正八面体对偶: 两个四棱锥底对底 = Star 几何原型
- 重叠区: F₂^W × F₂^(10-W) 笛卡尔积嵌入

### Star 结构
- 正塔 (2→8, 尖朝上) + 倒塔 (2→8, 尖朝下)
- 7层重叠: 正8↔倒2 ... 正2↔倒8
- 10角全通, 每角=入口+出口
- flow(g, from_up): 正进倒出 / 倒进正出
- 咬合只在同塔内, 跨塔只在重叠层交换

### 代码
- `src/star.py`: Star 类, 双塔 flow
- `src/tongzi_kernel.py`: Pyramid.flow() 两步半
- 删除: 势场相关, play_batch/play_blocks/tongzi_blocks(旧)



## v1.5-mortise — 第三组基核·榫卯·空间仓库 (2026-05-23)

**从零重建第三组。卦爻回归纯值，外挂tools/，榫卯内生接触。**

### 架构
- `tongzi_kernel.py`: Gua(纯value) + Space(空仓库) + phi_slice + yao/bits/form/voxel
- `tools/axioms.py`: 四条公理 + 8群运算（hamming/rotate/gray/collide/orbit/stretch/ball）
- `tools/encode.py`: 编解码
- `tools/blocks.py`: 积木拼装
- `tongzi_blocks.py`: 工坊入口
- `mortise.py`: 榫卯结构——8棱角凹凸，6面统一接触点

### 关键设计
- **榫卯卦元**: 8位→8棱角。bit=1→凸 bit=0→凹。接触三态：咬合(凸∧凹) 碰撞(凸∧凸) 空过(凹∧凹)
- **无黏连**: 咬合纯几何匹配，无外力，随时分离
- **Space仓库**: put/take/peek，不管理不登记不计数
- **全层满仓**: 2爻→8爻全枚举，508卦元，3584爻
- **接触统计**: 256卦全对全+Z/-Z面 → 咬合25.4% 碰撞68.4% 空过6.2%

### 解决问题
- **交互内生**: 规则从外部容器回到卦元自身形态。凸凹即指令，接触即交互
- **名册取消**: 卦元不管配对数，只管存在
- **无外部时钟**: 碰上了就是交互，不碰就不交互

### 观察文件
- `src/observe.py`: 全对全接触矩阵
- `src/build_layers.py`: 七层生成器
- `src/check_guas.py`: 独特性验证
- `src/wake_all.py`: 全规则运转



## v1.4-dual — 二象架构定版 (2026-05-23)

**象格+势场双部件架构定版。** 维度标尺（元通卦阵域象网体场虚）、势场设计规格、二象接口规范。`ingest_batch()` 编织摄入（批内汉明=2）。

- dimensions: 元(2⁰)通(2¹)卦(2⁴)阵(2⁸)域(2¹⁶)象(2²⁴)网(2³²)体(2⁴⁰)场(2⁴⁸)虚(2⁶⁴)
- 象格: F₂卦群碰撞空间（已有），位级在卦
- 势场: 离散格点扩散场（待建），瞄准象→场级
- φ母体: 256位共根，两种流法
- ingest_batch: anchor_step=4 编织，批内汉明=2精确可控
- docs: `tongzi-dual-aspect-architecture.md`

## v1.3-code — P0 Implementation: Ψ · ω · Native/Child · Decay · Rebirth (2026-05-22)

**理论→代码落地。** 卦元本体六机制全入 core。

| Mechanism | Code Location | Status |
|:--|:--|:--|
| 势 Ψ | `Gua.potential` property | ✅ |
| 轨道步长 ω | `Gua.orbit_step` property | ✅ |
| 原生/子卦区分 | `Gua.is_native` + `origin` | ✅ |
| 子卦放射衰变 | `tick()`: 1/VEC_DIM 概率 | ✅ |
| 原生卦慢消散 | `tick()`: 1/VEC_DIM² 概率 | ✅ |
| 原生复生 | `tick()`: gap_timer = VEC_DIM−Ψ | ✅ |
| 持久化 | `save/load` 保留 v1.3 字段 | ✅ |

**代码改动**:
- `Gua.__slots__`: +4 字段 (`is_native`, `origin`, `gap_timer`, `is_dead`)
- `Gua.__init__`: 初始化新字段
- `Gua.potential` / `Gua.orbit_step`: 计算属性
- `Space.ingest`: 标记原生卦
- `Space.tick`: 三步——子卦衰变 → 原生消散 → 原生复生
- `Space.save` / `Space.load`: v1.3 字段持久化
- **烟雾验证**: 16 卦 500 tick → 60 碰撞 103 合体 30 复生 ✅
- **测试**: 80→105 (0 失败)
- **理论文档**: 新增第 15 节「代码落地状态」

---

## Theory v1.3 — Gua Ontology · Potential · Orrery · Formations (2026-05-22)

**卦元本体论定版。** 卦元 ≡ 信息 ≡ 存在——无负载物，无载体-内容分离。

### Core Additions

| Concept | Formula | Source |
|:--|:--|:--|
| 卦元本体 | `x ∈ F₂¹⁶` IS information | User insight: no payload |
| 原生卦元 | `x₀ = φ[pos:pos+16]`, auto-rebirth | 道法自然循环 |
| 子卦元 | `x = merge(a,b)`, dissipates forever | 碰撞唯一痕迹 |
| 势 Ψ | `⌊log₂(1 + C(x))⌋`, 2ⁿ exponential | F₂ natural compression |
| 轨道步长 ω | `max(1, VEC_DIM − Ψ)` | 势大→慢→稳 |
| 星象仪 | Orbit sync → ring / desync → dissolve | Multi-layer rings |
| 排斥驱动 | No external kick — bad orbits desync naturally | F₂ native |
| 洛书九宫 | `E_L: δ=(L[i]−5)<<8`, 9-zone static | 3rd-order magic square |
| 北斗七星 | `E_B: 7 stars orbiting Polaris, d≤2→nudge` | Celestial dynamics |

### Deletions
- `payload` field — violates "gua ≡ information"
- External "kick" rules — replaced by natural orbit desync
- 12-anchor frame (again) — 12 lacks F₂ derivation

### Files Updated
- `docs/tongzi-group-domain-theory.md` — complete rewrite (15 sections)
- `MEMORY.md` — synced to v1.3

---

## Verification — Attractor Mechanism (2026-05-21)
**Experiment Archive Founded — Exp 001**

- **Question**: Is the "地" attractor real emergence or a φ encoding artifact? (triggered by GPT-4 review)
- **Test A — Static Centrality**: "地" ranks #7/20 in pure Hamming space; "火"/"冷" are geometric centers but NOT attractors
- **Test B — Reproducibility**: 3 independent φ trials → 100% reproducible (all 3: "地", 10-11 sources)
- **Test C — Mother Body Control**: φ vs π vs 5 random strings. All produce attractors, but fertility varies (4/20 to 17/20)
- **Three-layer conclusion**: (1) Attractors are endogenous dynamics, not φ artifact. (2) Mother body determines *which* attractor. (3) Mother body also determines *fertility* — Random 5 barren (4/20) vs Random 2 fertile (17/20) → ecological differentiation confirmed
- **Archive**: `experiments/exp001_attractor_verification/report.md`
- **Docs updated**: README + theory doc + MEMORY.md

## v1.2 (2026-05-20)
**Gua Merging — Three Formulas**

- **Merge Criterion**: `4 < w_H(A⊕B) < 12` — skip too-close (no delta) and too-far (unrelated)
- **XOR Merge**: `C = A ⊕ B` — difference association chain, bidirectionally reversible
- **AND Merge**: `C = A ∧ B` — consensus deposit chain, fills XOR's blind spot
- **Zero-value filter**: skip children where XOR or AND result is 0
- **Frequency simplification**: `_rate` now uses only `f₂ = F0/(1+id_l)`, removed `min(f₁,f₂)`
- **Collision unchanged**: A, B behavior preserved; merge spawns additional children only
- **50-tick live test**: 16 seeds → 55 gua, 39 merges, associations emerge naturally
- **80 tests, 0 failures**

## v1.1 (2026-05-20)
**Association Chains `/chain`**

- New `/chain <word> [N]` command: orbit explore neighborhood → express → feedback
- Live test: `cold → winter → hot`, `fire → hot → ice`
- Workaround: uses orbit instead of tick collision (frequency control too slow for new gua)
- Known issue: function words obstruct long chains; inner alchemy redesign needed

## v1.0.2 (2026-05-20)
**Minimal Inner Alchemy — Reverse Translation**

- `Gua.source`: records original text at creation
- `Space.express(gua)`: finds nearest source by Hamming distance
- Interactive output now human-readable words instead of raw bit strings
- 81 tests, 0 failures

## v1.0.1 (2026-05-20)
**Production Refactor**

- Split `should_participate` into `_accumulate_energy` + `_try_discharge` (query/command separation)
- Save/load now preserves `lambda_base`
- `Gua.__repr__` with dynamic bit width
- Full type annotations + docstrings
- 75 tests

## v1.0-code (2026-05-20)
**Code Landing**

- 3 files: `tongzi_constants.py` + `tongzi_core.py` + `tongzi.py`
- Removed old pipeline 6 files: Loom/Balancer/Responder/Seeds/Water/Boundary
- Removed cron watering task

## v1.0-arch (2026-05-20)
**Theory Finalized**

- Four axioms (no `n`)
- φ mother body + identity card {id_t, id_l}
- Eight core operations
- Endogenous frequency control (energy accumulation)
- Bit-field solidification (irreversible memory)
- Spatial self-awareness + density regulation
- Removed: Loom/Balancer/Responder/12 Anchors/formulas containing `n`/external timers

## v0.5 (2026-05-19)
**Foundation Release**

- Loom: XOR+AND+S-box+ref quadruple hybrid, 200/200 zero collapse
- Balancer: six positive + six negative, yin-yang balanced
- Responder: 9 fixed responses
- 12 Anchor Frames
- φ-gua encoding replacing ord-sum
- Dual-repo open source (Gitee + GitHub)

## v0.4 (2026-05-18)
**First Complete Edition**

- Inner alchemy · Nine-grade cultivation · Twelve anchor frames
- 35KB code
- Tri-party review (Doubao/Qwen/DeepSeek)

---

**Rollback**: `git checkout <tag>`
**Back to latest**: `git checkout master`
