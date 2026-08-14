"""
메인 실행 파일 - GitHub Actions에서 실행
실행 모드는 SLOT 환경변수로 결정 (외부 cron 서비스가 workflow_dispatch 호출시 inputs.slot으로 전달):
  morning : 전체 실행 + 텔레그램 아침 브리핑(AI시황) + 유튜브 다이제스트 (KST 08:08)
  email   : 전체 실행 + 이메일 발송 + 유튜브 다이제스트 (KST 15:07, "12시에 만나요" 처리 후)
  full    : 전체 실행 + 유튜브 다이제스트 (KST 18:14)
  market  : 시세만 가볍게 갱신 (장중 추가호출용, 알림 없음, 뉴스/포트폴리오/AI/유튜브는 그대로 유지)

SLOT이 없으면 GITHUB_SCHEDULE(진짜 GitHub schedule: 트리거, 지연될 수 있음)로 폴백,
둘 다 없으면 사람이 그냥 "Run workflow" 누른 테스트 실행으로 간주 (알림 보류).

유튜브 신규영상 알림은 2026-08-12부터 채널별 "마지막 발송 이후" 체크포인트 방식으로
하루 3번(morning/email/full 슬롯)만 한 건의 통합 메시지로 발송한다 (기존 채널별
즉시발송/다이제스트 혼용 방식은 스팸처럼 느껴진다는 피드백으로 폐지).
체크포인트는 data.json의 yt_checkpoints에 채널별 ISO 시각으로 저장되며 자정과 무관하게
유지된다 (사이트에 보여주는 "오늘의 영상" 목록은 기존처럼 자정에 리셋, 완전히 별개).
무음시간(22:00~07:00 KST)에는 발송도 체크포인트 갱신도 보류한다.
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

def _parse_dt(iso_str):
    try:
        return datetime.fromisoformat((iso_str or '').replace('Z', '+00:00'))
    except Exception:
        return None

def _today_videos_by_id(youtube_list):
    """data.json에 저장된 기존 유튜브 리스트 중 오늘(KST) 영상만 골라 videoId로 매핑(자정 지나면 자동 리셋)"""
    return {v['videoId']: v for v in (youtube_list or []) if v.get('videoId') and _is_today_kst(v.get('updated'))}

def _merge_today(existing_today, fetched):
    """이번 실행에서 못 가져온(차단 등) 채널의 오늘 영상은 그대로 유지, 새로 가져온 건 갱신"""
    fetched_ids = {v['videoId'] for v in fetched}
    carried = [v for vid, v in existing_today.items() if vid not in fetched_ids]
    return carried + fetched

SLOT_TO_MODE = {'morning': 'morning', 'email': 'email', 'full': 'full', 'market': 'market'}

def get_mode():
    slot = os.environ.get('SLOT', '').strip()
    if slot in SLOT_TO_MODE:
        return SLOT_TO_MODE[slot]
    if os.environ.get('FORCE_EMAIL', '').lower() == 'true':
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

# 텔레그램 발송 대상에서 제외할 채널 (사이트에는 표시하되 알림은 안 보냄)
NOTIFY_EXCLUDE = {'매일경제TV'}

def send_yt_checkpoint_digest(youtube_data, existing_checkpoints):
    """
    채널별 '마지막 발송 이후' 새로 나온 영상만 모아 텔레그램 한 건으로 발송.
    반환값: (갱신된 checkpoints dict, 발송했는지 여부)
    """
    from engines import notify
    if is_test_run():
        print('  테스트 실행 - 유튜브 다이제스트 발송 보류 (체크포인트도 유지)')
        return existing_checkpoints, False
    if notify.in_quiet_hours():
        print('  무음시간(22~07시) - 유튜브 다이제스트 발송 보류 (체크포인트도 유지)')
        return existing_checkpoints, False

    now = datetime.now(timezone.utc)
    now_iso = now.strftime('%Y-%m-%dT%H:%M:%SZ')
    checkpoints = dict(existing_checkpoints)
    to_send = []
    channels_checked = set()

    for v in youtube_data:
        name = v.get('name')
        if not name or name in NOTIFY_EXCLUDE:
            continue
        channels_checked.add(name)
        cp_dt = _parse_dt(existing_checkpoints.get(name))
        v_dt = _parse_dt(v.get('updated'))
        if v_dt is None:
            continue
        if cp_dt is None or v_dt > cp_dt:
            to_send.append(v)

    if to_send:
        notify.send(notify.yt_media_digest(to_send))
        print(f'  → 텔레그램 유튜브 다이제스트 발송: {len(to_send)}건')
    else:
        print('  유튜브 다이제스트: 신규 영상 없음')

    for name in channels_checked:
        checkpoints[name] = now_iso
    return checkpoints, bool(to_send)

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
    # youtube.run()은 체크포인트 다이제스트용으로 최근 36시간(오늘+어제 저녁)을 넓게 가져옴
    fetched = youtube.run(existing=existing_today)

    print('6. 유튜브 다이제스트 체크...')
    checkpoints, _ = send_yt_checkpoint_digest(fetched, existing.get('yt_checkpoints', {}))

    # 사이트에 저장/표시하는 목록은 오늘자만 (자정 리셋 유지, 어제 영상은 안 섞이게)
    fetched_today = [v for v in fetched if _is_today_kst(v.get('updated'))]
    # RSS 차단 등으로 일부/전체 채널 수집이 실패해도 오늘 기존 데이터를 지우지 않고 유지
    # (자정이 지나면 _today_videos_by_id가 어제 영상을 자동으로 걸러내 자연스럽게 리셋됨)
    youtube_data = _merge_today(existing_today, fetched_today)

    data = {
        'updated': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'market': market_data,
        'news': news_data,
        'portfolio': portfolio_data,
        'ai': ai_data,
        'youtube': youtube_data,
        'yt_checkpoints': checkpoints,
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

    if mode == 'market':
        run_market_only()
    elif mode == 'morning':
        run_full(send_morning=True)
    elif mode == 'email':
        run_full(send_email=True)
    else:
        run_full()

if __name__ == '__main__':
    main()
