import json
import os
from shared.models import EngineOutput

def save_output(engine_name: str, data: dict, output_path: str) -> None:
    output = EngineOutput(engine=engine_name, data=data)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output.to_dict(), f, ensure_ascii=False, indent=2)

def load_output(output_path: str) -> dict:
    if not os.path.exists(output_path):
        return {}
    with open(output_path, "r", encoding="utf-8") as f:
        return json.load(f)

def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    return a / b if b != 0 else default