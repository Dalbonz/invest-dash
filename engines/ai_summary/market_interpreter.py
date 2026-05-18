import json
import os
from engines.ai_summary.claude_client import ask
from engines.ai_summary.prompt_builder import build_market_prompt
from shared.utils import save_output
from shared.logger import get_logger

logger = get_logger("market_interpreter")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "output.json")

def parse_response(text: str) -> dict:
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end])
    except Exception:
        return {"raw": text, "parse_error": True}

def run() -> dict:
    system, prompt = build_market_prompt()
    response = ask(prompt, system)
    data = parse_response(response)
    save_output("market_interpreter", data, OUTPUT_PATH)
    logger.info("AI summary generated")
    return data

if __name__ == "__main__":
    result = run()
    print(json.dumps(result, ensure_ascii=False, indent=2))