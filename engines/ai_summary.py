import os, json, requests

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
MODEL = 'claude-haiku-4-5-20251001'

SYSTEM = """당신은 개인 투자자를 위한 친근한 시장 해설가입니다.
복잡한 금융 용어 대신 누구나 이해할 수 있는 쉬운 말로 설명하세요.
JSON 형식으로만 응답하세요."""

def run(market: dict, portfolio: dict) -> dict:
    if not ANTHROPIC_API_KEY:
        return {'error': 'no api key'}

    kr = {k: {'price': market[k]['price'], 'pct': market[k]['pct']}
          for k in ['kospi', 'kosdaq', 'usdkrw'] if k in market}
    us = {k: {'price': market[k]['price'], 'pct': market[k]['pct']}
          for k in ['sp500', 'nasdaq', 'nvda', 'aapl', 'tsla', 'msft'] if k in market}
    fx = {k: {'price': market[k]['price'], 'pct': market[k]['pct']}
          for k in ['usdkrw', 'jpykrw', 'dxy'] if k in market}

    prompt = f"""오늘의 시장 데이터입니다:

한국: {json.dumps(kr, ensure_ascii=False)}
미국: {json.dumps(us, ensure_ascii=False)}
환율: {json.dumps(fx, ensure_ascii=False)}
보유종목수: {portfolio.get('count', 0)}개

아래 JSON 형식으로만 응답하세요 (쉬운 말로, 이모지 포함):
{{
  "summary": "📌 오늘 한 줄 요약 (일반인도 이해하는 쉬운 말)",
  "kr": "🇰🇷 한국 시장 설명 (2~3문장, 쉽게)",
  "us": "🇺🇸 미국 시장 설명 (2~3문장, 쉽게)",
  "pick": "🛒 오늘 주목할 종목/섹터 (이유 포함, 2~3개)",
  "warn": "⚠️ 오늘 조심할 것 (쉬운 말로)",
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
                'max_tokens': 1200,
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
            print(f'content 없음: {json.dumps(data)[:200]}')
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
