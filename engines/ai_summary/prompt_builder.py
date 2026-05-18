import json
import os
from shared.utils import load_output

ENGINE_OUTPUTS = {
    "market": os.path.join(os.path.dirname(__file__), "../market/output.json"),
    "portfolio": os.path.join(os.path.dirname(__file__), "../portfolio/output.json"),
    "theme": os.path.join(os.path.dirname(__file__), "../theme/output.json"),
}

SYSTEM_PROMPT = """당신은 투자 분석 전문가입니다.
주어진 수치 데이터를 바탕으로 한국어로 간결하고 실용적인 시장 해석을 제공하세요.
계산은 하지 말고, 해석과 인사이트만 제공하세요.
JSON 형식으로 응답하세요."""

def build_market_prompt() -> tuple[str, str]:
    data = {k: load_output(v) for k, v in ENGINE_OUTPUTS.items()}
    user_prompt = f"""다음 데이터를 분석해주세요:

{json.dumps(data, ensure_ascii=False, indent=2)}

아래 JSON 형식으로 응답:
{{
  "market_summary": "시장 전체 요약 (2~3문장)",
  "key_signals": ["신호1", "신호2", "신호3"],
  "portfolio_comment": "포트폴리오 관련 코멘트",
  "risk_level": 1~5,
  "action_hint": "단기 액션 힌트"
}}"""
    return SYSTEM_PROMPT, user_prompt