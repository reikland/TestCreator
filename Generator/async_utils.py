import asyncio
from typing import Any, Awaitable


def run_coro(coro: Awaitable[Any]) -> Any:
    """
    Robust async runner for Streamlit contexts.

    - If no running loop: asyncio.run
    - If a loop exists (common under Streamlit): create a new loop and run coro
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
