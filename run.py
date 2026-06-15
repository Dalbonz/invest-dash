"""
메인 실행 파일 - GitHub Actions에서 실행
GITHUB_SCHEDULE 환경변수로 실행 모드 결정:
  yt      : 개인채널 유튜브만 체크 → 새 영상 있으면 텔레그램 발송
  morning : 전체 실행 + 텔레그램 아침 브리핑
  full    : 전체 실행 (알림 없음)
"""
import json, os
from datetime import datetime
from engines import market, news, portfolio, ai_summary, youtube

YT_SCHEDULES = {'0 21 * * *', '0 23 * * *', '0 1 * * *'}
MORNING_SCHEDULE = '30 23 * * *'

def get_mode():
    s = os.environ.get('GITHUB_SCHEDULE', '')
    if s in YT_SCHEDULES:
        return 'yt'
    if s == MORNING_SCHEDULE:
        return 'morning'
    return 'full'

def load_existing():
    try:
        with open('data.json', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def run_yt_only():
    from engines import notify
    existing = load_existing()
    existing_yt = {v['name']: v for v in (existing.get('youtube') or [])}

    print('유튜브 개인채널 체크...')
    new_videos = youtube.run(yt_only=True)

    notified = False
    for v in new_videos:
        old = existing_yt.get(v['name'])
        if old and old.get('videoId') == v.get('videoId'):
            print(f'  {v["name"]}: 기존 영상 (스킵)')
            continue
        notify.send(notify.yt_new_video(v['name'], v['title'], v['videoId']))
        print(f'  → 텔레그램 발송: {v["name"]}')
        existing_yt[v['name']] = v
        notified = True

    if notified:
        existing['youtube'] = list(existing_yt.values())
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        print('data.json youtube 갱신')
    else:
        print('새 영상 없음 - data.json 유지')

def run_full(send_morning=False):
    print('1. 시장 데이터 수집...')
    market_data = market.run()

    print('2. 뉴스 수집...')
    news_data = news.run()

    print('3. 포트폴리오 로드...')
    portfolio_data = portfolio.run()

    print('4. AI 요약 생성...')
    ai_data = ai_summary.run(market_data, portfolio_data)

    print('5. 유튜브 채널 수집...')
    youtube_data = youtube.run()

    data = {
        'updated': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'market': market_data,
        'news': news_data,
        'portfolio': portfolio_data,
        'ai': ai_data,
        'youtube': youtube_data,
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print('=== data.json 생성 완료 ===')

    if send_morning:
        from engines import notify
        msg = notify.morning_brief(ai_data, news_data, market_data)
        notify.send(msg)
        print('텔레그램 아침 브리핑 발송 완료')

def main():
    mode = get_mode()
    print(f'=== invest-dash 실행 (mode={mode}) ===')

    if mode == 'yt':
        run_yt_only()
    elif mode == 'morning':
        run_full(send_morning=True)
    else:
        run_full(send_morning=False)

if __name__ == '__main__':
    main()
