# invest-dash 진행상황 (세션 인수인계용)

> 새 세션 시작 시 이 파일을 Claude에게 전달하면 바로 이어서 진행 가능

---

## 프로젝트 기본 정보

| 항목 | 내용 |
|------|------|
| 레포 | https://github.com/Dalbonz/invest-dash (Public) |
| UI | Streamlit Cloud |
| 언어 | Python |
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

---

## 데이터 흐름

```
외부 API (yfinance, News)
    ↓
engines/**/**.py → output.json
    ↓
ai_summary/ → Claude API
    ↓
dashboard/app.py (Streamlit)
```

---

## 완료된 작업 ✅

### 환경 세팅
- [x] GitHub 레포 생성 (invest-dash, Public)
- [x] Streamlit Cloud GitHub 연동
- [x] Google Cloud 프로젝트 생성 (invest-dash)
- [x] Google Sheets API + Drive API 활성화
- [x] 서비스 계정 JSON 키 발급
- [x] Anthropic API 키 확인

### 코드 생성 및 GitHub 업로드
- [x] 전체 폴더 스캐폴딩
- [x] `requirements.txt`
- [x] `.env.example`
- [x] `shared/config.py`
- [x] `shared/constants.py`
- [x] `shared/logger.py`
- [x] `shared/models.py`
- [x] `shared/utils.py`
- [x] `shared/cache.py`
- [x] `shared/gsheet_client.py`
- [x] `engines/market/market_collector.py`
- [x] `engines/market/scoring_engine.py`
- [x] `engines/market/risk_detector.py`
- [x] `engines/portfolio/holdings_loader.py`
- [x] `engines/ai_summary/claude_client.py`
- [x] `engines/ai_summary/prompt_builder.py`
- [x] `engines/ai_summary/market_interpreter.py`
- [x] `review/output_validator.py`
- [x] `review/code_reviewer.py`
- [x] `dashboard/app.py`
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

### 배포
- [ ] Streamlit Cloud 배포 설정
- [ ] Streamlit Secrets 환경변수 설정
- [ ] Google Sheets holdings 시트 초기 데이터 구성

### 문서
- [ ] `docs/roadmap.md`
- [ ] `docs/prompts.md`
- [ ] `docs/api_rules.md`

---

## 다음 할 일 (우선순위 순)

1. Streamlit Cloud 배포
2. Streamlit Secrets 환경변수 설정
3. Google Sheets holdings 시트 구성
4. 나머지 엔진 코드 작성

---

## 환경변수 목록 (.env / Streamlit Secrets)

```
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_SHEETS_ID=...
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
```