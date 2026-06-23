import os, re, smtplib, requests
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
CHAT_IDS = [c.strip() for c in os.environ.get('TELEGRAM_CHAT_IDS', '').split(',') if c.strip()]
GMAIL_USER = os.environ.get('GMAIL_USER', '')
GMAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD', '')
EMAIL_RECIPIENTS = [e.strip() for e in os.environ.get('EMAIL_RECIPIENTS', '').split(',') if e.strip()]

DASH_URL = 'https://dalbonz.github.io/invest-dash'
KST = timezone(timedelta(hours=9))

def in_quiet_hours():
    h = datetime.now(KST).hour
    return h >= 22 or h < 7

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
    today = datetime.now(KST).strftime('%Y년 %m월 %d일')
    lines = [f'<b>{today} B&K 투자리포트</b>\n']

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

def yt_new_video(name, title, video_id, summary=''):
    lines = [
        f'<b>[유튜브] {name}</b>',
        title,
        f'https://youtube.com/watch?v={video_id}',
    ]
    if summary:
        lines.append('')
        lines.append(summary)
    return '\n'.join(lines)

def yt_media_digest(videos):
    """미디어채널(한국경제TV 등)의 신규 영상을 채널별로 묶어 한 건의 다이제스트로 발송"""
    lines = [f'<b>[유튜브] 미디어 신규영상 {len(videos)}건</b>\n']
    by_channel = {}
    for v in videos:
        by_channel.setdefault(v['name'], []).append(v)
    for name, vids in by_channel.items():
        lines.append(f'<b>{name}</b> ({len(vids)}건)')
        for v in vids:
            lines.append(f"• {v['title']}")
        lines.append('')
    return '\n'.join(lines).strip()

def _color_nums(text):
    def repl(m):
        s = m.group(0)
        color = '#c84a31' if s.startswith('+') else '#1261c4'
        return f'<span style="color:{color};font-weight:600">{s}</span>'
    return re.sub(r'[+-]\d+(?:\.\d+)?%?', repl, text)

def _md_bold(text):
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

def _fmt_ai_section(text):
    if not text:
        return ''
    out = []
    for line in text.split('\n'):
        t = line.strip()
        if not t:
            continue
        t = _color_nums(_md_bold(t))
        if re.match(r'^\d+\.', t):
            out.append(f'<div style="margin:5px 0 5px 16px;line-height:1.6">{t}</div>')
        else:
            out.append(f'<div style="font-weight:700;color:#1a73e8;margin-top:10px">{t}</div>')
    return ''.join(out)

def _fmt_yt_section(text):
    if not text:
        return ''
    out = []
    for line in text.split('\n'):
        t = line.strip()
        if not t:
            continue
        m = re.match(r'^\[\s*(.+?)\s*\]$', t)
        if m:
            out.append(f'<div style="font-weight:700;border-left:3px solid #1a73e8;padding-left:8px;margin-top:10px">{m.group(1)}</div>')
        else:
            body = _color_nums(re.sub(r'^-\s*', '', t))
            out.append(f'<div style="margin:4px 0 4px 12px;line-height:1.6">{body}</div>')
    return ''.join(out)

def _fmt_row(m):
    p, pct = m.get('price', 0), m.get('pct', 0)
    color = '#c84a31' if pct >= 0 else '#1261c4'
    sign = '+' if pct >= 0 else ''
    return f'<td style="padding:6px">{p:,.2f}</td><td style="padding:6px;color:{color}">{sign}{pct:.2f}%</td>'

def send_email(ai_data, news_data, market_data, youtube_data):
    if not GMAIL_USER or not GMAIL_PASSWORD or not EMAIL_RECIPIENTS:
        print('이메일 설정 없음 (스킵)')
        return

    today = datetime.now(KST).strftime('%Y년 %m월 %d일')

    ai_html = ''
    if ai_data and not ai_data.get('error'):
        labels = [
            ('summary', '오늘 한줄 요약'), ('kr', '한국 시장'), ('us', '미국 시장'),
            ('sectors', '주목 섹터'), ('holdings', '내 보유종목'),
            ('picks', '관심 분야'), ('do', '오늘 할 것'), ('dont', '오늘 하지 말 것'),
        ]
        for key, label in labels:
            text = ai_data.get(key, '')
            if not text:
                continue
            text_html = _fmt_ai_section(text)
            ai_html += f'<div style="margin-bottom:16px"><div style="font-size:13px;font-weight:800;color:#888;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px">{label}</div>{text_html}</div>'
    else:
        ai_html = '<div>AI 시황 데이터 없음</div>'

    rows = ''
    for k, label in [('kospi','코스피'),('kosdaq','코스닥'),('nasdaq','나스닥'),('sp500','S&P500'),('usdkrw','달러/원'),('oil','WTI유가'),('gold','금')]:
        m = market_data.get(k)
        if m:
            rows += f'<tr><td style="padding:6px">{label}</td>{_fmt_row(m)}</tr>'

    news_html = ''
    cur = ''
    for n in news_data[:12]:
        if n['source'] != cur:
            cur = n['source']
            news_html += f'<h4 style="color:#1a73e8;margin-top:14px">{cur}</h4>'
        news_html += f'<div style="margin-bottom:8px"><b>{n["title"]}</b><br><a href="{n["link"]}" style="color:#1a73e8;font-size:0.9em">기사 보기 →</a></div>'

    yt_html = ''
    for ch in youtube_data:
        summary_html = _fmt_yt_section(ch.get('summary') or '')
        yt_html += (
            f'<div style="margin-bottom:14px;padding:12px;background:#f9f9f9;border-radius:8px">'
            f'<div style="font-weight:700">{ch["name"]}</div>'
            f'<div style="color:#555;font-size:0.92em;margin-bottom:4px">{ch.get("title","")}</div>'
            f'<div style="font-size:0.92em">{summary_html}</div>'
            f'</div>'
        )

    html = (
        '<html><body style="font-family:Arial;max-width:680px;margin:0 auto;padding:20px;color:#222">'
        f'<h2 style="border-bottom:2px solid #1a73e8;padding-bottom:8px">{today} 투자브리핑</h2>'
        '<div style="background:#f0f7ff;padding:15px;border-radius:10px;margin:16px 0;line-height:1.8">'
        f'<b>AI 시황 분석</b><br><br>{ai_html}'
        '</div>'
        '<h3>주요 시장</h3>'
        '<table style="width:100%;border-collapse:collapse;font-size:14px;border:1px solid #eee">'
        '<tr style="background:#f8fafc"><th style="padding:6px;text-align:left">지수</th><th style="padding:6px;text-align:left">현재가</th><th style="padding:6px;text-align:left">등락률</th></tr>'
        f'{rows}</table><br>'
        f'<a href="{DASH_URL}" style="background:#1a73e8;color:white;padding:10px 20px;border-radius:8px;text-decoration:none;display:inline-block">대시보드 바로가기</a>'
        f'<h3 style="margin-top:24px">유튜브 요약</h3>{yt_html}'
        f'<h3 style="margin-top:24px">주요 뉴스</h3>{news_html}'
        '</body></html>'
    )

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'{today} 투자브리핑'
    msg['From'] = GMAIL_USER
    msg['To'] = ', '.join(EMAIL_RECIPIENTS)
    msg.attach(MIMEText(html, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(GMAIL_USER, GMAIL_PASSWORD)
            s.send_message(msg)
        print('이메일 발송 완료')
    except Exception as e:
        print(f'이메일 발송 오류: {e}')
