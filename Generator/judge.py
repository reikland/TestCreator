from typing import Any, Dict, List

from openai import OpenAI

from ftg.parsing import parse_json_strictish
from ftg.prompts import build_rank_prompt
from ftg.types import RankedTopic


def rank_topics(
    client: OpenAI,
    judge_model: str,
    topics: List[str],
    top_k: int,
) -> List[RankedTopic]:
    prompt = build_rank_prompt(topics=topics, top_k=top_k)

    response = client.chat.completions.create(
        model=judge_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    content = response.choices[0].message.content or ""
    data = parse_json_strictish(content)

    top = data.get("top_topics")
    if not isinstance(top, list) or not top:
        raise ValueError("Judge model returned invalid JSON: missing 'top_topics' list.")

    cleaned: List[RankedTopic] = []
    for i, item in enumerate(top, start=1):
        if not isinstance(item, dict):
            continue
        topic = str(item.get("topic") or "").strip()
        if not topic:
            continue
        cleaned.append({"rank": i, "topic": topic})

    return cleaned[:top_k]
