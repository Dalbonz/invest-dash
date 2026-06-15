import os, requests, xml.etree.ElementTree as ET

HEADERS = {'User-Agent': 'Mozilla/5.0'}

RSS_SOURCES = [
    {'name': '매일경제', 'url': 'https://www.mk.co.kr/rss/30100041/', 'category': '분석'},
    {'name': '한국경제', 'url': 'https://www.hankyung.com/feed/all-news', 'category': '국내'},
    {'name': '연합뉴스', 'url': 'https://www.yna.co.kr/rss/economy.xml', 'category': '국내'},
]

INVEST_KW = ['주식','증시','코스피','나스닥','금리','환율','달러','반도체','ETF','투자','Fed','연준','펀드','채권','원자재','인플레','경기','매수','매도']
EXCLUDE_KW = ['연예','드라마','스포츠','축구','야구','패션','맛집','날씨','사건','사고']

def is_invest(title):
    if any(k in title for k in EXCLUDE_KW): return False
    return any(k in title for k in INVEST_KW)

def _ai_summary(title, source):
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        return ''
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
                'max_tokens': 150,
                'temperature': 0,
                'messages': [{'role': 'user', 'content':
                    f'다음 경제 뉴스 제목을 투자자 관점에서 2문장으로 설명하세요.\n'
                    f'출처: {source}\n'
                    f'제목: {title}\n\n'
                    '형식: [배경/맥락 1문장] [투자 시사점 1문장]\n'
                    '규칙: 제목 사실만. 추측 금지. 이모지 금지.'
                }],
            },
            timeout=15,
        )
        if r.status_code == 200:
            return r.json()['content'][0]['text'].strip()
    except Exception as e:
        print(f'뉴스 AI 요약 오류 ({title[:30]}): {e}')
    return ''

def run():
    news = []
    for src in RSS_SOURCES:
        try:
            r = requests.get(src['url'], headers=HEADERS, timeout=10)
            root = ET.fromstring(r.content)
            cnt = 0
            for item in root.findall('.//item'):
                if cnt >= 4: break
                t = item.find('title')
                l = item.find('link')
                if t is None or l is None: continue
                title = (t.text or '').strip()
                link = (l.text or '').strip()
                if not title or not is_invest(title): continue
                summary = _ai_summary(title, src['name'])
                news.append({
                    'source': src['name'],
                    'category': src['category'],
                    'title': title,
                    'link': link,
                    'summary': summary,
                })
                cnt += 1
        except Exception as e:
            print(f'{src["name"]} 오류: {e}')
    return news

if __name__ == '__main__':
    import json
    print(json.dumps(run(), ensure_ascii=False, indent=2))
