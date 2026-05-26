import os, json, requests

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
MODEL = 'claude-haiku-4-5-20251001'

SYSTEM = """당신은 전문 투자 애널리스트입니다.
제공된 시장 데이터를 바탕으로 한국어로 상세하고 실용적인 투자 분석을 제공하세요.
JSON 형식으로만 응답하세요. 이모지 사용 금지."""

def run(market: dict, portfolio: dict) -> dict:
    if not ANTHROPIC_API_KEY:
        return {'error': 'no api key'}

    kr = {k: {'price': market[k]['price'], 'pct': market[k]['pct']}
          for k in ['kospi', 'kosdaq', 'usdkrw'] if k in market}
    us = {k: {'price': market[k]['price'], 'pct': market[k]['pct']}
          for k in ['sp500', 'nasdaq', 'nvda', 'aapl', 'tsla', 'msft'] if k in market}
    bond = {k: {'price': market[k]['price'], 'pct': market[k]['pct']}
            for k in ['us10y', 'us30y'] if k in market}
    fx = {k: {'price': market[k]['price'], 'pct': market[k]['pct']}
          for k in ['usdkrw', 'dxy'] if k in market}

    prompt = f"""오늘의 시장 데이터:

한국: {json.dumps(kr, ensure_ascii=False)}
미국: {json.dumps(us, ensure_ascii=False)}
미국채: {json.dumps(bond, ensure_ascii=False)}
환율: {json.dumps(fx, ensure_ascii=False)}
보유종목수: {portfolio.get('count', 0)}개

아래 JSON 형식으로만 응답 (이모지 사용 금지, 구체적인 수치와 종목명 포함):
{{
  "summary": "오늘 시장 한줄 핵심 요약",
  "kr": "한국 시장 상세 분석 (코스피/코스닥 동향, 외국인/기관 수급, 주요 섹터 흐름 포함, 3~4문장)",
  "us": "미국 시장 상세 분석 (주요 지수 동향, 기술주/가치주 흐름, 채권금리 영향 포함, 3~4문장)",
  "sectors": "주목 섹터 분석 (상승/하락 섹터 각 1~2개, 이유 포함)",
  "picks": "추천 분야 및 종목 (구체적 종목명 2~3개, 각 추천 이유 1문장씩)",
  "do": "오늘 해야 할 것 (구체적 액션 2~3가지)",
  "dont": "오늘 하지 말아야 할 것 (구체적 주의사항 2~3가지)",
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
                'max_tokens': 1500,
                'system': SYSTEM,
                'messages': [{'role': 'user', 'content': prompt}]
            },
            timeout=30
        )

        if res.status_code != 200:
            print(f'API 에러 {res.status_code}: {res.text[:200]}')
            return {'error': f'api_status_{res.status_code}'}

        data = res.json()
        if 'content' not in data:
            return {'error': 'no_content'}

        text = data['content'][0]['text']
        start = text.find('{')
        end = text.rfind('}') + 1
        if start == -1:
            return {'error': 'no_json', 'raw': text[:200]}

        return json.loads(text[start:end])

    except json.JSONDecodeError as e:
        return {'error': f'json_parse: {e}'}
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    print(json.dumps(run({}, {}), ensure_ascii=False, indent=2))
