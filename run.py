"""
메인 실행 파일 - GitHub Actions에서 실행
실행 모드는 SLOT 환경변수로 결정 (외부 cron 서비스가 workflow_dispatch 호출시 inputs.slot으로 전달):
  yt      : 개인채널 유튜브만 체크 → 새 영상 있으면 텔레그램 발송
  morning : 전체 실행 + 텔레그램 아침 브리핑 (KST 08:22, 장 시작 전)
  email   : 전체 실행 + 이메일 발송 (KST 15:07, 12시에 만나요 처리 후)
  full    : 전체 실행 (알림 없음)
  market  : 시세만 가볍게 갱신 (장중 추가호출용, 알림 없음, 뉴스/포트폴리오/AI/유튜브는 그대로 유지)

SLOT이 없으면 GITHUB_SCHEDULE(진짜 GitHub schedule: 트리거, 지연될 수 있음)로 폴백,
둘 다 없으면 사람이 그냥 "Run workflow" 누른 테스트 실행으로 간주 (알림 보류).

신규 유튜브 영상 알림은 모든 모드에서 공통으로 체크되며,
무음시간(22:00~07:00 KST)에는 텔레그램 발송을 보류한다 (data.json은 갱신됨).
"""
import json, os
from datetime import datetime, timezone, timedelta
from engines import market, news, portfolio, ai_summary, youtube

KST = timezone(timedelta(hours=9))

def _is_today_kst(iso_str):
    try:
        dt = datetime.fromisoformat((iso_str or '').replace('Z', '+00:00'))
        return dt.astimezone(KST).date() == datetime.now(KST).date()
    except Exception:
        return False

def _today_videos_by_id(youtube_list):
    """data.json에 저장된 기존 유튜브 리스트 중 오늘(KST) 영상만 골라 videoId로 매핑(자정 지나면 자동 리셋)"""
    return {v['videoId']: v for v in (youtube_list or []) if v.get('videoId') and _is_today_kst(v.get('updated'))}

def _merge_today(existing_today, fetched):
    """이번 실행에서 못 가져온(차단 등) 채널의 오늘 영상은 그대로 유지, 새로 가져온 건 갱신"""
    fetched_ids = {v['videoId'] for v in fetched}
    carried = [v for vid, v in existing_today.items() if vid not in fetched_ids]
    return carried + fetched

SLOT_TO_MODE = {'yt1': 'yt', 'yt2': 'yt', 'yt3': 'yt', 'morning': 'morning', 'afternoon': 'afternoon', 'email': 'email', 'full': 'full', 'market': 'market'}
YT_SCHEDULES = {'5 22 * * *', '8 23 * * *', '12 1 * * *'}
MORNING_SCHEDULE = '22 23 * * *'
EMAIL_SCHEDULE = '7 6 * * *'

def get_mode():
    slot = os.environ.get('SLOT', '').strip()
    if slot in SLOT_TO_MODE:
        return SLOT_TO_MODE[slot]
    if os.environ.get('FORCE_EMAIL', '').lower() == 'true':
        return 'email'
    s = os.environ.get('GITHUB_SCHEDULE', '')
    if s in YT_SCHEDULES:
        return 'yt'
    if s == MORNING_SCHEDULE:
        return 'morning'
    if s == EMAIL_SCHEDULE:
        return 'email'
    return 'full'

def is_test_run():
    """외부cron(SLOT)도 아니고 진짜 GitHub schedule도 아닌 단순 수동 Run workflow 클릭인지 판단"""
    if os.environ.get('SLOT', '').strip():
        return False
    if os.environ.get('GITHUB_SCHEDULE', '').strip():
        return False
    return os.environ.get('GITHUB_EVENT_NAME', '') == 'workflow_dispatch'

