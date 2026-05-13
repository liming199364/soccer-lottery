import argparse
import json
import os
import sys
import requests
from datetime import datetime, timedelta
from itertools import combinations

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fetch_match_data import get_match_detail_data, load_config

def calculate_win_probability(h2h_aggregates):
    if not h2h_aggregates or h2h_aggregates.get('matches', 0) == 0:
        return {"home": 33, "draw": 34, "away": 33}
        
    total_matches = h2h_aggregates.get('matches', 1)
    home_wins = h2h_aggregates.get('home_wins', 0)
    draws = h2h_aggregates.get('draws', 0)
    away_wins = h2h_aggregates.get('away_wins', 0)
    
    return {
        "home": round((home_wins / total_matches) * 100, 1),
        "draw": round((draws / total_matches) * 100, 1),
        "away": round((away_wins / total_matches) * 100, 1)
    }

SPECIAL_NAMES = {
    "Arsenal": "阿森纳",
    "Tottenham": "热刺",
    "Manchester United": "曼联",
    "Manchester City": "曼城",
    "Liverpool": "利物浦",
    "Chelsea": "切尔西",
    "Newcastle United": "纽卡斯尔联",
    "West Ham United": "西汉姆联",
    "Crystal Palace": "水晶宫",
    "Everton": "埃弗顿",
    "Burnley": "伯恩利",
    "Nottingham Forest": "诺丁汉森林",
    "Aston Villa": "阿斯顿维拉",
    "PSG": "巴黎圣日耳曼",
    "Bayern Munich": "拜仁慕尼黑",
    "Borussia Dortmund": "多特蒙德",
    "RB Leipzig": "RB莱比锡",
    "Real Madrid": "皇家马德里",
    "Barcelona": "巴塞罗那",
    "Atletico Madrid": "马德里竞技",
    "Juventus": "尤文图斯",
    "AC Milan": "AC米兰",
    "Inter Milan": "国际米兰",
    "Napoli": "那不勒斯",
    "AS Roma": "罗马",
    "Lazio": "拉齐奥",
}

CACHE = {}

def translate_team_name(name):
    if name in SPECIAL_NAMES:
        return SPECIAL_NAMES[name]
    
    if name in CACHE:
        return CACHE[name]
    
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q={requests.utils.quote(name)}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result and len(result) > 0 and len(result[0]) > 0:
                translation = result[0][0][0]
                CACHE[name] = translation
                return translation
    except Exception:
        pass
    
    CACHE[name] = name
    return name

def calculate_parlay_odds(matches):
    total_odds = 1.0
    for match in matches:
        rec = match["推荐"]
        odds = match["赔率"]
        
        if rec == "胜":
            total_odds *= odds["主胜"]
        elif rec == "平":
            total_odds *= odds["平局"]
        elif rec == "负":
            total_odds *= odds["客胜"]
        elif rec == "让胜":
            if "让球盘口" in match:
                total_odds *= match["让球盘口"]["让球主队赔率"]
            else:
                total_odds *= odds["主胜"]
        elif rec == "让平":
            if "让球盘口" in match:
                total_odds *= (match["让球盘口"]["让球主队赔率"] + match["让球盘口"]["让球客队赔率"]) / 2
            else:
                total_odds *= odds["平局"]
        elif rec == "让负":
            if "让球盘口" in match:
                total_odds *= match["让球盘口"]["让球客队赔率"]
            else:
                total_odds *= odds["客胜"]
    return round(total_odds, 2)

def calculate_h2h_confidence(home_odds, draw_odds, away_odds, recommendation):
    min_odds = min(home_odds, draw_odds, away_odds)
    max_odds = max(home_odds, draw_odds, away_odds)
    
    if recommendation == "胜":
        target_odds = home_odds
    elif recommendation == "平":
        target_odds = draw_odds
    else:
        target_odds = away_odds
    
    odds_ratio = max_odds / target_odds if target_odds != 0 else 1
    confidence = min(95, max(60, 75 + (odds_ratio - 1) * 10))
    return round(confidence)

