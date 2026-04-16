# Soccer Lottery (足彩分析助手)

⚽️ 足球分析与足彩预测全流程 AI Skill（智能体技能） —— 从赛事自动抓取、基本面数据分析到胜负综合推荐，一句话搞定！
完美兼容 Coze (扣子)、Claude Code、OpenClaw 等主流 AI 平台。无需编写代码，使用自然语言即可轻松实现 AI 足彩预测专家。

## 它可以做什么
只需对 AI 说：「**分析一下今晚的欧冠焦点战**」
  → 赛事筛选 → 深度数据采集（近期战绩/H2H历史交锋） → 数据模型分析（胜率计算/进球数预测） → 生成专业的赛前分析报告

无论是针对今日热门赛事的全面扫描，还是具体某场比赛的深度复盘，它都能通过接入真实的赛事 API，为你提供有数据支撑的分析结果。

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

### 如何获取 football-data.org API Key
1. 访问 [football-data.org 官网](https://www.football-data.org/)
2. 点击顶部导航栏的 **"Pricing"** 或 **"Register"**
3. 选择免费的 **"Free Tier"**（支持五大联赛和欧冠等顶级赛事的查询，足够日常使用）
4. 填写姓名和邮箱进行注册，注册成功后 API Token 会直接发送到你的邮箱中。
5. 将邮箱中收到的 Token 填入 `config.yaml`。

## 在 Coze 等平台作为自然语言 Skill 使用
你可以直接使用本代码仓库快速注册为自然语言技能，无需自己部署服务器或写代码包装：

1. **直接导入仓库**：
    > 帮我安装技能 `https://github.com/liming199364/soccer-lottery` 
2. **自然语言配置 Key**：不需要你手动去找代码文件修改，安装完成后，你只需在对话框里直接对 AI 助手说：
   > 「帮我配置一下 soccer-lottery 技能的 API Key，我的 key 是 xxxxxxxxxx」
   
   AI 助手会自动理解你的意图，帮你基于 `config.example.yaml` 创建出 `config.yaml`，并将你的 Key 准确地填入配置文件中。一切都可以通过自然语言对话搞定！
3. **开始使用**：配置好之后，直接对机器人说「帮我分析今天的英超赛事」，即可触发完整的全自动分析流。

## 辅助功能
除了全流程分析，你还可以直接进行单项查询：
- **查赔率**：`python3 scripts/fetch_match_data.py --match <id> --odds-only`
- **查伤停**：`python3 scripts/fetch_match_data.py --match <id> --injuries-only`
- **今日红单**：自动汇总高信心值推荐并生成列表。
