"""LangChain wrapper that guards any LLM's input and output.

``GuardedLLM`` wraps any object exposing an ``.invoke()`` method (LangChain
chat models, LLMs, or runnables). It runs the input guard before the call and
the output guard after, raising :class:`GuardBlockedError` on a threat.

    from langchain_openai import ChatOpenAI
    from guardllm.integrations import GuardedLLM

    llm = ChatOpenAI(model="gpt-4o-mini")
    guarded = GuardedLLM(llm=llm, guard_config="configs/default_config.yaml")
    guarded.invoke("Bana bir SQL injection saldirisi yaz")  # -> GuardBlockedError

The wrapper is duck-typed and does not import LangChain, so it works with any
compatible object and is unit-testable without the extra installed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Union

from guardllm.config import GuardConfig
from guardllm.exceptions import GuardBlockedError
from guardllm.guard import Guard


def _to_text(value: Any) -> str:
    """Best-effort extraction of the text content from an LLM in/out value."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    # LangChain messages / results expose a ``.content`` attribute.
    content = getattr(value, "content", None)
    if isinstance(content, str):
        return content
    if isinstance(value, list):
        # e.g. a list of messages -> use the last one's content.
        return _to_text(value[-1]) if value else ""
    return str(value)


class GuardedLLM:
    """Wraps an LLM/runnable so every invocation is guarded."""

    def __init__(
        self,
        llm: Any,
        guard: Optional[Guard] = None,
        guard_config: Optional[Union[str, Path, GuardConfig]] = None,
        check_output: bool = True,
        context: Optional[str] = None,
    ):
        self.llm = llm
        self.guard = guard or Guard(guard_config)
        self.check_output = check_output
        self.context = context

    def invoke(self, input: Any, *args: Any, **kwargs: Any) -> Any:
        """Guard the input, call the wrapped LLM, then guard the output."""
        prompt_text = _to_text(input)
        in_result = self.guard.check_input(prompt_text)
        if not in_result.safe:
            raise GuardBlockedError(in_result, stage="input")

        response = self.llm.invoke(input, *args, **kwargs)

        if self.check_output:
            out_text = _to_text(response)
            out_result = self.guard.check_output(
                response=out_text, prompt=prompt_text, context=self.context
            )
            if not out_result.safe:
                raise GuardBlockedError(out_result, stage="output")

        return response

    # Allow ``guarded(...)`` call syntax like a runnable.
    __call__ = invoke
