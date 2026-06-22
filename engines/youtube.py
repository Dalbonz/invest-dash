import os, re, time, requests
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

# summaryMode: 'full'(자막분석+AI요약, 비용 높음) / 'title'(제목만 AI요약, 자막조회 안함 - 비용 최소화)
# fullKeywords: summaryMode가 'title'이어도 제목에 이 키워드가 있으면 그 영상만 'full'로 승격
# (예: 한국경제TV는 하루 수백개라 기본 제목요약이지만, 아침방송 "당신이 잠든사이"는 중요해서 전체분석)
# → 채널을 새로 추가/수정할 때는 "하루에 몇 개 올라오는지 + summaryMode를 뭘로 할지"를 같이 정해야 함
CHANNELS = [
    {'name': '한국경제TV',      'handle': 'hkwowtv',                   'type': 'media', 'format': 'investment', 'summaryMode': 'title', 'fullKeywords': ['당신이 잠든사이']},
    {'name': '연합뉴스경제TV',  'handle': 'UC6kZpTl39-_SqfBrF1-N2oQ', 'type': 'media', 'format': 'investment', 'summaryMode': 'title'},
    {'name': '매일경제TV',      'handle': 'MKeconomy_TV',              'type': 'media', 'format': 'investment', 'summaryMode': 'title'},
    {'name': '12시에 만나요',   'handle': 'gyeomsonisnothing',          'type': 'yt',    'format': 'investment', 'titleKeyword': '12시에 만나요', 'summaryMode': 'full'},
    {'name': '경제사냥꾼',      'handle': 'UC7usMJDHmtbs_oegmzQKKMA', 'type': 'yt',    'format': 'free', 'summaryMode': 'full'},
    {'name': '슈페tv',          'handle': 'supe-tv',                   'type': 'yt',    'format': 'free', 'summaryMode': 'full'},
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

def _entry_to_dict(entry):
    return {
        'videoId':     getattr(entry.find('yt:videoId', NS),           'text', '') or '',
        'title':       getattr(entry.find('atom:title', NS),           'text', '') or '',
        'description': (getattr(entry.find('.//media:description', NS),'text', '') or '')[:600],
        'published':   getattr(entry.find('atom:published', NS),       'text', '') or '',
    }

class _NoMatch(Exception):
    """RSS는 정상 파싱됐지만 title_keyword에 맞는 entry가 없음 (재시도 불필요)"""

def _parse_xml_all(text, title_keyword=None):
    """오늘(KST) 발행된 entry를 전부 반환 (채널당 1개만 보던 기존 동작 대체)"""
    root = ET.fromstring(text)  # 차단 페이지(HTML)면 여기서 ParseError -> 재시도 대상
    entries = root.findall('atom:entry', NS)
    if not entries:
        raise _NoMatch()
    videos = []
    for entry in entries:
        title = getattr(entry.find('atom:title', NS), 'text', '') or ''
        if title_keyword and title_keyword not in title:
            continue
        v = _entry_to_dict(entry)
        if _is_today_kst(v.get('published', '')):
            videos.append(v)
    if not videos:
        raise _NoMatch()
    return videos

def _fetch_rss_all(url, title_keyword=None, retries=1):
    last_err = None
    for i in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
        except Exception as e:
            last_err = str(e)
            if i < retries - 1:
                time.sleep(2)
            continue
        if r.status_code != 200:
            last_err = f'status_{r.status_code}'  # 일시적 차단/지연일 수 있어 재시도 대상
            if i < retries - 1:
                time.sleep(2)
            continue
        try:
            return _parse_xml_all(r.text, title_keyword)
        except _NoMatch:
            return []
        except Exception as e:
            last_err = str(e)  # XML 파싱 실패 = 봇차단 페이지(HTML) 추정, 재시도
            if i < retries - 1:
                time.sleep(2)
    if last_err and retries > 1:
        print(f'  RSS 조회 실패(차단/오류 추정, {retries}회 시도): {last_err}')
    return []

def fetch_today(handle, title_keyword=None):
    """오늘(KST) 올라온 영상 전체 리스트 반환 (채널당 여러 개 가능)"""
    # 1차: ?user= 형식 (handle이 채널ID가 아니면 보통 404 - 재시도 불필요)
    videos = _fetch_rss_all(_rss_url(handle), title_keyword, retries=1)
    if videos:
        return videos

    if not re.match(r'^UC', handle):
        cid = _resolve_handle(handle)
        if cid:
            # 2차: 실제 channel_id URL - 일시적 차단/오류 대비 재시도
            return _fetch_rss_all(f'https://www.youtube.com/feeds/videos.xml?channel_id={cid}', title_keyword, retries=3)
    return []

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
    """
    existing: {videoId: 기존 영상 dict} — 호출 측(run.py)에서 '오늘(KST) 영상만' 미리 걸러서 넘겨줌.
    반환값: 오늘 올라온 영상 전체 리스트(채널당 여러 개 가능). 기존에 있던 videoId는 isNew=False로
    요약을 재사용하고, 새로 발견된 videoId만 자막조회/AI요약을 새로 수행해 isNew=True로 표시.
    """
    existing = existing or {}
    channels = [ch for ch in CHANNELS if ch['type'] == 'yt'] if yt_only else CHANNELS
    result = []
    for ch in channels:
        print(f'YouTube: {ch["name"]} 수집 중...')
        videos = fetch_today(ch['handle'], ch.get('titleKeyword'))
        if not videos:
            print('  → 오늘 영상 없음/조회 실패 (스킵)' + (f" - '{ch['titleKeyword']}' 포함 영상 못 찾음" if ch.get('titleKeyword') else ''))
            continue

        for video in videos:
            prev = existing.get(video['videoId'])
            if prev and prev.get('summary'):
                print(f'  → 기존 영상(요약 재사용): {video["title"][:40]}')
                result.append({**prev, 'name': ch['name'], 'type': ch['type'],
                               'videoId': video['videoId'], 'title': video['title'],
                               'updated': video['published'], 'isNew': False})
                continue

            mode = ch.get('summaryMode', 'full')
            if mode == 'title' and any(kw in video['title'] for kw in ch.get('fullKeywords', [])):
                mode = 'full'  # 채널 기본은 제목요약이지만 중요 코너는 전체분석으로 승격

            if mode == 'full':
                transcript = get_transcript(video['videoId']) if video['videoId'] else None
                if transcript and len(transcript.strip()) >= 200:
                    summary = _summarize_transcript(ch['name'], transcript, ch.get('format', 'free')) or video['title']
                    print('  → 자막 기반 요약')
                else:
                    summary = _summarize_title_only(ch['name'], video['title'])
                    print('  → 자막 없음, 제목 기반 요약')
            else:
                summary = _summarize_title_only(ch['name'], video['title'])
                print('  → 제목 기반 요약(비용 절감 모드)')

            result.append({
                'name':    ch['name'],
                'type':    ch['type'],
                'videoId': video['videoId'],
                'title':   video['title'],
                'updated': video['published'],
                'summary': summary,
                'isNew':   True,
            })
            print(f'  → {video["title"][:60]}')
    return result
