import anthropic
from shared.config import ANTHROPIC_API_KEY, CLAUDE_MODEL, CLAUDE_MAX_TOKENS
from shared.logger import get_logger

logger = get_logger("claude_client")
_client = None

def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client

def ask(prompt: str, system: str = "") -> str:
    try:
        msgs = [{"role": "user", "content": prompt}]
        kwargs = {"model": CLAUDE_MODEL, "max_tokens": CLAUDE_MAX_TOKENS, "messages": msgs}
        if system:
            kwargs["system"] = system
        response = _get_client().messages.create(**kwargs)
        return response.content[0].text
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return ""