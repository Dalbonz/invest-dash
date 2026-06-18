# PROGRESS.md - invest-dash 진행상황

> 새 세션 시작 시 날짜 입력 + CLAUDE.md + 이 파일 전달

---

## 현재 상태

**단계: 전체 파이썬 엔진 통합 완료, 3탭 대시보드 운영 중 (포트폴리오 탭 관리자 전용)**

접속 URL: https://dalbonz.github.io/invest-dash
마지막 업데이트: 2026-06-15

---

## 완료

- GitHub Actions 자동화 (KST 6/8/8:30/10/15/18시)
- market.py: us10y(^TNX), us30y(^TYX), candles 포함 / pykrx 투자자별 순매수
- ai_summary.py: Sonnet 4.6, 7개 섹션, **볼드** 형식 지시 포함
- news.py: 6개 RSS 소스 (속보/분석/국내/국제) + AI 요약(Haiku)
  - HEADERS를 풀브라우저 UA로 교체 (매일경제 Cloudflare 403 차단 해결)
  - 파이낸셜뉴스 RSS 경로 변경 대응 (`/rss/r20/fn_realnews_*.xml`)
  - 국제뉴스 소스 추가 (fn_realnews_international.xml) → UI 필터 '미국'→'국제'로 변경
- youtube.py: RSS로 영상탐색 + Supadata 자막 + AI 요약 (미디어채널 3개 + 개인채널 3개)
  - 개인채널은 오늘 영상만 사용 (당일 KST 기준 필터)
  - 자막 있으면 [섹션명]+불릿 구조 요약(투자/free 포맷), 자막 없으면 제목 기반 요약
  - **중복 호출 방지**: data.json의 기존 videoId와 동일하면 자막 재호출 없이 기존 요약 재사용 (run.py에서 existing 맵 전달)
  - temperature=0 고정
- notify.py: 텔레그램 발송 (아침 브리핑 + 개인채널 새 영상 알림)
- run.py: 모드 분기 (mode=yt/morning/full)
- index.html 3탭 구조 (포트폴리오 관리자 전용)
  - 탭1 투자브리핑: AI 섹션 들여쓰기 개선, 오늘할것/하지말것 중복 제거
  - 탭2 증시: 기준선 항상 표시, 한국/미국 버튼 타이틀 인라인, K/A 뱃지
  - 탭2 증시: 상승/하락분야 → 테마탭 (반도체/AI/소부장/로봇/조선/금융/바이오)
  - 탭3 미디어: 뉴스 accordion(클릭→기사보기), 유튜브 기본닫힘→클릭펼침
  - 관리자 버튼 업데이트 시간 왼쪽 배치
- requirements.txt: pykrx 추가

---

## 현재 index.html 탭 구조

| 탭 | 제목 | 내용 |
|---|---|---|
| 1 | 투자 브리핑 | AI시황(7섹션,들여쓰기) + 주요시장8개(WTI포함) |
| 2 | 증시 | 4카드(기준선sparkline) + 주식시세(테마탭,K/A뱃지) + ETF |
| 3 | 미디어 분석 | 뉴스(accordion+AI요약) + 유튜브(기본닫힘+펼침) |
| - | 포트폴리오 | 관리자→포트폴리오 보기로만 진입 (비번 1111) |

---

## GitHub Actions 실행 스케줄

| UTC | KST | 모드 | 내용 |
|---|---|---|---|
| 21:00 | 06:00 | yt | 개인채널 유튜브 체크 → 새 영상 텔레그램 발송 |
| 23:00 | 08:00 | yt | 개인채널 유튜브 체크 → 새 영상 텔레그램 발송 |
| 23:30 | 08:30 | morning | 전체 실행 + 아침 브리핑 텔레그램 발송 |
| 01:00 | 10:00 | yt | 개인채널 유튜브 체크 → 새 영상 텔레그램 발송 |
| 06:00 | 15:00 | full | 전체 실행 (알림 없음) |
| 09:00 | 18:00 | full | 전체 실행 (알림 없음) |

---

## 다음 작업 (미완료)

- 포트폴리오 Google Sheets 연동 설정 (아래 참고)
- 기관/외국인/개인 pykrx 실패 원인 파악 (data.json에 investors 없음, KRX_ID/PW 필요한 것으로 보임)
- ETF → 연금 섹션으로 교체 (구상 중)
- 카카오톡 알림 (검토 중)
- **Supadata 플랜 결정 대기** (아래 참고)

---

## Supadata 자막 API — 크레딧 이슈 (2026-06-18)

- 기존 Google Apps Script(YT_sumbot)가 매시간(24회/일) × 6채널로 Supadata를 호출해 Free플랜(월100크레딧) 소진
- 호출 테스트 결과 `429 limit-exceeded`, **리셋일: 2026-07-13**
- Apps Script 트리거 비활성화 권장 (크레딧 회복은 안 되지만, 리셋 후 invest-dash와 중복 소모 방지)
  - 비활성화: 스크립트 에디터 → 시계 아이콘(트리거) → `runScheduled` 옆 ⋮ → 삭제
  - **복구 방법**: 스크립트 에디터에서 함수 선택창에 `setupTrigger` 선택 → 실행(▶) → 매시간 트리거 자동 재생성됨 (코드에 이미 있는 함수, 별도 기억 불필요)
- youtube.py에 중복호출 방지 추가됨(위 참고) → 실제 소모량은 "워크플로 실행횟수"가 아니라 "신규 영상 개수"에 비례
- 플랜 선택 보류 중 (Basic $/월 300크레딧 vs Pro 3000크레딧) — 중복방지 적용 후 실사용량 보고 결정 예정

