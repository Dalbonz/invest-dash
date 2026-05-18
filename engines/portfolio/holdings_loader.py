import json
import os
from typing import List
from shared.gsheet_client import read_sheet
from shared.utils import save_output
from shared.logger import get_logger

logger = get_logger("holdings_loader")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "output.json")

SHEET_NAME = "주식현황상세"

def load_holdings() -> List[dict]:
    rows = read_sheet(SHEET_NAME)
    holdings = []
    for r in rows:
        # 빈 행 스킵
        if not r.get("종목명"):
            continue
        try:
            h = {
                "market": r.get("시장", ""),
                "name": r.get("종목명", ""),
                "sector": r.get("섹터", ""),
                "ticker": str(r.get("코드", "")),
                "quantity": float(r.get("보유량", 0) or 0),
                "avg_price": float(r.get("매수평단가", 0) or 0),
                "avg_price_krw": float(r.get("매수평단가(원)", 0) or 0),
                "total_cost_krw": float(r.get("매수총액(원)", 0) or 0),
                "avg_exchange_rate": float(r.get("평균환율", 0) or 0),
                "current_price": float(r.get("현재가", 0) or 0),
                "total_value_krw": float(r.get("평가총액(원)", 0) or 0),
                "total_profit_krw": float(r.get("원화수익", 0) or 0),
                "daily_profit": float(r.get("일간수익", 0) or 0),
            }
            holdings.append(h)
        except (ValueError, TypeError) as e:
            logger.warning(f"Skip row {r.get('종목명')}: {e}")
    return holdings

def run() -> dict:
    holdings = load_holdings()
    total_value = sum(h["total_value_krw"] for h in holdings)
    total_profit = sum(h["total_profit_krw"] for h in holdings)
    data = {
        "holdings": holdings,
        "count": len(holdings),
        "total_value_krw": total_value,
        "total_profit_krw": total_profit,
    }
    save_output("holdings_loader", data, OUTPUT_PATH)
    logger.info(f"Loaded {len(holdings)} holdings, total: {total_value:,.0f}원")
    return data

if __name__ == "__main__":
    result = run()
    print(json.dumps(result, ensure_ascii=False, indent=2))