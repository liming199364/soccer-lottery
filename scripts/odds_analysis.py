import argparse
import json

def analyze_odds(match_id):
    # 模拟赔率数据
    odds = {
        "match_id": match_id,
        "william_hill": {"home": 2.10, "draw": 3.40, "away": 3.20},
        "bet365": {"home": 2.15, "draw": 3.30, "away": 3.10}
    }
    print(json.dumps(odds, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--match", required=True, help="Match ID")
    args = parser.parse_args()
    analyze_odds(args.match)
