import os, json, requests
from datetime import datetime, timedelta

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
    # 변동성/달러
    'vix':     '^VIX',
    'dxy':     'DX-Y.NYB',
    # 환율
    'usdkrw':  'USDKRW=X',
    'jpykrw':  'JPYKRW=X',
    'eurkrw':  'EURKRW=X',
    'gbpkrw':  'GBPKRW=X',
    'cnykrw':  'CNYKRW=X',
    # 원자재
    'oil':     'CL=F',
    'brent':   'BZ=F',
    'gold':    'GC=F',
    'silver':  'SI=F',
    'natgas':  'NG=F',
    'copper':  'HG=F',
    # 채권
    'us10y':   '^TNX',
    'us30y':   '^TYX',
    # 미국 주요주
    'nvda':    'NVDA',
    'aapl':    'AAPL',
    'msft':    'MSFT',
    'tsla':    'TSLA',
    'googl':   'GOOGL',
    'meta':    'META',
    # ETF
    'spy':     'SPY',
    'qqq':     'QQQ',
    'tlt':     'TLT',
    'gld':     'GLD',
    'eem':     'EEM',
    'xle':     'XLE',
    # 국내 주요주
    'samsung':    '005930.KS',
    'hynix':      '000660.KS',
    'hanwha':     '012450.KS',
    'lignex':     '079550.KS',
    'rainbow':    '277810.KQ',
    'doosanrobo': '454910.KS',
    'samsungbio': '207940.KS',
    'celltrion':  '068270.KS',
}

# KR 주식 코드 매핑 (시장 key → KRX 6자리)
KR_CODES = {
    'samsung':    '005930',
    'hynix':      '000660',
    'hanwha':     '012450',
    'lignex':     '079550',
    'rainbow':    '277810',
    'doosanrobo': '454910',
    'samsungbio': '207940',
    'celltrion':  '068270',
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
                'time':  ts[i],
                'open':  round(opens[i] or 0, 4),
                'high':  round(highs[i] or 0, 4),
                'low':   round(lows[i] or 0, 4),
                'close': round(closes[i] or 0, 4),
                'vol':   int(vols[i] or 0) if i < len(vols) else 0,
            })

        return {
            'price':   round(price, 4),
            'change':  round(chg, 4),
            'pct':     pct,
            'high':    round(meta.get('regularMarketDayHigh', price), 4),
            'low':     round(meta.get('regularMarketDayLow', price), 4),
            'vol':     int(meta.get('regularMarketVolume', 0)),
            'candles': candles[-5:],
        }
    except Exception as e:
        print(f'{symbol} 오류: {e}')
        return None

def fetch_investor(krx_code):
    """pykrx로 당일 투자자별 순매수금액(억원) 조회"""
    try:
        from pykrx import stock as krx
        today = datetime.now().strftime('%Y%m%d')
        # 주말/공휴일 대비: 오늘 → 전날 순으로 시도
        for delta in [0, 1, 2, 3]:
            d = (datetime.now() - timedelta(days=delta)).strftime('%Y%m%d')
            try:
                df = krx.get_market_trading_value_by_investor(d, d, krx_code)
                if df is not None and not df.empty and '순매수거래대금' in df.columns:
                    def get_val(keys):
                        for k in keys:
                            if k in df.index:
                                return int(df.loc[k, '순매수거래대금'] / 1e8)
                        return 0
                    return {
                        'ind': get_val(['개인']),
                        'ins': get_val(['기관합계', '기관']),
                        'for': get_val(['외국인합계', '외국인']),
                    }
            except Exception:
                continue
        return None
    except ImportError:
        return None
    except Exception as e:
        print(f'투자자 데이터 오류 ({krx_code}): {e}')
        return None

def run():
    result = {}
    for key, sym in SYMBOLS.items():
        data = fetch_price(sym)
        if data:
            result[key] = data
            print(f'{key}: {data["price"]} ({data["pct"]}%)')

    # KR 주식 투자자별 순매수 데이터
    print('투자자 동향 수집 중...')
    investors = {}
    for key, code in KR_CODES.items():
        inv = fetch_investor(code)
        if inv:
            investors[code] = inv
            print(f'  {key}({code}): 기관{inv["ins"]:+d}억 외국인{inv["for"]:+d}억 개인{inv["ind"]:+d}억')
        else:
            print(f'  {key}({code}): 투자자 데이터 없음')
    if investors:
        result['investors'] = investors

    return result

if __name__ == '__main__':
    print(json.dumps(run(), ensure_ascii=False, indent=2))