def calculate_handicap_confidence(home_handicap_odds, away_handicap_odds):
    odds_diff = abs(home_handicap_odds - away_handicap_odds)
    avg_odds = (home_handicap_odds + away_handicap_odds) / 2
    
    if odds_diff < 0.1:
        confidence = 70
    elif odds_diff < 0.2:
        confidence = 75
    elif odds_diff < 0.3:
        confidence = 80
    else:
        confidence = 85
    
    if avg_odds < 1.8:
        confidence += 5
    elif avg_odds > 2.5:
        confidence -= 5
    
    return min(95, max(60, confidence))

def adjust_confidence_by_movement(confidence, trend):
    """根据赔率走势方向调整信心（由 Agent 在调用时传入走势描述）"""
    if not trend:
        return confidence
    
    trend_lower = trend.lower()
    if "down" in trend_lower or "降" in trend_lower or "走低" in trend_lower:
        confidence += 5
    elif "up" in trend_lower or "升" in trend_lower or "走高" in trend_lower:
        confidence -= 5
    
    return min(95, max(60, confidence))

def detect_upset_probability(home_odds, draw_odds, away_odds):
    """检测冷门概率"""
    min_odds = min(home_odds, draw_odds, away_odds)
    
    if min_odds == home_odds:
        favorite_odds = home_odds
        underdog_odds = max(draw_odds, away_odds)
    elif min_odds == away_odds:
        favorite_odds = away_odds
        underdog_odds = max(home_odds, draw_odds)
    else:
        favorite_odds = draw_odds
        underdog_odds = max(home_odds, away_odds)
    
    odds_ratio = underdog_odds / favorite_odds
    
    if odds_ratio < 2:
        upset_prob = 10
    elif odds_ratio < 3:
        upset_prob = 25
    elif odds_ratio < 4:
        upset_prob = 40
    else:
        upset_prob = 60
    
    return upset_prob

