import os, requests

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
CHAT_IDS = [c.strip() for c in os.environ.get('TELEGRAM_CHAT_IDS', '').split(',') if c.strip()]

DASH_URL = 'https://dalbonz.github.io/invest-dash'

def send(message):
    if not BOT_TOKEN or not CHAT_IDS:
        print('텔레그램 설정 없음 (스킵)')
        return
    for chat_id in CHAT_IDS:
        try:
            r = requests.post(
                f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                json={'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'},
                timeout=10,
            )
            if r.status_code != 200:
                print(f'텔레그램 발송 실패 ({chat_id}): {r.text[:100]}')
        except Exception as e:
            print(f'텔레그램 오류 ({chat_id}): {e}')

def morning_brief(ai_data, news_data, market_data):
    lines = ['<b>Invest Dash 아침 브리핑</b>\n']

    if ai_data and not ai_data.get('error'):
        s = ai_data.get('summary', '')
        if s:
            lines.append(f'{s}\n')

    def fmt(m):
        if not m: return '-'
        p, pct = m.get('price', 0), m.get('pct', 0)
        sign = '+' if pct >= 0 else ''
        return f'{p:,.0f} ({sign}{pct:.2f}%)'

    lines.append('[주요 지수]')
    for key, label in [('kospi','코스피'),('kosdaq','코스닥'),('sp500','S&P500'),('usdkrw','달러/원')]:
        m = market_data.get(key)
        if m:
            lines.append(f'{label}: {fmt(m)}')

    if news_data:
        lines.append('\n[뉴스]')
        for n in news_data[:3]:
            lines.append(f'• {n["title"]}')

    lines.append(f'\n{DASH_URL}')
    return '\n'.join(lines)

def yt_new_video(name, title, video_id):
    return (
        f'<b>[유튜브] {name}</b>\n'
        f'{title}\n'
        f'https://youtube.com/watch?v={video_id}'
    )