def load_existing():
    try:
        with open('data.json', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def notify_new_videos(videos, existing_today=None, send_digest=False):
    """
    notifyMode='instant' 영상: 항상 즉시 발송 (경제사냥꾼, 12시에 만나요, 당잠사)
    notifyMode='digest'  영상: send_digest=True일 때만 묶어서 발송 (morning/afternoon 슬롯)
    returns True if digestSent 플래그가 업데이트되어 data.json 재저장이 필요한 경우
    """
    from engines import notify
    if is_test_run():
        print('  테스트 실행(슬롯/스케줄 없음) - 신규영상 알림 보류 (data.json만 갱신)')
        return False
    if notify.in_quiet_hours():
        print('  무음시간(22~07시) - 신규영상 알림 보류 (data.json만 갱신)')
        return False

    new_videos = [v for v in videos if v.get('isNew')]
    needs_save = False

    # 즉시 알림 (경제사냥꾼, 12시에 만나요, 당잠사)
    instant = [v for v in new_videos if v.get('notifyMode') == 'instant']
    personal_instant = [v for v in instant if v.get('type') != 'media']
    media_instant = [v for v in instant if v.get('type') == 'media']
    for v in personal_instant:
        notify.send(notify.yt_new_video(v['name'], v['title'], v['videoId'], v.get('summary', '')))
        print(f'  → 텔레그램 발송(즉시): {v["name"]}')
    if media_instant:
        notify.send(notify.yt_media_digest(media_instant))
        print(f'  → 텔레그램 발송(즉시): {len(media_instant)}건')

    # 다이제스트 알림 (morning ~08:30 / afternoon ~14:30 슬롯에서만)
    if send_digest:
        # 이번 실행에서 새로 발견된 다이제스트 영상
        new_digest = [v for v in new_videos if v.get('notifyMode') != 'instant']
        seen = {v['videoId'] for v in new_digest}
        # 이전 yt슬롯에서 발견됐지만 아직 발송 안 된 영상 (data.json에서 로드)
        for v in (existing_today or {}).values():
            if v.get('notifyMode') != 'instant' and not v.get('digestSent') and v.get('videoId') not in seen:
                new_digest.append(v)
                seen.add(v['videoId'])
        if new_digest:
            notify.send(notify.yt_media_digest(new_digest))
            print(f'  → 텔레그램 발송(다이제스트): {len(new_digest)}건')
            digest_ids = {v['videoId'] for v in new_digest}
            for v in list(videos) + list((existing_today or {}).values()):
                if v.get('videoId') in digest_ids:
                    v['digestSent'] = True
            needs_save = True
        else:
            print('  다이제스트 발송할 신규 영상 없음')

    return needs_save

def run_yt_only(send_digest=False):
    existing = load_existing()
    existing_today = _today_videos_by_id(existing.get('youtube'))

    print('유튜브 개인채널 체크...')
    fetched = youtube.run(yt_only=True, existing=existing_today)
    needs_save = notify_new_videos(fetched, existing_today, send_digest=send_digest)

    youtube_data = _merge_today(existing_today, fetched)
    if any(v.get('isNew') for v in fetched) or needs_save:
        existing['youtube'] = youtube_data
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        print('data.json youtube 갱신')
    else:
        print('새 영상 없음 - data.json 유지')

def run_market_only():
    """장중 시세만 가볍게 갱신(뉴스/포트폴리오/AI/유튜브는 그대로 유지) - 알림 없음"""
    print('시장 데이터만 갱신(market-only slot)...')
    market_data = market.run()
    existing = load_existing()
    existing['market'] = market_data
    existing['updated'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    print('data.json market 필드만 갱신 완료')

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
    existing_today = _today_videos_by_id(existing.get('youtube'))
    fetched = youtube.run(existing=existing_today)
    notify_new_videos(fetched, existing_today, send_digest=send_morning)
    # RSS 차단 등으로 일부/전체 채널 수집이 실패해도 오늘 기존 데이터를 지우지 않고 유지
    # (자정이 지나면 _today_videos_by_id가 어제 영상을 자동으로 걸러내 자연스럽게 리셋됨)
    youtube_data = _merge_today(existing_today, fetched)

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
    print(f'=== invest-dash 실행 (mode={mode}, slot={os.environ.get("SLOT","-")}) ===')

    if mode == 'yt':
        run_yt_only()
    elif mode == 'afternoon':
        run_yt_only(send_digest=True)
    elif mode == 'market':
        run_market_only()
    elif mode == 'morning':
        run_full(send_morning=True)
    elif mode == 'email':
        run_full(send_email=True)
    else:
        run_full()

if __name__ == '__main__':
    main()
