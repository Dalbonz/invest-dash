# PROGRESS.md - invest-dash 진행상황

> 새 세션 시작 시 CLAUDE.md + 이 파일을 전달하면 바로 이어서 진행 가능

---

## 현재 상태

**단계: 리셋 완료 → data.json 스키마 확정 중**

---

## 완료 ✅

- GitHub 레포 생성 (Dalbonz/invest-dash, Public)
- Google Cloud 프로젝트 (invest-dash-496701)
- Google Sheets API + Drive API 활성화
- 서비스 계정 (invest-dash-bot) JSON 키 발급
- Anthropic API 키 확인
- 기존 Streamlit 코드 전체 삭제 (리셋)

---

## 다음 할 일 🔲

1. data.json 스키마 확정
2. Python 엔진 작성 (investment-news-bot 코드 재활용)
3. GitHub Actions 설정
4. GitHub Pages HTML UI

---

## 핵심 결정사항

| 항목 | 결정 |
|------|------|
| UI 방식 | GitHub Pages HTML (Streamlit 제거) |
| 데이터 흐름 | Python → data.json → HTML |
| 포트폴리오 | Google Sheets 읽기 전용 |
| 자동화 | GitHub Actions |
| AI | Claude API |

---

## 주요 에러 이력 (반복 방지)

| 에러 | 원인 | 해결 |
|------|------|------|
| ModuleNotFoundError | app.py 위치 문제 | 루트로 이동 |
| Secrets AttrDict | TOML 섹션 방식 | JSON 문자열로 저장 |
| WorksheetNotFound | 탭 이름 불일치 | 정확한 탭명 확인 |
| 2행 헤더 | get_all_records() 한계 | get_all_values() 사용 |

---

## 환경변수

```
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_SHEETS_ID=1jYVXz_rJ5CiVOWl3Rts5EPXBSgib3BCvf-TDXFegC6E
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
```