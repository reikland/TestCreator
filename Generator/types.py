from dataclasses import dataclass
from typing import Any, Dict, List, TypedDict


class RankedTopic(TypedDict):
    rank: int
    topic: str


@dataclass(frozen=True)
class AppRunConfig:
    openrouter_api_key: str
    gen_model: str
    judge_model: str
    target_n: int
    top_k: int
    batch_n: int
    max_rounds: int
    additional_instructions: str
