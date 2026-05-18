import json
import os
from engines.market.market_collector import collect_all
from engines.market.scoring_engine import score_market
from shared.utils import save_output
from shared.logger import get_logger

logger = get_logger("risk_detector")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "output.json")

def detect_risk(scores: dict) -> int:
    overall = scores.get("overall", 50)
    if overall >= 70: return 1
    if overall >= 55: return 2
    if overall >= 40: return 3
    if overall >= 25: return 4
    return 5

def run() -> dict:
    raw = collect_all()
    scores = score_market(raw)
    risk = detect_risk(scores)
    data = {
        "scores": scores,
        "risk_level": risk,
        "raw_summary": {
            region: {t: d.get("latest", 0) for t, d in tickers.items()}
            for region, tickers in raw.items()
        }
    }
    save_output("market", data, OUTPUT_PATH)
    logger.info(f"Market scored: {scores}, risk: {risk}")
    return data

if __name__ == "__main__":
    result = run()
    print(json.dumps(result, ensure_ascii=False, indent=2))