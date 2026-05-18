# invest-dash 진행상황 (세션 인수인계용)

> 새 세션 시작 시 이 파일을 Claude에게 전달하면 바로 이어서 진행 가능

---

## 프로젝트 기본 정보

| 항목 | 내용 |
|------|------|
| 레포 | https://github.com/Dalbonz/invest-dash (Public) |
| 앱 URL | https://invest-dash-ddfydopf3x7jvqggbzc5el.streamlit.app |
| UI | Streamlit Cloud |
| 언어 | Python 3.14 |
| AI | Claude API (claude-sonnet-4-20250514) |
| Holdings | Google Sheets 연동 |
| 저장소 | GitHub |

---

## 확정된 원칙

- Python: 데이터 수집 + 점수화만
- Claude API: 해석 + 리포트만
- 각 엔진 독립 실행 가능 (`python -m engines.xxx.xxx`)
- output.json이 엔진 간 유일한 인터페이스
- 고 사인 전까지 설계·제안만
- 달봉즈님 액션은 단계별 번호 리스트 + URL
- 코드 C&P는 TXT 파일로 제공
- 토큰 최소화
- 코드 생성 전 Streamlit Cloud 환경 기준 사전 검증 필수

---

## 데이터 흐름

```
외부 API (yfinance, News)
    ↓
engines/**/**.py → output.json
    ↓
ai_summary/ → Claude API
    ↓
app.py (Streamlit, 루트)
```

---

## 프로젝트 구조 확정

```
invest-dash/
├── app.py                          ← 루트 (Streamlit main)
├── engines/
│   ├── __init__.py
│   ├── market/
│   │   ├── __init__.py
│   │   ├── market_collector.py
│   │   ├── scoring_engine.py
│   │   ├── risk_detector.py
│   │   └── output.json
│   ├── portfolio/
│   │   ├── __init__.py
│   │   ├── holdings_loader.py
│   │   └── output.json
│   ├── ai_summary/
│   │   ├── __init__.py
│   │   ├── claude_client.py
│   │   ├── prompt_builder.py
│   │   ├── market_interpreter.py
│   │   └── output.json
│   ├── short_term/ (미완)
│   ├── mid_term/ (미완)
│   ├── long_term/ (미완)
│   └── theme/ (미완)
├── shared/
│   ├── __init__.py
│   ├── config.py
│   ├── constants.py
│   ├── logger.py
│   ├── models.py
│   ├── utils.py
│   ├── cache.py
│   └── gsheet_client.py
├── dashboard/                      ← pages/widgets/components용 (app.py 없음)
├── review/
│   ├── code_reviewer.py
│   └── output_validator.py
├── docs/
│   └── architecture.md
├── requirements.txt
├── .env.example
└── PROGRESS.md
```

---

## Streamlit Secrets 설정 완료

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
GOOGLE_SHEETS_ID = "..."

[GOOGLE_SERVICE_ACCOUNT]
type = "service_account"
project_id = "invest-dash-496701"
... (설정 완료)
```

---

## 완료된 작업 ✅

### 환경 세팅
- [x] GitHub 레포 생성 (invest-dash, Public)
- [x] Streamlit Cloud 배포 완료
- [x] Google Cloud 프로젝트 (invest-dash-496701)
- [x] Google Sheets API + Drive API 활성화
- [x] 서비스 계정 (invest-dash-bot) JSON 키 발급
- [x] Anthropic API 키 확인
- [x] Streamlit Secrets 설정 완료

### 코드
- [x] `app.py` (루트)
- [x] `shared/config.py` (st.secrets 지원)
- [x] `shared/constants.py`
- [x] `shared/logger.py`
- [x] `shared/models.py`
- [x] `shared/utils.py`
- [x] `shared/cache.py`
- [x] `shared/gsheet_client.py` (AttrDict → dict 변환 수정 완료)
- [x] `shared/__init__.py`
- [x] `engines/__init__.py`
- [x] `engines/market/__init__.py`
- [x] `engines/market/market_collector.py`
- [x] `engines/market/scoring_engine.py`
- [x] `engines/market/risk_detector.py`
- [x] `engines/portfolio/__init__.py`
- [x] `engines/portfolio/holdings_loader.py`
- [x] `engines/ai_summary/__init__.py`
- [x] `engines/ai_summary/claude_client.py`
- [x] `engines/ai_summary/prompt_builder.py`
- [x] `engines/ai_summary/market_interpreter.py`
- [x] `review/code_reviewer.py`
- [x] `review/output_validator.py`
- [x] `docs/architecture.md`

---

## 미완료 작업 🔲

### 빈 파일 (코드 작성 필요)
- [ ] `engines/short_term/momentum_analyzer.py`
- [ ] `engines/short_term/volatility_checker.py`
- [ ] `engines/short_term/flow_signal.py`
- [ ] `engines/mid_term/sector_rotation.py`
- [ ] `engines/mid_term/macro_cycle.py`
- [ ] `engines/mid_term/theme_tracker.py`
- [ ] `engines/long_term/retirement_checker.py`
- [ ] `engines/long_term/allocation_balance.py`
- [ ] `engines/long_term/exposure_analyzer.py`
- [ ] `engines/theme/news_fetcher.py`
- [ ] `engines/theme/keyword_analyzer.py`
- [ ] `engines/theme/trend_ranker.py`
- [ ] `engines/portfolio/risk_scoring.py`
- [ ] `engines/portfolio/correlation_checker.py`
- [ ] `review/data_flow_checker.py`
- [ ] `shared/timeframe.py`

### 다음 할 일 (우선순위 순)
1. gsheet_client 에러 확인 (AttrDict fix 배포 후)
2. Google Sheets holdings 시트 초기 데이터 구성
3. 나머지 엔진 코드 작성
4. UI 개선

---

## 주요 에러 해결 이력

| 에러 | 원인 | 해결 |
|------|------|------|
| ModuleNotFoundError: shared | app.py가 dashboard/ 안에 있음 | app.py를 루트로 이동 |
| missing fields client_email | st.secrets AttrDict를 dict로 변환 안 함 | dict(st.secrets["GOOGLE_SERVICE_ACCOUNT"]) |