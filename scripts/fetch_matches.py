import argparse
import json

def fetch_matches():
    # 模拟抓取今日赛事数据
    matches = [
        {"id": "1", "league": "Premier League", "home": "Arsenal", "away": "Chelsea", "time": "20:00"},
        {"id": "2", "league": "La Liga", "home": "Real Madrid", "away": "Barcelona", "time": "21:00"}
    ]
    print(json.dumps(matches, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    fetch_matches()
