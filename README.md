# Soccer Lottery (足彩分析助手)

⚽️ 足球分析与足彩预测全流程 AI Skill（智能体技能） —— 从赛事自动抓取、基本面数据分析到胜负综合推荐，一句话搞定！
完美兼容 Trae Solo、Claude Code、OpenClaw 等主流 AI 平台。无需编写代码，使用自然语言即可轻松实现 AI 足彩预测专家。

## 它可以做什么
只需对 AI 说：「**分析一下今晚的欧冠焦点战**」
  → 赛事筛选 → 深度数据采集（近期战绩/H2H历史交锋） → 数据模型分析（胜率计算/进球数预测） → 生成专业的赛前分析报告

无论是针对今日热门赛事的全面扫描，还是具体某场比赛的深度复盘，它都能通过接入真实的赛事 API，为你提供有数据支撑的分析结果。

## 核心能力

| 能力 | 说明 | 实现 |
| --- | --- | --- |
| **环境与配置** | 自动检查 Python 依赖与 API Key (支持 Football-Data.org 和 The Odds API) | `config.yaml` |
| **赛事筛选** | 抓取今日热门（英超/西甲/德甲/意甲/法甲等）或分析用户指定对阵 | `SKILL.md` Step 2 |
| **深度数据采集** | 基础信息、赔率（胜负平+让球盘）、近期战绩、H2H、伤停名单等多维度数据采集 | `scripts/fetch_match_data.py` |
| **数据模型分析** | 必发热度、赔率离散度、进球数预测与冷门探测研判 | `scripts/analyzer.py` |
| **智能推荐** | 支持胜负平推荐、让球推荐（让胜/让平/让负），自动选择信心更高的方案 | `scripts/analyzer.py` |
| **中文翻译** | 自动翻译球队名称为中文，支持特殊名称映射 | `scripts/analyzer.py` |
| **报告生成** | 输出包含概况、核心研判、数据亮点、推荐方案与风险提示的 Markdown 报告 | `SKILL.md` Step 5 |

## 安装

**Claude Code:**
```bash
git clone --depth 1 https://github.com/liming199364/soccer-lottery.git ~/.claude/skills/soccer-lottery
cd ~/.claude/skills/soccer-lottery && pip install -r requirements.txt
cp config.example.yaml config.yaml # 然后填入你的 API Key
```

**OpenClaw:**
```bash
git clone --depth 1 https://github.com/liming199364/soccer-lottery.git ~/.openclaw/skills/soccer-lottery
cd ~/.openclaw/skills/soccer-lottery && pip install -r requirements.txt
cp config.example.yaml config.yaml # 然后填入你的 API Key
```

## 配置
在 `config.yaml` 中配置你的数据源 API Key：
```yaml
api:
  football_data:
    key: "YOUR_FOOTBALL_DATA_API_KEY"  # Get from https://www.football-data.org/
  the_odds_api:
    key: "YOUR_THE_ODDS_API_KEY"  # Get from https://the-odds-api.com/

settings:
  leagues:
    - "PL"    # 英超
    - "PD"    # 西甲
    - "BL1"   # 德甲
    - "SA"    # 意甲
    - "FL1"   # 法甲
    - "CL"    # 欧冠
    # ... 更多联赛
```

### 如何获取 API Key

**1. Football-Data.org (赛事数据)**
- 访问 [football-data.org 官网](https://www.football-data.org/)
- 选择免费的 **"Free Tier"**（支持五大联赛和欧冠等顶级赛事）
- 注册后 API Token 会发送到你的邮箱

**2. The Odds API (赔率数据)**
- 访问 [The Odds API 官网](https://the-odds-api.com/)
- 注册免费账户，每月免费额度 500 次请求
- 提供结构化的赔率数据，包括胜负平和让球盘口

## 在 Trae Solo 等平台作为自然语言 Skill 使用
你可以直接使用本代码仓库快速注册为自然语言技能，无需自己部署服务器或写代码包装：

1. **直接导入仓库**：
    > 帮我安装技能 `https://github.com/liming199364/soccer-lottery` 
2. **自然语言配置 Key**：不需要你手动去找代码文件修改，安装完成后，你只需在对话框里直接对 AI 助手说：
   > 「帮我配置一下 soccer-lottery 技能的 API Key，我的 key 是 xxxxxxxxxx」
   
   AI 助手会自动理解你的意图，帮你基于 `config.example.yaml` 创建出 `config.yaml`，并将你的 Key 准确地填入配置文件中。一切都可以通过自然语言对话搞定！
3. **开始使用**：配置好之后，直接对机器人说「帮我分析今天的英超赛事」，即可触发完整的全自动分析流。

## 功能特性

### 🏆 推荐类型
- **胜负平**：主胜、平局、客胜
- **让球推荐**：让胜、让平、让负（当让球信心高于胜负平时自动选择）

### 📊 输出内容
- 详细分析（包含胜负平和让球盘口信息）
- 信心指数排行
- 投注分布建议
- 过关推荐（2串1、3串1组合）

### 🌍 球队名称翻译
自动翻译球队名称为中文，支持常用球队特殊名称映射（如 Arsenal → 阿森纳）

## 辅助功能
除了全流程分析，你还可以直接进行单项查询：
- **查赔率**：`python3 scripts/fetch_match_data.py --match <id> --odds-only`
- **查伤停**：`python3 scripts/fetch_match_data.py --match <id> --injuries-only`
- **今日红单**：自动汇总高信心值推荐并生成列表

## 输出示例

```
## 📊 今日足彩推荐（2026-05-10）

### 📋 详细分析

#### 伯恩利 VS 阿斯顿维拉
- **联赛**：英超
- **时间**：05-10 21:00

**💰 胜平负推荐**
| 选项 | 赔率 |
|------|------|
| 主胜 | 6.80 |
| 平局 | 3.15 |
| 客胜 | 1.62 |
- **推荐**：负
- **信心指数**：95%

**🎯 让球盘口**
| 让球值 | 让球主队 | 让球客队 |
|--------|---------|---------|
| +0.25 | 1.85 | 2.06 |
- **让球推荐**：让平
- **让球信心**：80%

---

## 🏆 过关推荐

### 2串1
| 组合 | 推荐 | 赔率 | 信心 |
|------|------|------|------|
| 伯恩利 VS 阿斯顿维拉 + 水晶宫 VS 埃弗顿 | 负+负 | 4.81 | 76% |

### 3串1
| 组合 | 推荐 | 赔率 | 信心 |
|------|------|------|------|
| 伯恩利 VS 阿斯顿维拉 + 水晶宫 VS 埃弗顿 + 诺丁汉森林 VS 纽卡斯尔联 | 负+负+负 | 12.08 | 76% |
```

## License
MIT License
