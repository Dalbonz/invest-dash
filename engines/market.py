import os, json, requests
from datetime import datetime

HEADERS = {'User-Agent': 'Mozilla/5.0'}

SYMBOLS = {
    # 국내 지수
    'kospi':   '^KS11',
    'kosdaq':  '^KQ11',
    # 미국 지수
    'sp500':   '^GSPC',
    'nasdaq':  '^IXIC',
    'dow':     '^DJI',
    'ndx':     '^NDX',
    # 환율
    'usdkrw':  'USDKRW=X',
    'jpykrw':  'JPYKRW=X',
    'eurkrw':  'EURKRW=X',
    'usdjpy':  'JPY=X',
    'eurusd':  'EURUSD=X',
    'dxy':     'DX-Y.NYB',
    # 원자재
    'oil':     'CL=F',
    'brent':   'BZ=F',
    'gold':    'GC=F',
    'silver':  'SI=F',
    # 채권
    'us10y':   '^TNX',
    'us30y':   '^TYX',
    # 미국 주요주
    'nvda':    'NVDA',
    'aapl':    'AAPL',
    'msft':    'MSFT',
    'tsla':    'TSLA',
    'googl':   'GOOGL',
    # ETF
    'spy':     'SPY',
    'qqq':     'QQQ',
    'tlt':     'TLT',
    'gld':     'GLD',
    'eem':     'EEM',
    'xle':     'XLE',
    # 국내 주요주
    'samsung': '005930.KS',
    'hynix':   '000660.KS',
}

def fetch_price(symbol):
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d'
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        d = r.json()['chart']['result'][0]
        meta = d['meta']
        price = meta['regularMarketPrice']
        prev = meta.get('chartPreviousClose', price)
        chg = price - prev
        pct = round(chg / prev * 100, 2) if prev else 0

        candles = []
        ts = d.get('timestamp', [])
        q = d.get('indicators', {}).get('quote', [{}])[0]
        opens = q.get('open', [])
        highs = q.get('high', [])
        lows = q.get('low', [])
        closes = q.get('close', [])
        vols = q.get('volume', [])
        for i in range(len(ts)):
            if i >= len(closes) or closes[i] is None:
                continue
            candles.append({
                'time': ts[i],
                'open': round(opens[i] or 0, 4),
                'high': round(highs[i] or 0, 4),
                'low':  round(lows[i] or 0, 4),
                'close': round(closes[i] or 0, 4),
                'vol':  int(vols[i] or 0) if i < len(vols) else 0,
            })

        return {
            'price':  round(price, 4),
            'change': round(chg, 4),
            'pct':    pct,
            'high':   round(meta.get('regularMarketDayHigh', price), 4),
            'low':    round(meta.get('regularMarketDayLow', price), 4),
            'vol':    int(meta.get('regularMarketVolume', 0)),
            'candles': candles[-5:],
        }
    except Exception as e:
        print(f'{symbol} 오류: {e}')
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