import requests
import yaml
import os
import json
from datetime import datetime

# ==========================================
# 1. 基础工具与配置
# ==========================================

def load_config():
    """加载项目根目录下的 config.yaml"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}

# ==========================================
# 2. API 数据源 (Football-Data.org)
# ==========================================

def fetch_football_data_api(endpoint, config):
    """封装 Football-Data.org API 调用"""
    api_key = config.get('api', {}).get('football_data', {}).get('key')
    if not api_key or "YOUR" in api_key:
        return {"error": "Football-Data API Key 未配置"}
    
    url = f"https://api.football-data.org/v4/{endpoint}"
    headers = {"X-Auth-Token": api_key}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# 3. 高层编排逻辑
# ==========================================

def get_match_detail_data(match_id, config=None):
    """供其他脚本（如 analyzer.py）调用的详情获取函数，返回 dict"""
    if config is None:
        config = load_config()
        
    data = {"match_id": match_id}
    h2h_raw = fetch_football_data_api(f"matches/{match_id}/head2head", config)
    
    if "error" not in h2h_raw:
        agg = h2h_raw.get('aggregates', {})
        home_team = agg.get('homeTeam', {}).get('name', '')
        away_team = agg.get('awayTeam', {}).get('name', '')
        
        data.update({
            "home_team": home_team, "away_team": away_team,
            "h2h_aggregates": {
                "matches": agg.get('numberOfMatches'), "goals": agg.get('totalGoals'),
                "home_wins": agg.get('homeTeam', {}).get('wins'), "away_wins": agg.get('awayTeam', {}).get('wins'),
                "draws": agg.get('homeTeam', {}).get('draws')
            }
        })
        
        # 情报占位符（由 Agent 运行时通过 WebSearch 填充）
        data["intelligence"] = {
            "injuries": "待联网核实",
            "odds_trend": "待联网核实",
            "hot_level": "High" if any(x in home_team or x in away_team for x in ["Napoli", "Tottenham", "Benfica", "Real Madrid"]) else "Medium"
        }
        
        return data
    else:
        return {"match_id": match_id, "error": h2h_raw["error"]}

def fetch_data(match_id=None):
    """主数据获取入口 (CLI Orchestrator)"""
    config = load_config()
    
    # 1. 列表模式：获取今日所有赛事
    if not match_id:
        raw_matches = fetch_football_data_api("matches", config)
        
        matches = []
        if "error" not in raw_matches:
            for m in raw_matches.get('matches', []):
                matches.append({
                    "id": m['id'], "league": m['competition']['name'],
                    "home_team": m['homeTeam']['name'], "away_team": m['awayTeam']['name'],
                    "utcDate": m['utcDate'], "status": m['status']
                })
        
        # 如果 API 没返回数据或数据较少，提示调用者进行 WebSearch 校验
        result = {"date": datetime.now().strftime("%Y-%m-%d"), "matches": matches}
        if not matches:
            result["warning"] = "API returned no matches. WebSearch VERIFICATION REQUIRED for non-European leagues."
            
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 2. 详情模式
    data = get_match_detail_data(match_id, config)
    print(json.dumps(data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--match", help="指定 Match ID 获取详情，不传则列出今日赛事")
    args = parser.parse_args()
    
    fetch_data(match_id=args.match)
