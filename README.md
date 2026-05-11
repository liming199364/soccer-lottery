# Soccer Lottery (足彩分析助手)

⚽️ 足球分析与足彩预测全流程 AI Skill（智能体技能） —— 从赛事自动抓取、基本面数据分析到胜负综合推荐，一句话搞定！
完美兼容 Trae Solo、Claude Code、OpenClaw 等主流 AI 平台。无需编写代码，使用自然语言即可轻松实现 AI 足彩预测专家。

## 它可以做什么
只需对 AI 说：「**今日红单**」或「**怎么买**」
  → **全自动管道触发** → 赛事全量抓取 → 焦点场次筛选 → 深度建模（H2H/胜率计算） → **让球/胜平负双重研判** → 生成详版分析报告

无论是针对今日热门赛事的全面扫描，还是具体某场比赛的深度复盘，它都能通过接入真实的赛事 API（及联网补全），为您提供有数据支撑的分析结果。

## 核心能力

| 能力 | 说明 | 实现 |
| --- | --- | --- |
| **自动化管道** | 一键触发抓取+分析+报告生成全流程，无需多轮对话 | `SKILL.md` Auto-Pipeline |
| **让球深度研判** | 自动对比「胜平负」与「让球」信心值，优先推荐最优方案 | `scripts/analyzer.py` |
| **多源数据补全** | API 结合 Web Scraper（澳客/500网），确保数据不中断 | `scripts/fetch_match_data.py` |
| **环境与配置** | 自动检查 Python 依赖与 API Key (Football-Data.org / The Odds API) | `config.yaml` |
| **报告生成** | 输出包含胜平负/让球赔率、关键因素、过关建议的详版报告 | `SKILL.md` Step 5 |

## 分析流程

### 🔄 数据获取流程
```
1. The Odds API (主要数据源 - 免费版500次/月)
   └─ 获取英超等联赛的实时赔率数据

2. 备用网页数据源 (多个备选，防止失效)
   └─ Flashscore、Betexplorer 等网站
   └─ 覆盖所有国内足彩联赛
```

### 🧠 分析流程
```
1. 赔率期望值计算
   └─ 根据赔率计算各选项的期望值

2. 赔率差距分析
   └─ 计算赔率差距，差距越大信心越高

3. 赔率波动分析 (联网获取历史数据)
   └─ 通过 Google/Bing 搜索引擎检索历史赔率
   └─ 分析赔率变化趋势（稳定、下降、上升、急剧变化）

4. 冷门概率检测
   └─ 根据赔率差距计算冷门概率

5. 信心指数综合计算
   └─ 综合考虑赔率、波动、冷门风险，生成最终信心指数
```

### 📊 支持的联赛（国内足彩全覆盖）

本系统通过「API + 智能爬虫」双引擎，实现了对国内竞足赛事的**全维度覆盖**：

1. **欧洲顶级联赛 (API 驱动)**：
   - 完美支持：英超、西甲、德甲、意甲、法甲、欧冠、欧联、葡超等。
   - 数据源：Football-Data.org (专业级实时数据)。

2. **亚洲及其他联赛 (爬虫驱动)**：
   - **支持亚洲联赛**：日职联 (J-League)、韩职联 (K-League)、中超、亚冠等。
   - **支持小联赛**：荷甲、比甲、瑞典超、挪超、美职联等竞足常驻赛事。
   - 数据源：通过 Okooo (澳客网) 和 500.com 实时抓取。只要是**国内竞彩挂牌**的比赛，系统均可识别并分析。

3. **让球盘口支持**：
   - 针对国内竞足特点，系统会自动抓取「让胜/让平/让负」数据，并结合 H2H 模型进行优先级研判。

---

## 🚀 快捷指令（Shortcuts）

## 安装

**Claude Code:**
```bash
git clone --depth 1 https://github.com/liming199364/soccer-lottery.git ~/.claude/skills/soccer-lottery
cd ~/.claude/skills/soccer-lottery && pip install -r requirements.txt
cp config.example.yaml config.yaml # 然后填入你的 API Key
```

**OpenClaw / Coze:**
```bash
# 直接在对话框输入以下指令
帮我安装技能 https://github.com/liming199364/soccer-lottery
```

## 配置
在 `config.yaml` 中配置你的数据源 API Key：
```yaml
api:
  football_data:
    key: "YOUR_FOOTBALL_DATA_API_KEY"  # Get from https://www.football-data.org/
  the_odds_api:
    key: "YOUR_THE_ODDS_API_KEY"  # Get from https://the-odds-api.com/
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

## 在 Coze 等平台作为自然语言 Skill 使用
你可以直接使用本代码仓库快速注册为自然语言技能，无需自己部署服务器或写代码包装：

1. **直接导入仓库**：
    > 帮我安装技能 `https://github.com/liming199364/soccer-lottery` 
2. **自然语言配置 Key**：不需要你手动去找代码文件修改，安装完成后，你只需在对话框里直接对 AI 助手说：
   > 「帮我配置一下 soccer-lottery 技能的 API Key，我的 key 是 xxxxxxxxxx」
   
   AI 助手会自动理解你的意图，帮你基于 `config.example.yaml` 创建出 `config.yaml`，并将你的 Key 准确地填入配置文件中。
3. **开始使用**：配置好之后，直接对机器人说「**今日红单**」或「**怎么买**」，即可触发全自动分析。

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
- **单场分析**：`python3 scripts/analyzer.py --match <id>`
- **查赔率**：`python3 scripts/fetch_match_data.py --match <id> --odds-only`
- **查伤停**：`python3 scripts/fetch_match_data.py --match <id> --injuries-only`

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
