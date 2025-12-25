import json
from typing import Any, Dict


def _strip_code_fences(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        lines = s.splitlines()
        lines = lines[1:]  # drop first fence line (``` or ```json)
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        s = "\n".join(lines).strip()
    return s


def parse_json_strictish(s: str) -> Dict[str, Any]:
    """
    Models sometimes return JSON inside code fences or with leading/trailing text.
    We attempt to recover the first top-level JSON object.
    """
    s = _strip_code_fences(s)

    try:
        return json.loads(s)
    except Exception:
        pass

    start = s.find("{")
    end = s.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Model did not return JSON.")

    candidate = s[start : end + 1]
    return json.loads(candidate)
