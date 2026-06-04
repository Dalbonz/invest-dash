# PROGRESS.md - invest-dash 진행상황

> 새 세션 시작 시 날짜 입력 + CLAUDE.md + 이 파일 전달

---

## 현재 상태

**단계: index.html 4탭 통합 완료, 추가 수정 진행 중**

접속 URL: https://dalbonz.github.io/invest-dash

---

## 완료

- GitHub Actions 자동화 (KST 9시/15시/18시)
- market.py: us10y(^TNX), us30y(^TYX), candles 포함
- ai_summary.py: summary/kr/us/sectors/picks/do/dont 7개 섹션
- news.py: category 포함
- Apps Script: 미디어채널 3개(한경TV/연합TV/매경TV) + 일반채널 3개 + 48시간 히스토리
- index.html 4탭 구조 배포 완료

---

## 현재 index.html 탭 구조

| 탭 | 제목 | 내용 |
|---|---|---|
| 1 | 투자 브리핑 | AI시황(7섹션) + 주요시장8개 + 뉴스(필터) |
| 2 | 증시 | 4카드(주식/지수/외환/원자재) + 주식시세 + ETF |
| 3 | 미디어 분석 | 뉴스(필터) + 유튜브(미디어/채널) |
| 4 | 포트폴리오 | Total/Bong/Kyoung + 비번(1111) + GS연동 |

---

## 다음 작업 (미완료)

1. 탭1 뉴스 섹션 제거 (탭3 중복)
2. 탭2 주식 타일 종목 교체
   - 한국: 삼성전자/SK하이닉스(반도체) + 한화에어로/LIG넥스원(방산) + 레인보우로보틱스/두산로보틱스(로봇) + 삼성바이오/셀트리온(바이오)
   - 미국: NVDA/MSFT/AAPL/TSLA/META/GOOGL
   - 관리자 메뉴에서 편집 가능하게
3. 탭3 관리자 진입 버튼 추가
4. 탭4 진입 시 비번 요구 (1111 SHA-256: 0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c)
5. 관리자 메뉴에 주식 타일 종목 편집 추가

---

## 주요 설정값

| 항목 | 값 |
|---|---|
| 포트폴리오 비번 | 1111 |
| SHA-256 해시 | 0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c |
| 관리자 비번 | 1111 (동일) |
| 관리자 진입 | 로고 5번 탭 |
| Bong GS URL | https://script.google.com/macros/s/AKfycbw1W851igwvCuIzoghZyKfgkpqsgc2oPxNHrHsJhDLWhQbKHvlxQGTqMzLuImqnImHv/exec |
| AI 모델 | claude-haiku-4-5-20251001 |

---

## 파일 구조

```
invest-dash/
├── engines/
│   ├── market.py      완료 (us10y/us30y 포함)
│   ├── news.py        완료
│   ├── portfolio.py   완료
│   └── ai_summary.py  완료 (7섹션 프롬프트)
├── .github/workflows/
│   └── update.yml     완료
├── index.html         완료 (4탭, 수정 필요)
├── run.py             완료
├── requirements.txt   완료
├── data.json          자동생성
├── CLAUDE.md          완료
└── PROGRESS.md        이 파일
```

---

## 에러 이력 (반복 방지)

| 에러 | 원인 | 해결 |
|---|---|---|
| api_status_404 | 모델명 오류 | claude-haiku-4-5-20251001 사용 |
| WorksheetNotFound | 탭 이름 불일치 | 주식현황상세 (정확히) |
| Actions push 403 | workflow permissions | Read and write 설정 |

---

## 참고 레포

- https://github.com/Dalbonz/investment-news-bot
- https://github.com/Dalbonz/4-my-money
