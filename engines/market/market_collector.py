import yfinance as yf
from shared.constants import KR_MARKET_INDEX, US_MARKET_INDEX, TIMEFRAMES
from shared.cache import get as cache_get, set as cache_set
from shared.logger import get_logger

logger = get_logger("market_collector")

def fetch_index_data(tickers: list, period_days: int) -> dict:
    cache_key = f"market_{'_'.join(tickers)}_{period_days}"
    cached = cache_get(cache_key, ttl_seconds=1800)
    if cached:
        return cached

    period = f"{period_days}d"
    result = {}
    for ticker in tickers:
        try:
            df = yf.Ticker(ticker).history(period=period)
            if df.empty:
                continue
            result[ticker] = {
                "close": df["Close"].tolist(),
                "dates": df.index.strftime("%Y-%m-%d").tolist(),
                "latest": float(df["Close"].iloc[-1]),
                "change_pct": float((df["Close"].iloc[-1] / df["Close"].iloc[0] - 1) * 100),
            }
        except Exception as e:
            logger.warning(f"{ticker} fetch failed: {e}")

    cache_set(cache_key, result)
    return result

def collect_all() -> dict:
    return {
        "kr": fetch_index_data(KR_MARKET_INDEX, TIMEFRAMES["short"]),
        "us": fetch_index_data(US_MARKET_INDEX, TIMEFRAMES["short"]),
    }