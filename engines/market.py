import os, json, requests
from datetime import datetime

HEADERS = {'User-Agent': 'Mozilla/5.0'}

SYMBOLS = {
    'kospi': '^KS11', 'kosdaq': '^KQ11',
    'sp500': '^GSPC', 'nasdaq': '^IXIC', 'dow': '^DJI',
    'usdkrw': 'USDKRW=X', 'jpykrw': 'JPYKRW=X',
    'vix': '^VIX', 'oil': 'CL=F', 'gold': 'GC=F',
    'nvda': 'NVDA', 'aapl': 'AAPL', 'msft': 'MSFT',
    'tsla': 'TSLA', 'samsung': '005930.KS', 'hynix': '000660.KS',
}

def fetch_price(symbol):
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=2d'
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        d = r.json()['chart']['result'][0]
        meta = d['meta']
        price = meta['regularMarketPrice']
        prev = meta.get('chartPreviousClose', price)
        chg = price - prev
        pct = round(chg / prev * 100, 2) if prev else 0
        return {'price': round(price, 4), 'change': round(chg, 4), 'pct': pct}
    except:
        return None

def run():
    result = {}
    for key, sym in SYMBOLS.items():
        data = fetch_price(sym)
        if data:
            result[key] = data
            print(f'{key}: {data["price"]} ({data["pct"]}%)')
    return result

if __name__ == '__main__':
    print(json.dumps(run(), ensure_ascii=False, indent=2))