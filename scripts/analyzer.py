import argparse
import json
import os
import sys

# 添加当前目录到环境变量以便导入 fetch_match_data
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fetch_match_data import fetch_match_details, load_config

def calculate_win_probability(h2h_aggregates):
    if not h2h_aggregates or h2h_aggregates.get('numberOfMatches', 0) == 0:
        return {"home": 33, "draw": 34, "away": 33}
        
    total_matches = h2h_aggregates.get('numberOfMatches', 1)
    home_wins = h2h_aggregates.get('homeTeamWins', 0)
    draws = h2h_aggregates.get('draws', 0)
    away_wins = h2h_aggregates.get('awayTeamWins', 0)
    
    return {
        "home": round((home_wins / total_matches) * 100, 1),
        "draw": round((draws / total_matches) * 100, 1),
        "away": round((away_wins / total_matches) * 100, 1)
    }

def analyze(match_id):
    config = load_config()
    match_data = fetch_match_details(match_id, config)
    
    if "error" in match_data:
        print(json.dumps({"error": match_data["error"]}, ensure_ascii=False, indent=2))
        return

    # 获取基础统计信息
    aggregates = match_data.get('aggregates', {})
    recent_matches = match_data.get('matches', [])[:5]
    
    # 简单的历史概率计算模型
    probs = calculate_win_probability(aggregates)
    
    # 决定推荐倾向
    recommendation = "Draw"
    confidence = "Low"
    if probs["home"] > 50:
        recommendation = "Home Win"
        confidence = "High" if probs["home"] > 65 else "Medium"
    elif probs["away"] > 50:
        recommendation = "Away Win"
        confidence = "High" if probs["away"] > 65 else "Medium"
    
    # 进球数预测 (基于历史交锋平均进球数)
    avg_goals = 0
    if aggregates.get('numberOfMatches', 0) > 0:
        avg_goals = aggregates.get('totalGoals', 0) / aggregates.get('numberOfMatches', 1)
        
    goals_prediction = f"Over 2.5 goals ({round(avg_goals, 2)} avg/match)" if avg_goals > 2.5 else f"Under 2.5 goals ({round(avg_goals, 2)} avg/match)"

    # 组装最终报告
    report = {
        "match_id": match_id,
        "match_info": {
            "home_team": match_data.get('aggregates', {}).get('homeTeam', {}).get('name', 'Unknown'),
            "away_team": match_data.get('aggregates', {}).get('awayTeam', {}).get('name', 'Unknown'),
            "total_h2h_matches": aggregates.get('numberOfMatches', 0)
        },
        "analysis": {
            "historical_win_probability": probs,
            "goals_prediction": goals_prediction,
            "upset_alert": "Low probability of upset" if confidence == "High" else "High probability of upset / Draw likely"
        },
        "recommendation": {
            "result": recommendation,
            "confidence": confidence,
            "note": "Prediction based strictly on historical H2H data. Requires current odds and injury data for a complete model."
        }
    }
    
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--match", required=True, help="Match ID to analyze")
    args = parser.parse_args()
    
    analyze(args.match)
