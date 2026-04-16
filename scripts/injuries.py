import argparse
import json

def get_injuries(match_id):
    # 模拟伤停信息
    injuries = {
        "match_id": match_id,
        "home_team": ["Player A (Injured)", "Player B (Suspended)"],
        "away_team": ["Player C (Doubtful)"]
    }
    print(json.dumps(injuries, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--match", required=True, help="Match ID")
    args = parser.parse_args()
    get_injuries(args.match)
