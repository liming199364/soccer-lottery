import argparse
import json

def predict(match_id):
    # 模拟预测结果
    prediction = {
        "match_id": match_id,
        "win_probability": {"home": 45, "draw": 30, "away": 25},
        "score_prediction": "2-1",
        "suggestion": "Recommend Home Win, Medium Confidence"
    }
    print(json.dumps(prediction, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--match", required=True, help="Match ID")
    args = parser.parse_args()
    predict(args.match)