---

## 텔레그램 발송 설정

Secrets 설정 완료 (2026-06-15):
- `TELEGRAM_BOT_TOKEN`: YT_sum_bot 토큰 설정됨
- `TELEGRAM_CHAT_IDS`: `8649321702,8799181333` (달봉즈, 경)

모드별 동작:
- **yt**: 개인채널(12시에만나요/경제사냥꾼/슈페tv) 새 영상 감지 시 발송
- **morning**: 아침 브리핑 (AI요약 + 주요지수 + 뉴스헤드라인 + 링크)

주의: 봇 토큰이 채팅에 노출됨 → BotFather에서 `/token` 재발급 권장

---

## 주요 설정값

| 항목 | 값 |
|---|---|
| 포트폴리오 비번 | 1111 |
| SHA-256 해시 | 0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c |
| 관리자 비번 | 1111 (동일) |
| 관리자 진입 | 로고 5번 탭 |
| Bong GS URL | https://script.google.com/macros/s/AKfycbw1W851igwvCuIzoghZyKfgkpqsgc2oPxNHrHsJhDLWhQbKHvlxQGTqMzLuImqnImHv/exec |
| AI 모델 (유튜브/뉴스요약) | claude-haiku-4-5-20251001 |
| AI 모델 (시황) | claude-sonnet-4-6 |

---

## 파일 구조

```
invest-dash/
├── engines/
│   ├── market.py      완료 (us10y/us30y/candles 포함)
│   ├── news.py        완료 (category + AI 요약)
│   ├── portfolio.py   완료 (GS 연동)
│   ├── ai_summary.py  완료 (7섹션 프롬프트)
│   ├── youtube.py     완료 (RSS+AI, 개인채널 오늘필터)
│   ├── notify.py      완료 (텔레그램 발송)
│   └── __init__.py
├── .github/workflows/
│   └── update.yml     완료 (KST 6/8/8:30/10/15/18시)
├── index.html         완료 (3탭 + 포트폴리오)
├── run.py             완료 (yt/morning/full 모드)
├── requirements.txt   완료
├── data.json          자동생성 (keys: updated/market/news/portfolio/ai/youtube)
├── CLAUDE.md          완료
└── PROGRESS.md        이 파일
```

---

## data.json 스키마 (확정)

```json
{
  "updated": "ISO8601 UTC",
  "market":  { "kospi": {...}, "sp500": {...}, ... },
  "news":    [ { "title", "link", "source", "category", "summary" }, ... ],
  "portfolio": { "bong": {...}, "kyoung": {...}, "total": {...} },
  "ai":      { "summary", "kr", "us", "sectors", "picks", "do", "dont" },
  "youtube": [ { "name", "type", "videoId", "title", "updated", "summary" }, ... ]
}
```

---

## 포트폴리오 Google Sheets 연동 설정 방법

현재 `portfolio.py`는 GS에서 데이터를 읽지만, UI의 포트폴리오 탭은 GS에서 직접 읽지 않고 Apps Script URL을 통해 읽음.

**A안 (권장): data.json 경유 방식**
- portfolio.py에서 GS 데이터를 읽어 data.json의 `portfolio.bong`, `portfolio.kyoung`에 저장
- UI에서 `jsonData.portfolio`를 직접 사용하도록 renderPortfolio 수정
- Apps Script 불필요

**현재 상태:**
- GOOGLE_SHEETS_ID: 설정됨
- GOOGLE_SERVICE_ACCOUNT_JSON: 설정 여부 확인 필요

---

## 에러 이력 (반복 방지)

| 에러 | 원인 | 해결 |
|---|---|---|
| api_status_404 | 모델명 오류 | claude-haiku-4-5-20251001 사용 |
| WorksheetNotFound | 탭 이름 불일치 | 주식현황상세 (정확히) |
| Actions push 403 | workflow permissions | Read and write 설정 |
| UTC 이중변환 | toKST 헬퍼 내부에서 +9h 중복 | ISO8601 그대로 JS Date에 넘기도록 수정 |
| 유튜브 할루시네이션 | 설명 부족 시 AI가 내용 생성 | 설명 30자 미만이면 제목만 반환 |
| handle 미해결 | YouTube @handle → channel_id 실패 | 다중 URL/패턴 시도 로직 강화 |
| rainbow -74% 데이터 오류 | 277810.KS(KOSPI)로 잘못 설정 | 277810.KQ(KOSDAQ)으로 수정 |
| Pages 공백 | index.html 미커밋으로 구 버전 서비스 | 전체 변경사항 수동 커밋 필요 |
| loadETF JS 문법 오류 | `}}}}catch` 여분 중괄호 | `}}}catch`로 수정 |
| 매일경제 RSS "not well-formed" | Cloudflare가 기본 UA 차단(403, 챌린지 HTML 반환) | 풀브라우저 User-Agent로 교체 |
| 파이낸셜뉴스 RSS 404 | RSS 경로가 `/rss/r20/fn_realnews_*.xml`로 변경됨 | URL 갱신 |
| 12시에만나요 영상 오매칭 | RSS 최신 1건만 사용 → 다른 시간대 프로그램 섞임 | RSS 전체 entry 순회 + titleKeyword 필터 |
| Supadata 429 limit-exceeded | 기존 Apps Script가 매시간 호출해 Free플랜(월100) 소진 | 유료 플랜 업그레이드 + 중복호출 방지 추가 |

---

## 참고 레포

- https://github.com/Dalbonz/investment-news-bot
- https://github.com/Dalbonz/4-my-money
