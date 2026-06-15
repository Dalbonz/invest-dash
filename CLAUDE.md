# CLAUDE.md - invest-dash 프로젝트 컨텍스트

> Claude Code 및 Claude.ai 세션 시작 시 이 파일을 먼저 읽을 것

---

## 프로젝트 개요

개인 투자 참고용 대시보드
- 한국/미국 주식, ETF, 연금 포트폴리오 모니터링
- 시장 데이터 + AI 해석 + 포트폴리오 현황 통합

---

## 기술 스택 (확정)

| 항목 | 내용 |
|------|------|
| 언어 | Python |
| 데이터 흐름 | Python 엔진 → data.json → GitHub Pages HTML |
| 자동화 | GitHub Actions (스케줄 실행) |
| UI | GitHub Pages (단일 HTML, 모바일/PC 반응형) |
| AI (시황) | Anthropic Claude API (claude-sonnet-4-20250514) |
| AI (유튜브 요약) | Anthropic Claude API (claude-haiku-4-5-20251001) |
| 포트폴리오 | Google Sheets 연동 (읽기 전용) |
| 저장소 | GitHub (Dalbonz/invest-dash) |

---

## 아키텍처

```
Python 엔진들 (GitHub Actions)
    ↓
data.json (GitHub 레포)
    ↓
GitHub Pages HTML 대시보드
```

---

## 데이터 소스

| 소스 | 용도 | 엔진 |
|------|------|------|
| yfinance | 시장 지수/종목 가격 | market.py |
| RSS (매경, 한경 등) | 뉴스 | news.py |
| YouTube RSS XML | 유튜브 최신 영상 수집 | youtube.py |
| Google Sheets | 포트폴리오 보유 현황 | portfolio.py |
| Anthropic Claude API | 시장 해석/AI 요약/유튜브 요약 | ai_summary.py, youtube.py |

---

## Google Sheets 구조

| 탭명 | 용도 |
|------|------|
| 주식현황상세 | 현재 보유 주식 현황 (2행 헤더) |
| 예적금내역 | 예적금 현황 |
| 입출금통장 | 현금 현황 |

- 1행: 그룹 헤더 (병합 셀)
- 2행: 실제 컬럼명
- 3행~: 데이터

---

## 환경변수 (GitHub Actions Secrets)

```
ANTHROPIC_API_KEY
GOOGLE_SHEETS_ID=1jYVXz_rJ5CiVOWl3Rts5EPXBSgib3BCvf-TDXFegC6E
GOOGLE_SERVICE_ACCOUNT_JSON
```

---

## 참고 레포

- https://github.com/Dalbonz/investment-news-bot (시장 데이터/AI 코드 재활용)
- https://github.com/Dalbonz/4-my-money (UI 스타일 참고)

---

## 개발 원칙

1. 데이터 먼저, UI 나중
2. data.json 스키마 확정 후 변경 금지
3. 코드 생성 전 반드시 자체 검증
4. 연관 파일 수정 시 한 번에 모두 알림
5. 줄 번호 언급 금지
6. 고 사인 전까지 제안만
7. 달봉즈님 액션은 단계별 번호 + URL
8. 코드는 TXT 파일로 제공
9. 토큰 최소화

---

## 작업 환경

- 평일: 안드로이드 탭 (github.dev로 편집)
- 주말: PC 가능
- Claude Code 사용 가능