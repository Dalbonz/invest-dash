import os, re, requests
import xml.etree.ElementTree as ET

HEADERS = {'User-Agent': 'Mozilla/5.0'}

CHANNELS = [
    {'name': '한국경제TV',      'handle': 'hkwowtv',                   'type': 'media'},
    {'name': '연합뉴스경제TV',  'handle': 'UC6kZpTl39-_SqfBrF1-N2oQ', 'type': 'media'},
    {'name': '매일경제TV',      'handle': 'MKeconomy_TV',              'type': 'media'},
    {'name': '12시에 만나요',   'handle': 'gyeomsonisnothing',          'type': 'yt'},
    {'name': '경제사냥꾼',      'handle': 'UC7usMJDHmtbs_oegmzQKKMA', 'type': 'yt'},
    {'name': '슈페tv',          'handle': 'supe-tv',                   'type': 'yt'},
]

NS = {
    'atom':  'http://www.w3.org/2005/Atom',
    'yt':    'http://www.youtube.com/xml/schemas/2015',
    'media': 'http://search.yahoo.com/mrss/',
}

def _rss_url(handle):
    if re.match(r'^UC[A-Za-z0-9_-]{22}$', handle):
        return f'https://www.youtube.com/feeds/videos.xml?channel_id={handle}'
    return f'https://www.youtube.com/feeds/videos.xml?user={handle}'

def _resolve_handle(handle):
    urls = [
        f'https://www.youtube.com/@{handle}',
        f'https://www.youtube.com/c/{handle}',
        f'https://www.youtube.com/user/{handle}',
    ]
    patterns = [
        r'"channelId"\s*:\s*"(UC[A-Za-z0-9_-]{22})"',
        r'"externalChannelId"\s*:\s*"(UC[A-Za-z0-9_-]{22})"',
        r'href="/channel/(UC[A-Za-z0-9_-]{22})"',
        r'channel/(UC[A-Za-z0-9_-]{22})',
    ]
    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
            if r.status_code != 200:
                continue
            for pat in patterns:
                m = re.search(pat, r.text)
                if m:
                    print(f'  → handle 해결: {handle} → {m.group(1)[:12]}...')
                    return m.group(1)
        except Exception:
            continue
    return None

def _parse_xml(text):
    try:
        root = ET.fromstring(text)
        entry = root.find('atom:entry', NS)
        if not entry:
            return None
        return {
            'videoId':     getattr(entry.find('yt:videoId', NS),           'text', '') or '',
            'title':       getattr(entry.find('atom:title', NS),           'text', '') or '',
            'description': (getattr(entry.find('.//media:description', NS),'text', '') or '')[:600],
            'published':   getattr(entry.find('atom:published', NS),       'text', '') or '',
        }
    except Exception:
        return None

def fetch_latest(handle):
    try:
        r = requests.get(_rss_url(handle), headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return _parse_xml(r.text)
    except Exception:
        pass

    if not re.match(r'^UC', handle):
        cid = _resolve_handle(handle)
        if cid:
            try:
                r = requests.get(
                    f'https://www.youtube.com/feeds/videos.xml?channel_id={cid}',
                    headers=HEADERS, timeout=10
                )
                if r.status_code == 200:
                    return _parse_xml(r.text)
            except Exception:
                pass
    return None

def _summarize(name, title, description):
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        return title

    has_desc = len(description.strip()) >= 50

    if has_desc:
        prompt = (
            f'채널: {name}\n'
            f'제목: {title}\n'
            f'설명: {description}\n\n'
            '위 정보만 바탕으로 투자자 관점에서 한국어로 요약하세요.\n'
            '형식:\n'
            '핵심 주제: [제목의 핵심 의미 1문장]\n'
            '주요 내용:\n'
            '1. [내용]\n'
            '2. [내용]\n'
            '3. [내용]\n'
            '주목 키워드: [종목명/섹터/지수 등]\n\n'
            '규칙: 제목과 설명에 있는 내용만 작성. 없는 내용 추가 금지.'
        )
    else:
        prompt = (
            f'채널: {name}\n'
            f'제목: {title}\n\n'
            '위 유튜브 영상 제목만을 바탕으로 투자자 관점에서 한국어로 요약하세요.\n'
            '형식:\n'
            '핵심 주제: [제목의 핵심 의미 1문장]\n'
            '주목 키워드: [제목에서 추출한 종목명/섹터/키워드]\n\n'
            '규칙: 제목에 있는 내용만 작성. 추측 금지.'
        )

    try:
        r = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json',
            },
            json={
                'model': 'claude-haiku-4-5-20251001',
                'max_tokens': 300,
                'temperature': 0,
                'messages': [{'role': 'user', 'content': prompt}],
            },
            timeout=30,
        )
        if r.status_code == 200:
            return r.json()['content'][0]['text'].strip()
    except Exception as e:
        print(f'AI 요약 오류 ({name}): {e}')
    return title

def run():
    result = []
    for ch in CHANNELS:
        print(f'YouTube: {ch["name"]} 수집 중...')
        video = fetch_latest(ch['handle'])
        if not video:
            print(f'  → 데이터 없음 (스킵)')
            continue
        summary = _summarize(ch['name'], video['title'], video['description'])
        result.append({
            'name':    ch['name'],
            'type':    ch['type'],
            'videoId': video['videoId'],
            'title':   video['title'],
            'updated': video['published'],
            'summary': summary,
        })
        print(f'  → {video["title"][:60]}')
    return result
