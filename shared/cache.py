import json
import os
import time
from shared.config import CACHE_DIR

os.makedirs(CACHE_DIR, exist_ok=True)

def _cache_path(key: str) -> str:
    return os.path.join(CACHE_DIR, f"{key}.json")

def get(key: str, ttl_seconds: int = 3600) -> dict | None:
    path = _cache_path(key)
    if not os.path.exists(path):
        return None
    if time.time() - os.path.getmtime(path) > ttl_seconds:
        return None
    with open(path, "r") as f:
        return json.load(f)

def set(key: str, data: dict) -> None:
    with open(_cache_path(key), "w") as f:
        json.dump(data, f)

def invalidate(key: str) -> None:
    path = _cache_path(key)
    if os.path.exists(path):
        os.remove(path)