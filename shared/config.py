import os
from dotenv import load_dotenv

load_dotenv()

def _get(key: str, default: str = "") -> str:
    try:
        import streamlit as st
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)

ANTHROPIC_API_KEY = _get("ANTHROPIC_API_KEY")
GOOGLE_SHEETS_ID = _get("GOOGLE_SHEETS_ID")

CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_MAX_TOKENS = 1000

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CACHE_DIR = os.path.join(DATA_DIR, "cache")
RAW_DIR = os.path.join(DATA_DIR, "raw")