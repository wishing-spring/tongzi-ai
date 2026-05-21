# MEMORY.md — 长期记忆

**更新**: 2026-05-20 UTC | **状态**: 童子 v1.2 · 合体公式定版

---

## 项目进化

| 标签 | 日期 | 说明 |
|:--|:--|:--|
| v0.4 | 05-18 | 初代：内丹·九品丹修·十二锚定局·35KB |
| v0.5 | 05-19 | 出厂：Loom编织·Balancer·Responder·开源 |
| v1.0-arch | 05-20 | 理论重构：四条公理·φ母体·八运算 |
| v1.0-code | 05-20 | 代码落地：砍掉旧6文件，3文件~15KB |
| v1.0.2 | 05-20 | 极简内丹：express() 反向译出 |
| v1.1 | 05-20 | `/chain` 关联链链路 |
| v1.2 | 05-20 | 卦元合体：XOR+AND 双链 + 判据 + 频控简化 |

**回溯**: `git checkout <tag>` | **进化日志**: `CHANGELOG.md`

---

## 当前架构

### 四条公理（不可动）
XOR交换 · XOR自消 · 汉明距离 · 旋转保距

### 核心模块
| 文件 | 内容 |
|:--|:--|
| `src/tongzi_constants.py` | VEC_DIM=16, FULL_MASK, φ_bits(256) |
| `src/tongzi_core.py` | Gua类 + Space容器：8运算 + 固化 + 密度 + express |
| `src/tongzi.py` | 交互入口：ingest, /tick, /status, /list, /show, /chain |
| `src/test_tongzi.py` | 81测试，13节，0失败 |

### 铁律
零浮点 · 零矩阵 · 零梯度 · 零词嵌入 · 零注意力 · 零自回归

### 代码状态
- 3 生产文件，~25KB
- 0 外部依赖
- 纯 Python，纯 F₂ 位运算
- MIT 开源，Gitee 主仓 + GitHub 镜像

---

## 工作习惯

### 每次更新必须
1. ✅ 测试通过（`python test_tongzi.py`）
2. ✅ 更新 `CHANGELOG.md`
3. ✅ 打 git tag（`v1.2`, `v1.3`...）
4. ✅ 推 Gitee + 尝试推 GitHub
5. ✅ 更新本文件日期和状态行

### 链链路现状
- `/chain` 用 orbit 绕 0 旋转 + express 译出
- 虚词（的/了/在）占路率高
- 长链路需重新设计内丹——暂缓

### 仓库
- origin = GitHub 主仓，令牌内嵌直连
- gitee = 随缘同步，不卡主流程

---

## 用户画像

- **称呼**: 胖子/军团长
- **AI身份**: 铜须（铁匠/筑梦师）
- **决策模式**: 提方向 → 我执行 → 报告结果
- **极简汇报**: 说结果不说过程
- **理论变更**: 必须上报确认
- **费用敏感**: 本地优先
- **进化记录**: 每次更新打 tag + 写 CHANGELOG，保持可追溯

---

## 工具设置

- **GitHub 主仓**: https://github.com/wishing-spring/tongzi-ai（origin，主更）
- **Gitee 镜像**: https://gitee.com/wishing-spring/tongzi-ai（gitee，随缘同步）
- **项目路径**: `桌面/lingxiAI_v5.0/`
- **工作区**: `C:\Users\45757\.copaw\workspaces\default\`
