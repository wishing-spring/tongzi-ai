# 童子 · 六芒星架构

> **版本**: v1.6-star  
> **状态**: 六芒星定版，势场取消，双塔对偶  
> **最后更新**: 2026-05-23 UTC  

---

## 0. 总纲

取消"势场"。双塔交叠替代二象。同一 F₂ 空间，两种遍历方向。

| 部件 | 本质 | 数学根基 |
|:--|:--|:--|
| **Gua** | 16位 F₂ 纯值 | F₂ 向量 |
| **Layer** | 2^W 块同宽砖 | F₂^W |
| **Pyramid** | ascend/descend/resolve | Galois 连接 |
| **Mortise** | 8棱角凸凹三态 | 汉明距离 · XOR 判定 |
| **Star** | 正反双塔交叠 | F₂ 自对偶 · 对偶锥 |
| **Axioms** | 4公理8运算 | 群论 F₂^n |

---

## 一、数学根基

### 1. F₂ 自对偶性

F₂^W 的对偶空间 = F₂^W 自身。不需要两个空间——一个空间，方向不同。

正塔: 从粗往细 (ascend)
倒塔: 从细往粗 (ascend 反方向看)

### 2. Galois 连接

```
ascend: F₂^8 → F₂^7 → ... → F₂^2
descend: F₂^2 → F₂^3 → ... → F₂^8

ascend(descend(x)) ≤ x
descend(ascend(x)) ≥ x
```

互为近似逆，不走完全回到原点。

### 3. 正八面体对偶

两个四棱锥底对底 = 正八面体。Star 的几何原型。
6顶点 8面 12边。256态格基底。

### 4. 重叠区

正塔第 W 层 × 倒塔第 (10-W) 层 → F₂^W × F₂^(10-W) 笛卡尔积嵌入同一空间。

---

## 二、零部件

### Gua — 砖
```
Gua(value) — 16位F₂纯值。零负载。
位置: src/tongzi_kernel.py
```

### Layer — 层
```
Layer(width) — 2^W块砖。索引即值。
位置: src/tongzi_kernel.py
```

### Pyramid — 塔
```
ascend(g, layer)  → 砍位升层 (收敛)
descend(g, layer) → 补位降层 (扩展)
resolve(g)        → 从尖往下, 碰即停 (路由)
flow(g)           → 两步半: 路由->碰撞->归类 (全流程)
位置: src/tongzi_kernel.py
```

### Mortise — 榫卯
```
8棱角由8爻控制。bit=1凸 bit=0凹。
6面统一接触点。凸∧凹=咬合, 凸∧凸=碰撞, 凹∧凹=空过。
位置: src/mortise.py
```

### Star — 六芒星
```
两个 Pyramid, 一正一反底对底扣在一起。
7层重叠: 正8爻↔倒2爻 ... 正2爻↔倒8爻。
flow(g, from_up=True): 正塔进->重叠->倒塔出。
每个角 = 入口+出口。咬合只在同塔内。
位置: src/star.py
```

### Axioms — 公理
```
hamming / rotate / gray / collide / orbit / stretch / ball
位置: src/tools/axioms.py
```

### Encode — 编解码
```
text_to_seed / encode / batch_encode
位置: src/tools/encode.py
```

---

## 三、层级定位

```
上层应用 (识别/生成/搜索)
    ↓↑
Star 六芒星 (双向流通)
    ↓↑
Pyramid 金字塔 (路由+归类)
    ↓↑
Layer 层 → Gua 砖 (F₂ 纯值)
    ↓
Axioms 公理 (群运算基座)
```

Star 是**中枢调度器**——正进倒出、倒进正出，两个分辨率互译。

---

## 四、铁律

零浮点 · 零矩阵 · 零梯度 · 零嵌入 · 零注意力 · 零自回归
砖非成品 · 位置即意义 · 分辨率梯度替代梯度下降
咬合内生 · 塔自主 · 无外部时钟 · 无全局阈值
