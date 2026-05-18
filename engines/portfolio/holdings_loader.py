import json
import os
from typing import List
from shared.gsheet_client import read_sheet, write_sheet
from shared.models import Holding
from shared.utils import save_output
from shared.logger import get_logger

logger = get_logger("holdings_loader")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "output.json")
SHEET_NAME = "holdings"

def load_holdings() -> List[Holding]:
    rows = read_sheet(SHEET_NAME)
    holdings = []
    for r in rows:
        try:
            h = Holding(
                ticker=r["ticker"],
                name=r["name"],
                market=r["market"],
                quantity=float(r["quantity"]),
                avg_price=float(r["avg_price"]),
                asset_type=r["asset_type"],
                sector=r.get("sector", ""),
                currency=r.get("currency", "KRW"),
            )
            holdings.append(h)
        except (KeyError, ValueError) as e:
            logger.warning(f"Skip row {r}: {e}")
    return holdings

def save_holdings(holdings: List[dict]) -> bool:
    return write_sheet(SHEET_NAME, holdings)

def run() -> dict:
    holdings = load_holdings()
    data = {"holdings": [h.__dict__ for h in holdings], "count": len(holdings)}
    save_output("holdings_loader", data, OUTPUT_PATH)
    logger.info(f"Loaded {len(holdings)} holdings")
    return data

if __name__ == "__main__":
    result = run()
    print(json.dumps(result, ensure_ascii=False, indent=2))