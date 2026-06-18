import os, json, requests

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
MODEL = 'claude-sonnet-4-6'

SYSTEM = """당신은 전문 투자 애널리스트입니다.
제공된 실제 시장 데이터만을 바탕으로 한국어로 상세하고 실용적인 투자 분석을 제공하세요.
데이터에 없는 내용은 절대 추가하지 마세요. JSON 형식으로만 응답하세요. 이모지 사용 금지."""

# 포트폴리오 종목명 → market.py 시세 키 매핑 (보유종목 액션아이템용)
NAME_TO_KEY = {
    '삼성전자': 'samsung', 'SK하이닉스': 'hynix', '한화에어로': 'hanwha', '한화에어로스페이스': 'hanwha',
    'LIG넥스원': 'lignex', '레인보우로보틱스': 'rainbow', '두산로보틱스': 'doosanrobo',
    '삼성바이오로직스': 'samsungbio', '셀트리온': 'celltrion',
    'NVIDIA': 'nvda', 'NVDA': 'nvda', 'Apple': 'aapl', 'AAPL': 'aapl',
    'Microsoft': 'msft', 'MSFT': 'msft', 'Tesla': 'tsla', 'TSLA': 'tsla',
    'Alphabet': 'googl', 'Google': 'googl', 'GOOGL': 'googl', 'Meta': 'meta', 'META': 'meta',
}

