from typing import Any, List

from forecasting_tools import TopicGenerator

from ftg.async_utils import run_coro
from ftg.llm import normalize_litellm_model_name


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def to_text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        return str(value.get("topic") or value.get("text") or "").strip()
    for attr in ("topic", "text", "content", "title"):
        if hasattr(value, attr):
            attr_value = getattr(value, attr)
            if isinstance(attr_value, str):
                return attr_value.strip()
    return ""


async def _fetch_batch(gen_model: str, count: int, additional_instructions: str):
    return await TopicGenerator.generate_random_topic(
        model=normalize_litellm_model_name(gen_model),
        number_of_topics=count,
        additional_instructions=additional_instructions,
    )


async def _generate_topics_async(
    gen_model: str,
    target_n: int,
    batch_n: int,
    max_rounds: int,
    additional_instructions: str,
) -> List[str]:
    seen = set()
    out: List[str] = []

    for _ in range(max_rounds):
        remaining = target_n - len(out)
        if remaining <= 0:
            break

        ask = max(batch_n, remaining)  # oversample to compensate dedup
        batch = await _fetch_batch(gen_model, ask, additional_instructions)
        batch = batch if isinstance(batch, list) else [batch]

        added = 0
        for item in batch:
            topic = to_text(item)
            if not topic:
                continue
            key = normalize(topic)
            if key in seen:
                continue
            seen.add(key)
            out.append(topic)
            added += 1
            if len(out) >= target_n:
                break

        if added == 0:
            break

    return out


def generate_topics(
    gen_model: str,
    target_n: int,
    batch_n: int,
    max_rounds: int,
    additional_instructions: str,
) -> List[str]:
    return run_coro(
        _generate_topics_async(
            gen_model=gen_model,
            target_n=target_n,
            batch_n=batch_n,
            max_rounds=max_rounds,
            additional_instructions=additional_instructions,
        )
    )
