"""Exception types raised by GuardLLM integrations."""

from __future__ import annotations

from guardllm.result import GuardResult


class GuardLLMError(Exception):
    """Base class for all GuardLLM errors."""


class GuardBlockedError(GuardLLMError):
    """Raised when a guard blocks input or output.

    Carries the originating :class:`~guardllm.result.GuardResult` so callers
    can inspect the threat, confidence and details.
    """

    def __init__(self, result: GuardResult, stage: str = "input"):
        self.result = result
        self.stage = stage
        message = (
            f"{stage.capitalize()} blocked - {result.threat} "
            f"(confidence: {result.confidence:.2f})"
        )
        super().__init__(message)
