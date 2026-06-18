import os, re, requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

def _is_today_kst(published_str):
    try:
        dt = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
        return dt.astimezone(KST).date() == datetime.now(KST).date()
    except Exception:
        return True

HEADERS = {'User-Agent': 'Mozilla/5.0'}
SUPADATA_API_KEY = os.environ.get('SUPADATA_API_KEY', '')

CHANNELS = [
    {'name': '한국경제TV',      'handle': 'hkwowtv',                   'type': 'media', 'format': 'investment'},
    {'name': '연합뉴스경제TV',  'handle': 'UC6kZpTl39-_SqfBrF1-N2oQ', 'type': 'media', 'format': 'investment'},
    {'name': '매일경제TV',      'handle': 'MKeconomy_TV',              'type': 'media', 'format': 'investment'},
    {'name': '12시에 만나요',   'handle': 'gyeomsonisnothing',          'type': 'yt',    'format': 'investment'},
    {'name': '경제사냥꾼',      'handle': 'UC7usMJDHmtbs_oegmzQKKMA', 'type': 'yt',    'format': 'free'},
    {'name': '슈페tv',          'handle': 'supe-tv',                   'type': 'yt',    'format': 'free'},
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

def get_transcript(video_id):
    if not SUPADATA_API_KEY or not video_id:
        return None
    video_url = requests.utils.quote(f'https://www.youtube.com/watch?v={video_id}', safe='')
    url = f'https://api.supadata.ai/v1/youtube/transcript?url={video_url}&text=true&lang=ko'
    try:
        r = requests.get(url, headers={'x-api-key': SUPADATA_API_KEY}, timeout=20)
        if r.status_code != 200:
            return None
        data = r.json()
        content = data.get('content')
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return ' '.join(i.get('text', '') for i in content)
    except Exception as e:
        print(f'  자막 조회 오류: {e}')
    return None

COMMON_RULES = (
    '당신은 최고의 투자 분석가입니다.\n'
    '아래는 [{name}] 채널의 한국어 유튜브 자막입니다.\n'
    '광고/홍보 구간은 무시하세요.\n\n'
    '규칙:\n'
    '- 한국어로만 작성\n'
    '- 이모지/마크다운 금지\n'
    '- 섹션 헤더는 [ 섹션명 ] 형식\n'
    "- 항목은 '- '로 시작\n\n"
)

FORMAT_INVESTMENT = (
    '[ 핵심 메시지 ]\n\n- 핵심 포인트 (최대 3개)\n\n'
    '[ 주목 섹터/종목 ]\n\n- 종목/섹터 - 이유 (최대 3개)\n\n'
    '[ 매수 시그널 ]\n\n- 조건 또는 타이밍\n\n'
    '[ 매도/주의 ]\n\n- 리스크 요인\n\n'
    '[ 오늘 액션 ]\n\n- 행동 지침 (최대 4개)'
)
FORMAT_FREE = (
    '[ 핵심 요약 ]\n\n- 핵심 포인트 (최대 3개)\n\n'
    '[ 주요 내용 ]\n\n- 세부 포인트 (최대 4개)'
)

def _summarize_transcript(name, transcript, fmt):
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        return None
    trimmed = transcript.strip()[:6000]
    instructions = COMMON_RULES.format(name=name) + (FORMAT_INVESTMENT if fmt == 'investment' else FORMAT_FREE)
    prompt = instructions + '\n\n[자막]\n' + trimmed
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
                'max_tokens': 1200,
                'temperature': 0,
                'messages': [{'role': 'user', 'content': prompt}],
            },
            timeout=40,
        )
        if r.status_code == 200:
            return r.json()['content'][0]['text'].strip()
    except Exception as e:
        print(f'  AI 요약 오류 ({name}): {e}')
    return None

def _summarize_title_only(name, title):
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        return title
    prompt = (
        f'채널: {name}\n제목: {title}\n\n'
        '위 유튜브 영상 제목만을 바탕으로 투자자 관점에서 한국어로 핵심 주제 1문장과 주목 키워드를 요약하세요.\n'
        '제목에 없는 내용은 추측하지 마세요.'
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
                'max_tokens': 200,
                'temperature': 0,
                'messages': [{'role': 'user', 'content': prompt}],
            },
            timeout=30,
        )
        if r.status_code == 200:
            return r.json()['content'][0]['text'].strip()
    except Exception as e:
        print(f'  AI 요약 오류 ({name}): {e}')
    return title

def run(yt_only=False, existing=None):
    existing = existing or {}
    channels = [ch for ch in CHANNELS if ch['type'] == 'yt'] if yt_only else CHANNELS
    result = []
    for ch in channels:
        print(f'YouTube: {ch["name"]} 수집 중...')
        video = fetch_latest(ch['handle'])
        if not video:
            print('  → 데이터 없음 (스킵)')
            continue
        if ch['type'] == 'yt' and not _is_today_kst(video.get('published', '')):
            print('  → 오늘 영상 없음 (스킵)')
            continue

        prev = existing.get(ch['name'])
        if prev and prev.get('videoId') == video['videoId'] and prev.get('summary'):
            print('  → 기존과 동일한 영상 (자막 재호출 스킵, 기존 요약 재사용)')
            result.append({
                'name':    ch['name'],
                'type':    ch['type'],
                'videoId': video['videoId'],
                'title':   video['title'],
                'updated': video['published'],
                'summary': prev['summary'],
            })
            continue

        transcript = get_transcript(video['videoId']) if video['videoId'] else None
        if transcript and len(transcript.strip()) >= 200:
            summary = _summarize_transcript(ch['name'], transcript, ch.get('format', 'free')) or video['title']
            print('  → 자막 기반 요약')
        else:
            summary = _summarize_title_only(ch['name'], video['title'])
            print('  → 자막 없음, 제목 기반 요약')

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