def run(market: dict, portfolio: dict) -> dict:
    if not ANTHROPIC_API_KEY:
        return {'error': 'no api key'}

    kr = {k: {'price': market[k]['price'], 'pct': market[k]['pct']}
          for k in ['kospi', 'kosdaq', 'usdkrw'] if k in market}
    us = {k: {'price': market[k]['price'], 'pct': market[k]['pct']}
          for k in ['sp500', 'nasdaq', 'dow', 'nvda', 'aapl', 'tsla', 'msft', 'meta', 'googl'] if k in market}
    bond = {k: {'price': market[k]['price'], 'pct': market[k]['pct']}
            for k in ['us10y', 'us30y'] if k in market}
    fx = {k: {'price': market[k]['price'], 'pct': market[k]['pct']}
          for k in ['usdkrw', 'dxy', 'jpykrw'] if k in market}
    commodity = {k: {'price': market[k]['price'], 'pct': market[k]['pct']}
                 for k in ['gold', 'oil', 'brent', 'silver'] if k in market}
    kr_stocks = {k: {'price': market[k]['price'], 'pct': market[k]['pct']}
                 for k in ['samsung', 'hynix', 'hanwha', 'samsungbio', 'celltrion'] if k in market}

    my_stocks = {}
    for h in portfolio.get('holdings', []):
        name = (h.get('종목명') or '').strip()
        key = NAME_TO_KEY.get(name)
        if key and key in market:
            my_stocks[name] = {'price': market[key]['price'], 'pct': market[key]['pct']}

    holdings_instruction = (
        '"holdings": "내 보유종목 액션:\\n1. [종목명] - [현재 시세 기반 액션, 구체적 수치 포함]\\n2. ...",'
        if my_stocks else
        '"holdings": "",'
    )

    prompt = f"""오늘의 실제 시장 데이터:

한국 지수: {json.dumps(kr, ensure_ascii=False)}
미국 지수/주요주: {json.dumps(us, ensure_ascii=False)}
미국채금리: {json.dumps(bond, ensure_ascii=False)}
환율: {json.dumps(fx, ensure_ascii=False)}
원자재: {json.dumps(commodity, ensure_ascii=False)}
국내 주요주: {json.dumps(kr_stocks, ensure_ascii=False)}
내 보유종목 시세: {json.dumps(my_stocks, ensure_ascii=False)}
포트폴리오 종목수: {portfolio.get('count', 0)}개

위 데이터만 바탕으로 아래 JSON 형식으로 응답하세요. 각 섹션은 충분히 상세하게, 최소 4~5개 항목으로 작성하세요.
각 항목은 반드시 줄바꿈(\\n)으로 구분된 번호 리스트 형식으로 작성하고, 각 항목은 1~2문장으로 구체적으로 설명하세요.
예시: "1. **핵심수치** 상세 설명 1~2문장\\n2. **핵심수치** 상세 설명 1~2문장"
중요 수치/종목명은 **굵게** 표시. 이모지 사용 금지. 데이터에 없는 종목/지수 언급 금지.
sectors 항목은 "상승 섹터:" "하락/주의 섹터:" "중립 관망:" 각 카테고리 제목을 한 번만 쓰고 그 아래 번호 리스트를 붙이세요 (항목마다 카테고리명 반복 금지).
holdings 항목은 "내 보유종목 시세"에 데이터가 있을 때만 작성하고, 비어있으면 빈 문자열로 두세요. 보유종목이 아닌 종목은 절대 언급하지 마세요.

{{
  "summary": "오늘 시장 핵심 한줄 요약 (수치 포함, 2문장)",
  "kr": "한국 시장 분석:\\n1. 코스피/코스닥 수준과 방향 (구체적 수치 포함, 1~2문장)\\n2. 환율 영향 분석 (달러/원 수준과 주식시장 영향)\\n3. 국내 주요 종목 흐름 (위 데이터 기반)\\n4. 수급/투자자 동향 추정\\n5. 오늘 주목할 포인트",
  "us": "미국 시장 분석:\\n1. 주요 지수 동향 (다우/S&P500/나스닥 각각 수치 포함)\\n2. 기술주 흐름 (나스닥/빅테크 분석)\\n3. 미국채 금리 수준과 시장 영향\\n4. 달러 인덱스 영향\\n5. 한국 시장에 미칠 영향",
  "sectors": "상승 섹터:\\n1. [섹터명] - [이유, 수치 포함, 1~2문장]\\n2. [섹터명] - [이유, 수치 포함]\\n3. [섹터명] - [이유, 수치 포함]\\n하락/주의 섹터:\\n1. [섹터명] - [이유, 수치 포함]\\n2. [섹터명] - [이유, 수치 포함]\\n중립 관망:\\n1. [섹터명] - [이유]\\n2. [섹터명] - [이유]",
  {holdings_instruction}
  "picks": "관심 분야 (데이터 기반):\\n1. [분야/종목]: [이유 1~2문장]\\n2. [분야/종목]: [이유 1~2문장]\\n3. [분야/종목]: [이유 1~2문장]\\n4. [분야/종목]: [이유 1~2문장]",
  "do": "오늘 할 것:\\n1. [구체적 액션, 1~2문장]\\n2. [구체적 액션]\\n3. [구체적 액션]\\n4. [구체적 액션]",
  "dont": "오늘 하지 말 것:\\n1. [주의사항, 1~2문장]\\n2. [주의사항]\\n3. [주의사항]\\n4. [주의사항]",
  "risk_level": 3
}}"""

    try:
        res = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key': ANTHROPIC_API_KEY,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json'
            },
            json={
                'model': MODEL,
                'max_tokens': 7000,
                'system': SYSTEM,
                'messages': [{'role': 'user', 'content': prompt}]
            },
            timeout=75
        )

        if res.status_code != 200:
            print(f'API 에러 {res.status_code}: {res.text[:200]}')
            return {'error': f'api_status_{res.status_code}'}

        data = res.json()
        if 'content' not in data:
            print(f'AI 시황 오류: no_content / {str(data)[:200]}')
            return {'error': 'no_content'}

        if data.get('stop_reason') == 'max_tokens':
            print('AI 시황 경고: max_tokens로 응답이 잘림 (JSON 파싱 실패 가능)')

        text = data['content'][0]['text']
        start = text.find('{')
        end = text.rfind('}') + 1
        if start == -1:
            print(f'AI 시황 오류: no_json / raw: {text[:200]}')
            return {'error': 'no_json', 'raw': text[:200]}

        return json.loads(text[start:end])

    except json.JSONDecodeError as e:
        print(f'AI 시황 오류: json_parse: {e}')
        return {'error': f'json_parse: {e}'}
    except Exception as e:
        print(f'AI 시황 오류: {e}')
        return {'error': str(e)}

if __name__ == '__main__':
    print(json.dumps(run({}, {}), ensure_ascii=False, indent=2))
