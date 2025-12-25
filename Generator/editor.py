from typing import Any, Dict, List

from openai import OpenAI

from ftg.parsing import parse_json_strictish
from ftg.prompts import build_edit_prompt
from ftg.types import RankedTopic


def edit_topics_with_llm(
    client: OpenAI,
    model_name: str,
    topics: List[RankedTopic],
    user_prompt: str,
) -> List[RankedTopic]:
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": build_edit_prompt(topics, user_prompt)}],
        temperature=0.2,
    )

    content = response.choices[0].message.content or ""
    data = parse_json_strictish(content)

    edited_topics = data.get("top_topics")
    if not isinstance(edited_topics, list):
        raise ValueError("Edited topics JSON invalid: missing 'top_topics' list.")

    if len(edited_topics) != len(topics):
        raise ValueError("Edited topics count does not match the original list.")

    n = len(topics)
    provided_ranks = []
    cleaned: List[RankedTopic] = []

    for item in edited_topics:
        if not isinstance(item, dict):
            raise ValueError("Edited topics must be a list of objects.")
        r = item.get("rank")
        t = str(item.get("topic") or "").strip()
        if not t:
            raise ValueError("All edited topics must include a non-empty 'topic' field.")
        provided_ranks.append(r)
        cleaned.append({"rank": int(r), "topic": t})

    expected = set(range(1, n + 1))
    try:
        provided = set(int(x) for x in provided_ranks)
    except Exception:
        raise ValueError("Edited topics 'rank' must be integers 1..N.")

    if provided != expected:
        raise ValueError("Edited topics must include every rank exactly once (1..N).")

    cleaned.sort(key=lambda x: int(x["rank"]))
    for i in range(n):
        cleaned[i]["rank"] = i + 1

    return cleaned
