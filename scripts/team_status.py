import argparse
import json

def get_team_status(match_id):
    # 模拟球队近况与H2H数据
    status = {
        "match_id": match_id,
        "h2h": "Home team won 3 of last 5 matches",
        "home_recent": "W W D L W",
        "away_recent": "D D W L L"
    }
    print(json.dumps(status, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--match", required=True, help="Match ID")
    args = parser.parse_args()
    get_team_status(args.match)
