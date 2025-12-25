import json
from typing import Any, Dict, List


def build_rank_prompt(topics: List[str], top_k: int) -> str:
    return f"""
You are a professional forecasting editor.

Select the {top_k} most interesting forecasting questions from the list below.

Criteria:
- High epistemic uncertainty
- Clear resolution criteria
- Real-world importance

Return STRICT JSON:

{{
  "top_topics": [
    {{
      "rank": 1,
      "topic": "..."
    }}
  ]
}}

Topics:
{json.dumps(topics, ensure_ascii=False, indent=2)}
""".strip()


def _format_topics(topics: List[Dict[str, Any]]) -> str:
    return json.dumps(topics, ensure_ascii=False, indent=2)


def build_edit_prompt(topics: List[Dict[str, Any]], user_prompt: str) -> str:
    n = len(topics)
    return f"""
You are a professional forecasting editor.

You receive a ranked list of forecasting questions. Apply the user's requested edits while keeping the questions concrete, time-bounded, and forecastable.
Maintain exactly {n} entries and keep the ranks sequential starting at 1.
Avoid duplicates or vague phrasing.

Return STRICT JSON:

{{
  "top_topics": [
    {{
      "rank": 1,
      "topic": "..."
    }}
  ]
}}

Existing ranked topics:
{_format_topics(topics)}

User request:
{user_prompt}
""".strip()
