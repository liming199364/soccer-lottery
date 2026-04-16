import argparse
import json
import yaml
import os
import requests
from datetime import datetime

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return None

def get_headers(config):
    headers = {}
    if config and 'api' in config and 'football_data' in config['api']:
        api_key = config['api']['football_data'].get('key')
        if api_key and api_key != "YOUR_API_KEY_HERE":
            headers['X-Auth-Token'] = api_key
    return headers

def fetch_today_matches(config):
    headers = get_headers(config)
    if not headers:
        return {"error": "API Key not configured. Please check config.yaml."}
        
    url = "https://api.football-data.org/v4/matches"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # 过滤出配置的联赛
        target_leagues = config.get('settings', {}).get('leagues', ["PL", "PD", "BL1", "SA", "FL1", "CL"])
        filtered_matches = []
        
        for match in data.get('matches', []):
            if match.get('competition', {}).get('code') in target_leagues:
                filtered_matches.append({
                    "id": match['id'],
                    "league": match['competition']['name'],
                    "home_team": match['homeTeam']['name'],
                    "away_team": match['awayTeam']['name'],
                    "utcDate": match['utcDate'],
                    "status": match['status']
                })
        return {"date": datetime.now().strftime("%Y-%m-%d"), "matches": filtered_matches}
    except Exception as e:
        return {"error": str(e)}

def fetch_match_details(match_id, config):
    headers = get_headers(config)
    if not headers:
        return {"error": "API Key not configured"}
        
    # 获取比赛详情和H2H
    url = f"https://api.football-data.org/v4/matches/{match_id}/head2head"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def fetch_data(match_id=None, odds_only=False, injuries_only=False):
    config = load_config()
    
    # 如果没有提供 match_id，则获取今日热门赛事
    if not match_id:
        result = fetch_today_matches(config)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 如果提供了 match_id，获取特定比赛的详细信息
    data = {"match_id": match_id}
    
    # 从 football-data.org 获取真实数据 (H2H和近期战绩)
    h2h_data = fetch_match_details(match_id, config)
    
    if odds_only:
        # 实际情况中，赔率和伤停通常需要其他API（如RapidAPI的API-Sports）
        # 这里为了演示，如果是真实API调用失败或未配置，返回提示
        data["odds"] = {"error": "Odds data requires RapidAPI integration. Not fully implemented in basic tier."}
    elif injuries_only:
        data["injuries"] = {"error": "Injuries data requires RapidAPI integration. Not fully implemented in basic tier."}
    else:
        # 组装基础信息和H2H
        if "error" not in h2h_data:
            match_info = h2h_data.get('aggregates', {})
            data["h2h_aggregates"] = {
                "numberOfMatches": match_info.get('numberOfMatches'),
                "totalGoals": match_info.get('totalGoals'),
                "homeTeamWins": match_info.get('homeTeam', {}).get('wins'),
                "awayTeamWins": match_info.get('awayTeam', {}).get('wins'),
                "draws": match_info.get('homeTeam', {}).get('draws')
            }
            
            # 提取最近的交锋记录
            recent_matches = []
            for m in h2h_data.get('matches', [])[:5]:
                recent_matches.append({
                    "date": m.get('utcDate'),
                    "home": m.get('homeTeam', {}).get('name'),
                    "away": m.get('awayTeam', {}).get('name'),
                    "score": f"{m.get('score', {}).get('fullTime', {}).get('home', '?')}-{m.get('score', {}).get('fullTime', {}).get('away', '?')}"
                })
            data["recent_h2h"] = recent_matches
        else:
            data["h2h_error"] = h2h_data["error"]
            
        data["odds"] = {"status": "Pending RapidAPI Integration"}
        data["injuries"] = {"status": "Pending RapidAPI Integration"}
        
    print(json.dumps(data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--match", required=False, help="Match ID")
    parser.add_argument("--odds-only", action="store_true", help="Fetch only odds data")
    parser.add_argument("--injuries-only", action="store_true", help="Fetch only injuries data")
    args = parser.parse_args()
    
    fetch_data(args.match, args.odds_only, args.injuries_only)
