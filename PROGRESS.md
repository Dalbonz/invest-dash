# PROGRESS.md - invest-dash 진행상황

> 새 세션 시작 시 날짜 입력 + CLAUDE.md + 이 파일 전달

---

## 현재 상태

**단계: 전체 파이썬 엔진 통합 완료, 3탭 대시보드 운영 중 (포트폴리오 탭 관리자 전용) + PWA(B&K) + 이메일 발송 추가**

접속 URL: https://dalbonz.github.io/invest-dash
마지막 업데이트: 2026-06-18

**앱 이름: B&K** (PWA 홈화면 설치 시 표시되는 이름)

---

## 완료

- GitHub Actions 자동화, cron 시각을 정각/30분에서 오프셋 (아래 스케줄 참고)
- market.py: us10y(^TNX), us30y(^TYX), candles 포함 / pykrx 투자자별 순매수(KRX 로그인 필요, 미해결)
- ai_summary.py: Sonnet 4.6, **볼드** 형식, **섹션당 4~5개 항목으로 분량 확대**
  - **내 보유종목(holdings) 섹션 추가**: 포트폴리오 종목명이 market.py 시세 키와 매칭되면 자동으로 액션아이템 생성 (NAME_TO_KEY 매핑, 매칭 없으면 빈 문자열로 안전하게 스킵 — 할루시네이션 방지)
- news.py: 6개 RSS 소스 (속보/분석/국내/국제) + AI 요약(Haiku)
  - HEADERS를 풀브라우저 UA로 교체 (매일경제 Cloudflare 403 차단 해결)
  - 파이낸셜뉴스 RSS 경로 변경 대응 (`/rss/r20/fn_realnews_*.xml`)
  - 국제뉴스 소스 추가 (fn_realnews_international.xml) → UI 필터 '미국'→'국제'로 변경
- youtube.py: RSS로 영상탐색 + Supadata 자막 + AI 요약 (미디어채널 3개 + 개인채널 3개)
  - 개인채널은 오늘 영상만 사용 (당일 KST 기준 필터)
  - 자막 있으면 [섹션명]+불릿 구조 요약(투자/free 포맷), 자막 없으면 제목 기반 요약
  - 중복 호출 방지: data.json의 기존 videoId와 동일하면 자막 재호출 없이 기존 요약 재사용
  - "12시에 만나요" 채널 titleKeyword 필터링 (같은 채널의 다른 시간대 프로그램과 구분)
  - temperature=0 고정
- notify.py: 텔레그램(아침브리핑+신규영상) + **이메일 발송 추가** (Gmail SMTP, HTML 다이제스트)
  - **무음시간 가드** `in_quiet_hours()`: KST 22:00~07:00에는 텔레그램 발송 보류 (data.json은 갱신)
- run.py: 모드 분기 (yt/morning/email/full) — **모든 모드에서 신규영상 체크+알림 통일 적용** (기존엔 yt모드만 알림)
- index.html 3탭 구조 (포트폴리오 관리자 전용)
  - 탭1 투자브리핑: AI 섹션 들여쓰기 개선, holdings 섹션 표시 추가
  - 탭2 증시: 기준선 항상 표시, 한국/미국 버튼 타이틀 인라인, K/A 뱃지
  - 탭2 증시: 상승/하락분야 → 테마탭 (반도체/AI/소부장/로봇/조선/금융/바이오)
  - 탭3 미디어: 뉴스 accordion, **유튜브 요약 가독성 개선** (섹션별 색상: 매수=초록/매도주의=빨강/오늘액션=보라, 좌측 컬러바)
  - 관리자 버튼 업데이트 시간 왼쪽 배치
- **PWA 추가**: manifest.json + service-worker.js + 아이콘(B&K, icons/) → "홈 화면에 추가" 가능
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

## GitHub Actions 실행 스케줄 (2026-06-18 변경)

cron을 정각/30분에서 오프셋 — GitHub가 공식 권장하는 방식. 정각/30분에 전세계 cron이 몰려서
**2.5~5시간 지연**되는 게 실제 로그로 확인된 원인이었음 (이전엔 08:30 브리핑이 11~13시에 도착).
추가로 investment-news-bot의 워크플로가 정확히 같은 시각(`30 23 * * *`)에 같은 계정에서 돌고 있어
지연을 가중시키고 있었음 → 비활성화 권장 (본인이 직접: Actions 탭 → Disable workflow).

| UTC | KST | 모드 | 내용 |
|---|---|---|---|
| 22:05 | 07:05 | yt | 개인채널 유튜브 체크 (무음시간 종료 직후, 밤사이 영상 첫 알림) |
| 23:08 | 08:08 | yt | 개인채널 유튜브 체크 |
| 23:22 | 08:22 | morning | 전체 실행 + 아침 브리핑 텔레그램 발송 (장 시작 09:00 전) |
| 01:12 | 10:12 | yt | 개인채널 유튜브 체크 |
| 06:07 | 15:07 | email | 전체 실행 + 이메일 발송 (12시에 만나요 처리 후) |
| 09:14 | 18:14 | full | 전체 실행 (텔레그램/이메일 없음, 신규영상은 알림) |

