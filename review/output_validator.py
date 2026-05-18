import json
import os
import glob
from shared.logger import get_logger

logger = get_logger("output_validator")

REQUIRED_FIELDS = ["engine", "version", "timestamp", "status", "data"]

def validate_file(path: str) -> dict:
    result = {"path": path, "ok": False, "errors": []}
    try:
        with open(path) as f:
            data = json.load(f)
        if data == {}:
            result["errors"].append("empty output")
            return result
        for field in REQUIRED_FIELDS:
            if field not in data:
                result["errors"].append(f"missing field: {field}")
        if data.get("status") == "error":
            result["errors"].append(f"engine error: {data.get('error', '')}")
        result["ok"] = len(result["errors"]) == 0
    except Exception as e:
        result["errors"].append(str(e))
    return result

def run() -> dict:
    base = os.path.join(os.path.dirname(__file__), "..", "engines")
    outputs = glob.glob(f"{base}/**/output.json", recursive=True)
    results = [validate_file(p) for p in outputs]
    passed = sum(1 for r in results if r["ok"])
    report = {"total": len(results), "passed": passed, "failed": len(results) - passed, "details": results}

    report_path = os.path.join(os.path.dirname(__file__), "review_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Validation: {passed}/{len(results)} passed")
    return report

if __name__ == "__main__":
    result = run()
    print(json.dumps(result, ensure_ascii=False, indent=2))