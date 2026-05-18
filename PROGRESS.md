# PROGRESS.md - invest-dash 진행상황

> 새 세션 시작 시 CLAUDE.md + 이 파일을 전달하면 바로 이어서 진행 가능

---

## 현재 상태

**단계: AI 요약 모델명 오류 수정 필요**

---

## 완료 ✅

- GitHub 레포 생성 (Dalbonz/invest-dash, Public)
- 전체 구조 구축 완료
- GitHub Actions 자동화 (data.json 생성/push)
- GitHub Pages 배포 완료
- Google Sheets 포트폴리오 연동 (주식현황상세, 16개 종목)
- 시장 데이터 수집 정상 (yfinance)
- 뉴스 수집 정상 (RSS)
- index.html 대시보드 배포 완료

**접속 URL:** https://dalbonz.github.io/invest-dash

---

## 즉시 해결 필요 🔥

### AI 요약 모델명 오류
- 현재 에러: `api_status_404`
- 원인: 모델명이 유효하지 않음
- 파일: `engines/ai_summary.py`
- 해결: Actions 로그에서 정확한 에러 메시지 확인 후 올바른 모델명으로 수정
- **다음 세션 시작 시 첫 번째로 할 것**

**검증 방법:**
1. `engines/ai_summary.py` 에서 에러 시 상세 로그 출력 확인
2. https://console.anthropic.com → API Keys → 현재 유효한 키 확인
3. GitHub Secrets `ANTHROPIC_API_KEY` 업데이트

---

## 다음 할 일 🔲

1. AI 요약 모델명 수정 (최우선)
2. 포트폴리오 평가금액/수익 0원 수정 (₩ 기호 파싱 문제)
3. 탭 구조 UI 구현 (4개 탭)
4. 유튜브 탭 연동 (4-my-money youtube.json)
5. 뉴스 탭 연동 (investment-news-bot data.json)
6. 애플 스타일 UI 디자인

---

## 탭 구조 확정 (UI 작업 예정)

| 탭 | 데이터 소스 |
|------|------|
| 📊 시장 | invest-dash data.json |
| 💼 포트폴리오 | invest-dash data.json |
| 📰 뉴스 | investment-news-bot data.json |
| 🎬 유튜브 | 4-my-money youtube.json |

---

## 아키텍처 (확정)

```
Python 엔진들 (GitHub Actions - KST 9시, 15시, 18시)
    ↓
data.json (GitHub 레포)
    ↓
GitHub Pages HTML 대시보드
```

---

## 파일 구조

```
invest-dash/
├── engines/
│   ├── __init__.py
│   ├── market.py       ✅
│   ├── news.py         ✅
│   ├── portfolio.py    ✅
│   └── ai_summary.py   ⚠️ 모델명 수정 필요
├── .github/workflows/
│   └── update.yml      ✅
├── index.html          ✅
├── run.py              ✅
├── requirements.txt    ✅
├── data.json           ✅ (자동 생성)
├── CLAUDE.md           ✅
└── PROGRESS.md         ✅
```

---

## 기술 스택

| 항목 | 내용 |
|------|------|
| 언어 | Python |
| 자동화 | GitHub Actions |
| UI | GitHub Pages HTML |
| AI | Anthropic Claude API |
| 포트폴리오 | Google Sheets (주식현황상세, 2행 헤더) |

---

## Google Sheets

- ID: `1jYVXz_rJ5CiVOWl3Rts5EPXBSgib3BCvf-TDXFegC6E`
- 탭: `주식현황상세`
- 1행: 그룹헤더, 2행: 컬럼명, 3행~: 데이터
- 서비스계정: `invest-dash-bot@invest-dash-496701.iam.gserviceaccount.com`

---

## 참고 레포

- https://github.com/Dalbonz/investment-news-bot
- https://github.com/Dalbonz/4-my-money

---

## 주요 에러 이력 (반복 방지)

| 에러 | 원인 | 해결 |
|------|------|------|
| Streamlit 구조 | 배포 환경 불안정 | GitHub Pages로 전환 |
| WorksheetNotFound | 탭 이름 불일치 | 정확한 탭명 확인 |
| 2행 헤더 | get_all_records() 한계 | get_all_values() 사용 |
| Actions push 403 | workflow permissions | Read and write 설정 |
| AI api_status_404 | 모델명 오류 | 다음 세션에서 수정 |