무음시간(KST 22:00~07:00)에는 어느 모드든 신규영상 텔레그램 알림이 보류됨 (data.json은 갱신).

---

## 다음 작업 (미완료)

- 포트폴리오 Google Sheets 연동 설정 (아래 참고) — 완성도 낮음, 프론트 그래프 미연결
- 기관/외국인/개인 pykrx 실패 원인 파악 (data.json에 investors 없음, KRX_ID/PW 필요한 것으로 보임)
- ETF → 내 연금 섹션으로 교체 (구상 중, 보류)
- investment-news-bot 워크플로 비활성화 (본인 액션 필요, 위 스케줄 참고)
- GMAIL_USER / GMAIL_PASSWORD / EMAIL_RECIPIENTS Secrets 등록 필요 (이메일 기능 활성화 조건)
- holdings 액션아이템: 현재 NAME_TO_KEY에 등록된 8개 종목만 매칭됨 → 포트폴리오 실제 종목과 비교해 매핑 확장 필요
- **Supadata 플랜 결정 대기** (아래 참고)

---

## 시스템 완성도 평가 (2026-06-18 기준, 자체 진단)

| 영역 | 완성도 | 비고 |
|---|---|---|
| 시장데이터 | 90% | investor 데이터(pykrx)만 미작동 |
| 뉴스 | 90% | 소스 6개 복구 완료 |
| AI 시황 | 88% | 분량 확대 + holdings 스캐폴딩 완료 |
| 유튜브 | 88% | 자막+필터+dedup 완료 |
| 텔레그램 | 85% | cron 지연 원인 파악, 오프셋 적용 |
| 이메일 | 70% | 코드 완료, secrets 등록 대기 |
| 관리자 패널 | 90% | |
| PWA | 80% | manifest+SW+아이콘 완료, 실기기 설치 테스트 필요 |
| 포트폴리오 GS연동 | 40% | 백엔드만 있고 프론트 미검증 (별도 작업 예정) |

investment-news-bot/YT_sumbot 대비 시장·뉴스·유튜브는 기능 우위 확인, 이메일은 새로 구현,
포트폴리오만 기존 대비 검증 부족 상태.

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
- **yt/morning/email/full 전체**: 새 영상 감지 시 텔레그램 발송 (무음시간 22~07시는 보류)
- **morning**: 아침 브리핑 (AI요약 + 주요지수 + 뉴스헤드라인 + 링크)
- **email**: AI시황 전체 + 시장표 + 유튜브요약 + 뉴스 HTML 다이제스트 (Gmail SMTP)

주의: 봇 토큰이 채팅에 노출됨 → BotFather에서 `/token` 재발급 권장

이메일 설정 (Secrets 등록 필요):
- `GMAIL_USER`: 발신 Gmail 주소
- `GMAIL_PASSWORD`: Gmail 앱 비밀번호 (일반 로그인 비번 아님, Google계정→보안→앱비밀번호에서 발급)
- `EMAIL_RECIPIENTS`: 쉼표구분 수신자 목록

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
├── index.html         완료 (3탭 + 포트폴리오 + PWA 등록)
├── run.py             완료 (yt/morning/email/full 모드)
├── manifest.json      완료 (PWA, 앱이름 B&K)
├── service-worker.js  완료 (네트워크우선 캐싱)
├── icons/             완료 (icon-192.png, icon-512.png)
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
  "ai":      { "summary", "kr", "us", "sectors", "holdings", "picks", "do", "dont" },
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
| 08:30 브리핑 지연(2.5~5시간) | cron이 정각/30분에 몰려 GitHub 큐 혼잡 + investment-news-bot이 동일 시각 cron 운영 | 모든 cron을 비정각으로 오프셋, investment-news-bot 워크플로 비활성화 |
| 수동실행시 신규영상 텔레그램 중복발송 | "모든 모드 알림 통일" 적용 후 workflow_dispatch도 알림 대상 포함됨 | GITHUB_EVENT_NAME=workflow_dispatch면 신규영상 알림만 보류 |
| data.json push 충돌(non-fast-forward) | 여러 실행이 거의 동시에 끝나 git push 경쟁 | pull --rebase 후 재시도 루프(최대5회) 추가 |
| 이메일 "AI 시황 데이터 없음" (조용한 실패) | 섹션 길이 확대 후 응답이 max_tokens(4500)에서 잘려 JSON 파싱 실패, 콘솔에 에러도 안 찍힘 | max_tokens 7000으로 확대 + 실패 분기에 print 로그 추가 |
| 이메일에 **볼드** 마크다운 그대로 노출 | text.replace('\n','<br>')만 적용, 볼드/수치색상 처리 없음 | _fmt_ai_section/_fmt_yt_section 추가 (대시보드 fmtAI와 동일 로직) |

---

## 참고 레포

- https://github.com/Dalbonz/investment-news-bot
- https://github.com/Dalbonz/4-my-money
