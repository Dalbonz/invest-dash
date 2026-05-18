import ast
import os
import glob
import json
from shared.logger import get_logger

logger = get_logger("code_reviewer")

MAX_FUNC_LINES = 30
HARDCODE_PATTERNS = ["http://", "https://", "api_key", "password", "secret"]

def review_file(path: str) -> dict:
    result = {"path": path, "warnings": []}
    try:
        with open(path) as f:
            source = f.read()

        for pattern in HARDCODE_PATTERNS:
            if pattern in source.lower():
                result["warnings"].append(f"hardcode suspected: '{pattern}'")

        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                lines = node.end_lineno - node.lineno
                if lines > MAX_FUNC_LINES:
                    result["warnings"].append(f"func '{node.name}' too long: {lines} lines")

    except Exception as e:
        result["warnings"].append(f"parse error: {e}")

    result["ok"] = len(result["warnings"]) == 0
    return result

def run() -> dict:
    base = os.path.join(os.path.dirname(__file__), "..")
    py_files = glob.glob(f"{base}/**/*.py", recursive=True)
    py_files = [f for f in py_files if "test" not in f]
    results = [review_file(f) for f in py_files]
    passed = sum(1 for r in results if r["ok"])
    report = {"total": len(results), "passed": passed, "details": results}
    logger.info(f"Code review: {passed}/{len(results)} clean")
    return report

if __name__ == "__main__":
    result = run()
    print(json.dumps(result, ensure_ascii=False, indent=2))