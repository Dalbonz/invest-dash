import requests, xml.etree.ElementTree as ET

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
                news.append({
                    'source': src['name'],
                    'category': src['category'],
                    'title': title,
                    'link': link,
                })
                cnt += 1
        except Exception as e:
            print(f'{src["name"]} 오류: {e}')
    return news

if __name__ == '__main__':
    import json
    print(json.dumps(run(), ensure_ascii=False, indent=2))
