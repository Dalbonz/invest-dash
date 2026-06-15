# PROGRESS.md - invest-dash 진행상황

> 새 세션 시작 시 날짜 입력 + CLAUDE.md + 이 파일 전달

---

## 현재 상태

**단계: 전체 파이썬 엔진 통합 완료, 4탭 대시보드 운영 중**

접속 URL: https://dalbonz.github.io/invest-dash
마지막 업데이트: 2026-06-05 (워크플로 실행 확인 중)

---

## 완료

- GitHub Actions 자동화 (KST 9시/15시/18시)
- market.py: us10y(^TNX), us30y(^TYX), candles 포함
- ai_summary.py: summary/kr/us/sectors/picks/do/dont 7개 섹션
- news.py: category 포함
- youtube.py: RSS+AI 수집 엔진 (미디어채널 3개 + 일반채널 3개)
  - 4-my-money 외부 JSON 의존 제거, data.json 통합 완료
  - handle → channel_id 자동 변환 로직 포함
  - AI 요약: 설명 30자 미만이면 제목만 반환 (할루시네이션 방지)
  - temperature=0 고정
- index.html 4탭 구조 배포 완료
  - 탭1 뉴스 섹션 제거 (탭3 중복 해소)
  - 탭2 주식 타일 종목 교체 (한국 8개 + 미국 6개) + 관리자 편집 가능
  - 탭3 관리자 진입 버튼 추가
  - 탭4 포트폴리오 진입 시 비번 요구
  - 관리자 탭별 분리 (증시/미디어/포트폴리오 컨텍스트)
  - 우상단 Last Update 항상 표시 (데이터 로드 즉시, 전 탭 공통)
  - 미디어 탭: 600px↑ 뉴스/유튜브 좌우 2열, 600px 미만 탭버튼 유지
  - 투자브리핑 AI 타이틀 가시성 개선 (굵기/색상/left-border 강조)
  - 투자브리핑 AI 텍스트 줄바꿈 자동 처리 (pre-line + fmtAI)
  - 증시 차트 N페이 스타일 (전일종가 기준선, 상승=빨강/하락=파랑 baseline)
  - 증시 주식시세 테이블 기관/외국인/개인 순매수 컬럼 추가 (PC 768px↑)
  - 증시 주요ETF 섹션에 cb5 스파크라인 카드 추가 (SPY/QQQ/TLT/GLD/XLE 5개)
- ai_summary.py: Haiku → Sonnet 4.6 업그레이드, 프롬프트 상세화, max_tokens 3000
- market.py: pykrx 투자자별 순매수(기관/외국인/개인) 데이터 추가
- requirements.txt: pykrx 추가

---

## 현재 index.html 탭 구조

| 탭 | 제목 | 내용 |
|---|---|---|
| 1 | 투자 브리핑 | AI시황(7섹션) + 주요시장8개 |
| 2 | 증시 | 4카드(주식/지수/외환/원자재) + 주식시세 + ETF |
| 3 | 미디어 분석 | 뉴스(필터) + 유튜브(미디어/채널) |
| 4 | 포트폴리오 | Total/Bong/Kyoung + 비번(1111) + GS연동 |

---

## 다음 작업 (미완료)

- 포트폴리오 Google Sheets 연동 설정 (아래 참고)

---

## 주요 설정값

| 항목 | 값 |
|---|---|
| 포트폴리오 비번 | 1111 |
| SHA-256 해시 | 0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c |
| 관리자 비번 | 1111 (동일) |
| 관리자 진입 | 로고 5번 탭 |
| Bong GS URL | https://script.google.com/macros/s/AKfycbw1W851igwvCuIzoghZyKfgkpqsgc2oPxNHrHsJhDLWhQbKHvlxQGTqMzLuImqnImHv/exec |
| AI 모델 (요약) | claude-haiku-4-5-20251001 |
| AI 모델 (시황) | claude-sonnet-4-6 |

---

## 파일 구조

```
invest-dash/
├── engines/
│   ├── market.py      완료 (us10y/us30y/candles 포함)
│   ├── news.py        완료 (category 포함)
│   ├── portfolio.py   완료 (GS 연동)
│   ├── ai_summary.py  완료 (7섹션 프롬프트)
│   ├── youtube.py     완료 (RSS+AI, data.json 통합)
│   └── __init__.py
├── .github/workflows/
│   └── update.yml     완료 (KST 9/15/18시)
├── index.html         완료 (4탭)
├── run.py             완료
├── requirements.txt   완료
├── data.json          자동생성 (keys: updated/market/news/portfolio/ai/youtube)
├── CLAUDE.md          완료
└── PROGRESS.md        이 파일
```

---

## data.json 스키마 (확정)

```json
{
  "updated": "ISO8601 KST",
  "market":  { "indices": [...], "stocks": [...], "etfs": [...], ... },
  "news":    [ { "title", "link", "source", "category", "published" }, ... ],
  "portfolio": { "bong": {...}, "kyoung": {...}, "total": {...} },
  "ai":      { "summary", "kr", "us", "sectors", "picks", "do", "dont" },
  "youtube": [ { "name", "type", "videoId", "title", "updated", "summary" }, ... ]
}
```

---

## 포트폴리오 Google Sheets 연동 설정 방법

현재 `portfolio.py`는 GS에서 데이터를 읽지만, UI의 포트폴리오 탭은 GS에서 직접 읽지 않고 Apps Script URL을 통해 읽음. 두 경로 중 하나가 연결되어야 함.

**현재 구조 이슈:** portfolio.py는 data.json에 저장하지만, UI 포트폴리오 탭은 `getAppsScriptUrlFor('bong')` URL을 호출. data.json의 포트폴리오 데이터를 UI에서 읽도록 연결이 안 됨.

**해결 방법 (둘 중 선택):**

**A안 (권장): data.json 경유 방식**
- portfolio.py에서 GS 데이터를 읽어 data.json의 `portfolio.bong`, `portfolio.kyoung`에 저장
- UI에서 `jsonData.portfolio`를 직접 사용하도록 renderPortfolio 수정
- Apps Script 불필요

**B안: Apps Script 방식 (현재 구조 유지)**
1. GS에서 도구 → 스크립트 편집기 → Apps Script 코드 배포
2. 웹 앱 URL을 관리자 메뉴 → 포트폴리오 설정에 입력
3. GS 공유 설정: "링크가 있는 모든 사용자" 뷰어 권한 필요

**현재 상태:** portfolio.py가 GS 연동 중인지 Secrets 설정 여부 확인 필요
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

---

## 참고 레포

- https://github.com/Dalbonz/investment-news-bot
- https://github.com/Dalbonz/4-my-money
