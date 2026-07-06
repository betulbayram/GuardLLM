"""Framework integrations for GuardLLM.

These modules depend on optional third-party packages (FastAPI, LangChain,
OpenAI). They are imported lazily so that ``import guardllm`` never requires
them; the relevant extra is only needed when you actually use an integration:

    pip install "guardllm[api]"   # FastAPI middleware
"""

from __future__ import annotations

from typing import Any

__all__ = ["GuardMiddleware", "GuardedLLM", "OpenAIGuard", "guard_openai"]


def __getattr__(name: str) -> Any:  # PEP 562 lazy attribute loading
    if name == "GuardMiddleware":
        from guardllm.integrations.fastapi_middleware import GuardMiddleware

        return GuardMiddleware
    if name == "GuardedLLM":
        from guardllm.integrations.langchain_guard import GuardedLLM

        return GuardedLLM
    if name in ("OpenAIGuard", "guard_openai"):
        from guardllm.integrations import openai_guard

        return getattr(openai_guard, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
