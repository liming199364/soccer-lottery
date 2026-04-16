# Soccer Lottery (足彩分析助手)

足球分析与足彩预测全流程 AI Skill —— 从赛事抓取到综合推荐，一句话搞定。
兼容 Claude Code 和 OpenClaw 的 skill 格式。安装后输入关键词即可触发完整流程。

## 它能做什么
说出「帮我分析一下今天的足彩」或「预测一下今晚英超比分」
  → 赛事抓取 → 球队近况（H2H） → 伤停预测 → 赔率分析 → 综合推荐（胜平负建议）

核心功能涵盖主流联赛（五大联赛、欧冠等）的数据自动抓取，并提供基于统计模型的赛前分析。

## 核心能力

| 能力 | 说明 | 实现 |
| --- | --- | --- |
| **赛事抓取** | 自动抓取五大联赛、欧冠等主流今日赛事 | `scripts/fetch_matches.py` |
| **赔率分析** | 主流博彩公司（威廉希尔、立博、Bet365等）初盘与即时盘口分析 | `scripts/odds_analysis.py` |
| **球队近况** | 历史交锋记录 (H2H)、近期战绩连胜/连败趋势 | `scripts/team_status.py` |
| **伤停预测** | 核心球员伤病、停赛信息对战局影响评估 | `scripts/injuries.py` |
| **综合推荐** | 基于多维数据的胜平负概率、比分预测及投注建议 | `toolkit/prediction.py` |

## 安装

**Claude Code:**
```bash
git clone --depth 1 https://github.com/liming199364/soccer-lottery.git ~/.claude/skills/soccer-lottery
cd ~/.claude/skills/soccer-lottery && pip install -r requirements.txt
```

**OpenClaw:**
```bash
git clone --depth 1 https://github.com/liming199364/soccer-lottery.git ~/.openclaw/skills/soccer-lottery
cd ~/.openclaw/skills/soccer-lottery && pip install -r requirements.txt
```

## 触发关键词
- 足彩
- 赔率
- 足球分析
- 比分预测
- 今日赛事
- 球队H2H
- 胜平负建议

## 目录结构
- `SKILL.md`: Skill 核心指令与流程定义
- `scripts/`: 数据抓取与分析脚本
- `toolkit/`: 预测模型与工具库
- `requirements.txt`: 依赖包列表
