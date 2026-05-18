# PROGRESS.md - invest-dash 진행상황

> 새 세션 시작 시 CLAUDE.md + 이 파일을 전달하면 바로 이어서 진행 가능

---

## 현재 상태

**단계: 엔진 완성 → GitHub Actions push 권한 수정 필요**

---

## 완료 ✅

- GitHub 레포 생성 (Dalbonz/invest-dash, Public)
- 기존 Streamlit 코드 전체 삭제 (리셋)
- CLAUDE.md, PROGRESS.md 생성
- 전체 구조 커밋 완료:
  - `run.py` (메인 실행)
  - `engines/market.py`
  - `engines/news.py`
  - `engines/portfolio.py`
  - `engines/ai_summary.py`
  - `engines/__init__.py`
  - `.github/workflows/update.yml`
  - `requirements.txt`
- GitHub Actions Secrets 3개 설정 완료
  - ANTHROPIC_API_KEY
  - GOOGLE_SHEETS_ID
  - GOOGLE_SERVICE_ACCOUNT_JSON
- GitHub Actions 수동 실행 → data.json 생성 성공 (444 lines)

---

## 다음 할 일 🔲

1. **GitHub Actions push 권한 수정** (최우선)
   - update.yml에 `permissions: contents: write` 추가
   - 또는 GitHub 레포 Settings → Actions → Workflow permissions → Read and write 허용

2. GitHub Pages 활성화 (data.json 읽는 HTML 대시보드)

3. index.html 작성 (4-my-money 스타일 참고)

---

## 즉시 수정할 것 (다음 세션 시작 시)

### update.yml permissions 추가

```yaml
jobs:
  update:
    runs-on: ubuntu-latest
    permissions:
      contents: write   # ← 이거 추가
```

또는 GitHub 레포:
Settings → Actions → General → Workflow permissions → Read and write permissions 선택 → Save

---

## 아키텍처 (확정)

```
Python 엔진들 (GitHub Actions 스케줄)
    ↓
data.json (GitHub 레포)
    ↓
GitHub Pages HTML 대시보드
```

---

## 기술 스택

| 항목 | 내용 |
|------|------|
| 언어 | Python |
| 자동화 | GitHub Actions (KST 9시, 15시, 18시) |
| UI | GitHub Pages HTML (모바일/PC 반응형) |
| AI | Anthropic Claude API (claude-sonnet-4-20250514) |
| 포트폴리오 | Google Sheets (주식현황상세 탭, 2행 헤더) |

---

## Google Sheets 구조

- 시트 ID: `1jYVXz_rJ5CiVOWl3Rts5EPXBSgib3BCvf-TDXFegC6E`
- 탭명: `주식현황상세`
- 1행: 그룹 헤더 (병합 셀)
- 2행: 실제 컬럼명
- 3행~: 데이터

---

## 참고 레포

- https://github.com/Dalbonz/investment-news-bot (엔진 코드 재활용)
- https://github.com/Dalbonz/4-my-money (UI 스타일 참고)

---

## 주요 에러 이력 (반복 방지)

| 에러 | 원인 | 해결 |
|------|------|------|
| Streamlit ModuleNotFoundError | app.py 위치 | → 구조 전체 변경 (GitHub Pages로) |
| Secrets AttrDict | TOML 섹션 방식 | JSON 문자열로 저장 |
| WorksheetNotFound | 탭 이름 불일치 | 정확한 탭명 확인 |
| 2행 헤더 | get_all_records() 한계 | get_all_values() 사용 |
| Actions push 403 | workflow permissions | contents: write 추가 필요 |