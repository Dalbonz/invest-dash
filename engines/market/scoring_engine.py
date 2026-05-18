from shared.utils import safe_divide

def score_momentum(change_pct: float) -> int:
    if change_pct >= 5:   return 90
    if change_pct >= 2:   return 70
    if change_pct >= 0:   return 55
    if change_pct >= -2:  return 40
    if change_pct >= -5:  return 25
    return 10

def score_market(market_data: dict) -> dict:
    scores = {}
    for region, tickers in market_data.items():
        region_scores = []
        for ticker, data in tickers.items():
            s = score_momentum(data.get("change_pct", 0))
            region_scores.append(s)
        scores[region] = int(sum(region_scores) / len(region_scores)) if region_scores else 50
    scores["overall"] = int(sum(scores.values()) / len(scores)) if scores else 50
    return scores