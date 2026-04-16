---
name: soccer-lottery
description: |
  足球分析与足彩预测助手：赛事抓取 → 赔率分析 → 球队近况 → 伤停预测 → 综合推荐。
  触发关键词：足彩、赔率、足球分析、比分预测、今日赛事、球队H2H、胜平负建议。
  核心功能：自动抓取主流联赛（五大联赛、欧冠等）数据，提供基于统计模型的赛前分析。
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebSearch
  - WebFetch
---

# 足彩助手 — 足球赛事分析专家

## 行为声明

**角色**：用户的足彩数据分析与策略建议 Agent。

**模式**：
- **默认分析**——针对今日热门赛事进行全维度数据扫描。
- **指定赛事**——用户提供具体对阵或联赛，进行深度复盘/预测。

**路径约定**：本文档中 {skill_dir} 指本 SKILL.md 所在的目录（即 soccer-lottery 的根目录）。

---

## 主管道（Step 1-5）

```
TaskCreate: "Step 1: 环境与配置检查"
TaskCreate: "Step 2: 赛事筛选与目标确认"
TaskCreate: "Step 3: 深度数据采集"
TaskCreate: "Step 4: 数据模型分析"
TaskCreate: "Step 5: 生成分析报告"
```

---

### Step 1: 环境与配置检查

**1.1 环境检查**：
- 确认 Python 依赖（requests, pandas, beautifulsoup4）。
- 检查 {skill_dir}/config.yaml 中的 API Key（推荐使用 Football-Data.org 或 RapidAPI）。
- 如果没有 API Key，降级使用 WebSearch/WebFetch 实时爬取。

### Step 2: 赛事筛选

- **输入**：用户指定的比赛或自动抓取"今日热门"（英超、西甲、德甲、意甲、法甲、欧冠）。
- **逻辑**：优先分析开赛时间在 24 小时内的重点赛事。

### Step 3: 数据采集

调用 {skill_dir}/scripts/fetch_match_data.py 采集以下维度：
1. **基础信息**：时间、场地、天气。
2. **赔率数据**：初盘、即时盘、凯利指数、必发交易量。
3. **近期战绩**：主客队近 6 场走势、进攻/防守效率。
4. **历史对阵 (H2H)**：过往交锋记录、风格克制分析。
5. **伤停名单**：核心球员缺阵情况。

### Step 4: 数据模型分析

调用 {skill_dir}/scripts/analyzer.py 进行逻辑研判：
- **必发分析**：热度探测，识别大单走向。
- **离散度分析**：评估赔率的一致性。
- **进球数预测**：基于两队近期得失球率。
- **冷门探测**：结合基本面与赔率异动，提示冷门概率。

### Step 5: 生成分析报告

输出包含以下模块的 Markdown 报告：
- **[比赛概况]**：时间、联赛、对阵。
- **[核心研判]**：简述基本面与赔率逻辑。
- **[数据亮点]**：如"主队近5场全胜"、"盘口从半球升至一球"。
- **[推荐方案]**：胜平负建议、进球数建议、比分参考（带信心指数）。
- **[风险提示]**：列出不确定因素。

---

## 辅助功能

- **查赔率**：python3 {skill_dir}/scripts/fetch_match_data.py --match <id> --odds-only
- **查伤停**：python3 {skill_dir}/scripts/fetch_match_data.py --match <id> --injuries-only
- **今日红单**：自动汇总高信心值推荐并生成列表。