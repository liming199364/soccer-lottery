# 足彩助手 (Soccer Lottery)

足球分析与足彩预测全流程 AI Skill —— 从赛事抓取到综合推荐报告，一句话搞定。
兼容 Claude Code 和 OpenClaw 的 skill 格式。安装后说「帮我分析今天的英超」即可触发完整流程。

## 它能做什么
"分析今晚的欧冠焦点战"
  → 赛事筛选 → 深度数据采集（基本面/赔率/伤停） → 数据模型分析（必发/离散度/冷门） → 生成分析报告

默认模式下，它会自动抓取今日热门赛事并进行全维度数据扫描；你也可以提供具体对阵或联赛进行深度复盘和预测。

## 核心能力

| 能力 | 说明 | 实现 |
| --- | --- | --- |
| **环境与配置** | 自动检查 Python 依赖与 API Key (推荐 Football-Data.org 或 RapidAPI) | `config.yaml` |
| **赛事筛选** | 抓取今日热门（英超/西甲/欧冠等）或分析用户指定对阵 | `SKILL.md` Step 2 |
| **深度数据采集** | 基础信息、赔率、近期战绩、H2H、伤停名单等多维度数据采集 | `scripts/fetch_match_data.py` |
| **数据模型分析** | 必发热度、赔率离散度、进球数预测与冷门探测研判 | `scripts/analyzer.py` |
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
    key: "YOUR_API_KEY_HERE"  # Get from https://www.football-data.org/
```

## 辅助功能
除了全流程分析，你还可以直接进行单项查询：
- **查赔率**：`python3 scripts/fetch_match_data.py --match <id> --odds-only`
- **查伤停**：`python3 scripts/fetch_match_data.py --match <id> --injuries-only`
- **今日红单**：自动汇总高信心值推荐并生成列表。
