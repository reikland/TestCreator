import os
from openai import OpenAI


def build_openrouter_client(openrouter_api_key: str) -> OpenAI:
    # Ensure we don't accidentally use OpenAI_API_KEY while pointing to OpenRouter.
    os.environ["OPENROUTER_API_KEY"] = openrouter_api_key
    os.environ.pop("OPENAI_API_KEY", None)
    os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")

    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key,
    )


def normalize_openai_model_name(model_name: str) -> str:
    # OpenAI client hitting OpenRouter expects model without "openrouter/" prefix
    return model_name.removeprefix("openrouter/").strip()


def normalize_litellm_model_name(model_name: str) -> str:
    # forecasting_tools TopicGenerator expects "openrouter/<provider/model>"
    cleaned = model_name.strip()
    return cleaned if cleaned.startswith("openrouter/") else f"openrouter/{cleaned}"
