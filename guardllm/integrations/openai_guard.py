"""OpenAI client wrapper that guards chat completions.

``OpenAIGuard`` wraps an OpenAI client (v1 SDK) and guards the
``chat.completions.create`` call: it checks the user message before the call
and the assistant response after.

    from openai import OpenAI
    from guardllm.integrations import OpenAIGuard

    guarded = OpenAIGuard(OpenAI())
    resp = guarded.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Merhaba"}],
    )

Duck-typed: the OpenAI SDK is not imported here, so this is testable with a
stub client.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Union

from guardllm.config import GuardConfig
from guardllm.exceptions import GuardBlockedError
from guardllm.guard import Guard


def _last_user_message(messages: list[dict]) -> str:
    for msg in reversed(messages):
        if isinstance(msg, dict) and msg.get("role") == "user":
            content = msg.get("content", "")
            return content if isinstance(content, str) else str(content)
    return ""


def _response_text(response: Any) -> str:
    """Extract assistant text from an OpenAI ChatCompletion response."""
    try:
        return response.choices[0].message.content or ""
    except (AttributeError, IndexError, TypeError):
        # dict-shaped response fallback
        try:
            return response["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError):
            return ""


class OpenAIGuard:
    """Guards an OpenAI client's chat completions."""

    def __init__(
        self,
        client: Any,
        guard: Optional[Guard] = None,
        guard_config: Optional[Union[str, Path, GuardConfig]] = None,
        check_output: bool = True,
        context: Optional[str] = None,
    ):
        self.client = client
        self.guard = guard or Guard(guard_config)
        self.check_output = check_output
        self.context = context

    def create(self, *, messages: list[dict], **kwargs: Any) -> Any:
        """Guarded drop-in for ``client.chat.completions.create``."""
        prompt = _last_user_message(messages)
        in_result = self.guard.check_input(prompt)
        if not in_result.safe:
            raise GuardBlockedError(in_result, stage="input")

        response = self.client.chat.completions.create(messages=messages, **kwargs)

        if self.check_output:
            out_result = self.guard.check_output(
                response=_response_text(response), prompt=prompt, context=self.context
            )
            if not out_result.safe:
                raise GuardBlockedError(out_result, stage="output")

        return response


def guard_openai(
    client: Any,
    guard_config: Optional[Union[str, Path, GuardConfig]] = None,
    **kwargs: Any,
) -> OpenAIGuard:
    """Convenience factory: ``guard_openai(OpenAI())``."""
    return OpenAIGuard(client, guard_config=guard_config, **kwargs)
