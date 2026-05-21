import os, json, requests

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

SYSTEM = "당신은 투자 전문 애널리스트입니다. 수치 데이터를 바탕으로 한국어로 실용적인 시장 해석을 제공하세요. JSON 형식으로만 응답하세요."

def run(market: dict, portfolio: dict) -> dict:
    if not ANTHROPIC_API_KEY:
        return {'error': 'no api key'}

    kr = {k: market[k] for k in ['kospi','kosdaq','usdkrw'] if k in market}
    us = {k: market[k] for k in ['sp500','nasdaq','nvda','aapl'] if k in market}

    prompt = f"""시장 데이터:
KR: {json.dumps(kr, ensure_ascii=False)}
US: {json.dumps(us, ensure_ascii=False)}
포트폴리오 종목수: {portfolio.get('count', 0)}

아래 JSON으로만 응답:
{{
  "market_summary": "시장 전체 요약 2문장",
  "kr_signal": "한국 시장 핵심 시그널",
  "us_signal": "미국 시장 핵심 시그널",
  "risk_level": 3,
  "action_hint": "단기 액션 힌트 1문장",
  "key_signals": ["신호1", "신호2", "신호3"]
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
                'model': 'claude-haiku-4-5-20251001',
                'max_tokens': 1000,
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
            print(f'응답에 content 없음: {json.dumps(data)[:200]}')
            return {'error': 'no_content_in_response'}

        text = data['content'][0]['text']
        start = text.find('{')
        end = text.rfind('}') + 1
        if start == -1:
            return {'error': 'no_json_in_response', 'raw': text[:200]}

        return json.loads(text[start:end])

    except json.JSONDecodeError as e:
        return {'error': f'json_parse: {e}'}
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    print(json.dumps(run({}, {}), ensure_ascii=False, indent=2))