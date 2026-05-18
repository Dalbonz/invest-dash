# invest-dash 아키텍처

## 데이터 흐름
```
외부 API (yfinance, News)
    ↓
engines/**/**.py → output.json (Python: 수집·계산만)
    ↓
ai_summary/ → Claude API (해석·리포트만)
    ↓
dashboard/app.py (Streamlit 렌더링)
```

## 원칙
- Python: 데이터 수집 + 점수화만
- Claude API: 해석 + 리포트만
- 각 엔진은 독립 실행 가능
- output.json이 엔진 간 유일한 인터페이스

## 환경
- UI: Streamlit Cloud
- 저장소: GitHub (Public)
- Holdings: Google Sheets
- AI: Anthropic Claude API

## 엔진 실행 순서
1. engines/market/risk_detector.py
2. engines/portfolio/holdings_loader.py
3. engines/theme/trend_ranker.py (추후)
4. engines/ai_summary/market_interpreter.py
5. review/output_validator.py (검증)