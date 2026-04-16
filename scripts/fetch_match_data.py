import argparse
import json
import yaml
import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return None

def fetch_data(match_id, odds_only=False, injuries_only=False):
    # 模拟数据抓取
    config = load_config()
    data = {"match_id": match_id}
    
    if odds_only:
        data["odds"] = {"william_hill": {"home": 2.10, "draw": 3.40, "away": 3.20}}
    elif injuries_only:
        data["injuries"] = {"home_team": ["Player A"], "away_team": ["Player C"]}
    else:
        data["basic_info"] = {"time": "20:00", "weather": "Sunny"}
        data["odds"] = {"william_hill": {"home": 2.10, "draw": 3.40, "away": 3.20}}
        data["recent_form"] = {"home": "W W D L W", "away": "D D W L L"}
        data["h2h"] = "Home team won 3 of last 5 matches"
        data["injuries"] = {"home_team": ["Player A"], "away_team": ["Player C"]}
        
    print(json.dumps(data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--match", required=True, help="Match ID")
    parser.add_argument("--odds-only", action="store_true", help="Fetch only odds data")
    parser.add_argument("--injuries-only", action="store_true", help="Fetch only injuries data")
    args = parser.parse_args()
    
    fetch_data(args.match, args.odds_only, args.injuries_only)