def adjust_for_upset_risk(confidence, home_odds, draw_odds, away_odds, recommendation):
    """根据冷门风险调整信心指数"""
    upset_prob = detect_upset_probability(home_odds, draw_odds, away_odds)
    
    min_odds = min(home_odds, draw_odds, away_odds)
    is_favorite = False
    
    if (recommendation == "胜" and home_odds == min_odds) or \
       (recommendation == "负" and away_odds == min_odds) or \
       (recommendation == "平" and draw_odds == min_odds):
        is_favorite = True
    
    if is_favorite and upset_prob > 30:
        confidence -= min(upset_prob // 5, 15)
    
    return min(95, max(50, confidence))

def generate_parlay_combinations(recommendations, max_parlay=3):
    parlays = {
        "2串1": [],
        "3串1": []
    }

    sorted_recs = sorted(recommendations, key=lambda x: x.get("信心指数", 0), reverse=True)

    if len(sorted_recs) >= 2:
        for combo in combinations(sorted_recs, 2):
            combo_list = list(combo)
            parlays["2串1"].append({
                "比赛组合": [f"{m['主队']} VS {m['客队']}" for m in combo_list],
                "推荐": "+".join([m["推荐"] for m in combo_list]),
                "组合赔率": calculate_parlay_odds(combo_list),
                "信心指数": min(m.get("信心指数", 50) for m in combo_list),
                "比赛时间": [f"{m['比赛日期']} {m['比赛时间']}" for m in combo_list]
            })

    if len(sorted_recs) >= 3:
        for combo in combinations(sorted_recs, 3):
            combo_list = list(combo)
            parlays["3串1"].append({
                "比赛组合": [f"{m['主队']} VS {m['客队']}" for m in combo_list],
                "推荐": "+".join([m["推荐"] for m in combo_list]),
                "组合赔率": calculate_parlay_odds(combo_list),
                "信心指数": min(m.get("信心指数", 50) for m in combo_list),
                "比赛时间": [f"{m['比赛日期']} {m['比赛时间']}" for m in combo_list]
            })

    for key in parlays:
        parlays[key] = sorted(parlays[key], key=lambda x: x["组合赔率"], reverse=True)[:3]

    return parlays

def generate_simple_report(match_id=None, league=None):
    config = load_config()
    
    report = {
        "日期": datetime.now().strftime("%Y-%m-%d"),
        "联赛": league or "全部",
        "推荐列表": [],
        "分析详情": [],
        "信心指数排行": [],
        "投注分布": {}
    }

    now = datetime.now()
    cutoff = now + timedelta(hours=24)
    
    print(f"[!] 正在筛选从 {now.strftime('%m-%d %H:%M')} 到 {cutoff.strftime('%m-%d %H:%M')} 之间的赛事...")
    
    return report

def analyze(match_id, injury_info=None, trend_info=None):
    config = load_config()
    raw_data = get_match_detail_data(match_id, config)
    
    if "error" in raw_data:
        print(json.dumps({"error": raw_data["error"]}, ensure_ascii=False, indent=2))
        return

    # 1. 基础数据
    aggregates = raw_data.get('h2h_aggregates', {})
    h2h_probs = calculate_win_probability(aggregates)
    hot_level = raw_data.get('intelligence', {}).get('hot_level', 'Medium')
    
    # 2. 信心权重分配 (50% 赔率走势 + 30% 实时情报 + 20% H2H)
    base_confidence = max(h2h_probs.values()) / 100
    
    # 赔率走势修正 (50%) - 最高权重（由 Agent 传入）
    trend_score = 0.5 # 默认中性
    if trend_info:
        if "down" in trend_info.lower() or "降" in trend_info: trend_score = 0.9
        elif "up" in trend_info.lower() or "升" in trend_info: trend_score = 0.1
        
    # 伤病情报修正 (30%) - 权重高于历史数据（由 Agent 传入）
    injury_score = 0.5 # 默认中性
    if injury_info:
        if "missing core" in injury_info.lower() or "核心缺阵" in injury_info: injury_score = 0.1
        elif "full squad" in injury_info.lower() or "全主力" in injury_info: injury_score = 0.9

    # 全新加权计算逻辑
    final_confidence_val = (trend_score * 0.5) + (injury_score * 0.3) + (base_confidence * 0.2)
    
    # 3. 热门场次降级处理
    if hot_level == "High":
        final_confidence_val *= 0.85
        
    # 4. 推荐决策
    recommendation = "平"
    if h2h_probs["home"] > 50: recommendation = "胜"
    elif h2h_probs["away"] > 50: recommendation = "负"
    
    # 5. 让球逻辑保护
    if h2h_probs["home"] > h2h_probs["away"] + 5:
        handicap_val = -1
    elif h2h_probs["away"] > h2h_probs["home"] + 5:
        handicap_val = 1
    else:
        handicap_val = -1
    
    final_rec = recommendation
    
    if hot_level == "High" or final_confidence_val < 0.7:
        if handicap_val < 0:
            if recommendation == "胜":
                final_rec = "让平" if final_confidence_val > 0.6 else "让负"
            else:
                final_rec = "让负"
        else:
            if recommendation == "负":
                final_rec = "让平" if final_confidence_val > 0.6 else "让胜"
            else:
                final_rec = "让胜"
            
    report = {
        "match_id": match_id,
        "match_info": {
            "home_team": raw_data.get('home_team'),
            "away_team": raw_data.get('away_team'),
            "hot_level": hot_level,
            "handicap": f"主{handicap_val:+}"
        },
        "intelligence": {
            "injury_status": injury_info or "未知 (建议联网确认)",
            "odds_trend": trend_info or "稳定 (建议联网确认)"
        },
        "recommendation": {
            "result": final_rec,
            "confidence": f"{round(final_confidence_val * 100)}%",
            "note": f"{'主让球' if handicap_val < 0 else '主受让'}"
        }
    }
    
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--match", required=False, help="Match ID to analyze")
    parser.add_argument("--league", required=False, help="League to analyze")
    parser.add_argument("--simple", action="store_true", help="Generate simple report")
    parser.add_argument("--injury", help="Injury intelligence (e.g. 'missing core')")
    parser.add_argument("--trend", help="Odds trend intelligence (e.g. 'down')")
    args = parser.parse_args()

    if args.simple or args.league:
        result = generate_simple_report(args.match, args.league)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.match:
        analyze(args.match, injury_info=args.injury, trend_info=args.trend)
    else:
        result = generate_simple_report()
        print(json.dumps(result, ensure_ascii=False, indent=2))
