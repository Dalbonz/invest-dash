"""
메인 실행 파일 - GitHub Actions에서 실행
GITHUB_SCHEDULE 환경변수로 실행 모드 결정:
  yt      : 개인채널 유튜브만 체크 → 새 영상 있으면 텔레그램 발송
  morning : 전체 실행 + 텔레그램 아침 브리핑 (KST 08:22, 장 시작 전)
  email   : 전체 실행 + 이메일 발송 (KST 15:07, 12시에 만나요 처리 후)
  full    : 전체 실행 (알림 없음)

신규 유튜브 영상 알림은 모든 모드에서 공통으로 체크되며,
무음시간(22:00~07:00 KST)에는 텔레그램 발송을 보류한다 (data.json은 갱신됨).
"""
import json, os
from datetime import datetime
from engines import market, news, portfolio, ai_summary, youtube

YT_SCHEDULES = {'5 22 * * *', '8 23 * * *', '12 1 * * *'}
MORNING_SCHEDULE = '22 23 * * *'
EMAIL_SCHEDULE = '7 6 * * *'

def get_mode():
    s = os.environ.get('GITHUB_SCHEDULE', '')
    if s in YT_SCHEDULES:
        return 'yt'
    if s == MORNING_SCHEDULE:
        return 'morning'
    if s == EMAIL_SCHEDULE:
        return 'email'
    return 'full'

def load_existing():
    try:
        with open('data.json', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def notify_new_videos(videos, existing_yt):
    from engines import notify
    if os.environ.get('GITHUB_EVENT_NAME', '') == 'workflow_dispatch':
        print('  수동 실행(workflow_dispatch) - 신규영상 알림 보류 (data.json만 갱신)')
        return
    if notify.in_quiet_hours():
        print('  무음시간(22~07시) - 신규영상 알림 보류 (data.json만 갱신)')
        return
    for v in videos:
        old = existing_yt.get(v['name'])
        if old and old.get('videoId') == v.get('videoId'):
            continue
        notify.send(notify.yt_new_video(v['name'], v['title'], v['videoId'], v.get('summary', '')))
        print(f'  → 텔레그램 발송: {v["name"]}')

def run_yt_only():
    existing = load_existing()
    existing_yt = {v['name']: v for v in (existing.get('youtube') or [])}

    print('유튜브 개인채널 체크...')
    new_videos = youtube.run(yt_only=True, existing=existing_yt)
    notify_new_videos(new_videos, existing_yt)

    changed = any(existing_yt.get(v['name'], {}).get('videoId') != v.get('videoId') for v in new_videos)
    if changed:
        merged = {**existing_yt, **{v['name']: v for v in new_videos}}
        existing['youtube'] = list(merged.values())
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        print('data.json youtube 갱신')
    else:
        print('새 영상 없음 - data.json 유지')

def run_full(send_morning=False, send_email=False):
    print('1. 시장 데이터 수집...')
    market_data = market.run()

    print('2. 뉴스 수집...')
    news_data = news.run()

    print('3. 포트폴리오 로드...')
    portfolio_data = portfolio.run()

    print('4. AI 요약 생성...')
    ai_data = ai_summary.run(market_data, portfolio_data)

    print('5. 유튜브 채널 수집...')
    existing = load_existing()
    existing_yt = {v['name']: v for v in (existing.get('youtube') or [])}
    youtube_data = youtube.run(existing=existing_yt)
    notify_new_videos(youtube_data, existing_yt)

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

    if send_email:
        from engines import notify
        notify.send_email(ai_data, news_data, market_data, youtube_data)

def main():
    mode = get_mode()
    print(f'=== invest-dash 실행 (mode={mode}) ===')

    if mode == 'yt':
        run_yt_only()
    elif mode == 'morning':
        run_full(send_morning=True)
    elif mode == 'email':
        run_full(send_email=True)
    else:
        run_full()

if __name__ == '__main__':
    main()
