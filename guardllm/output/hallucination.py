"""Hallucination / faithfulness detector.

Given a model ``response`` and the ``context`` it was supposed to be grounded
in, estimate how faithful the response is to that context.

The default method is a dependency-free lexical baseline:

* content-token overlap between response and context, and
* a numeric-consistency check (numbers asserted in the response that do not
  appear in the context are a strong hallucination signal — e.g. a population
  of "15 milyon" when the context says "5.8 milyon").

An NLI-model backend (``method="nli"`` with ``guardllm[ml]`` installed) can be
plugged in later for stronger semantic entailment scoring.
"""

from __future__ import annotations

import re

from guardllm.config import HallucinationConfig
from guardllm.result import GuardResult

_TOKEN_RE = re.compile(r"[0-9]+(?:[.,][0-9]+)?|[a-zçğıöşü]+", re.IGNORECASE)
_NUM_RE = re.compile(r"[0-9]+(?:[.,][0-9]+)?")

# Minimal TR+EN stopword set — enough to stop trivial filler from inflating overlap.
_STOPWORDS: set[str] = {
    # Turkish
    "ve", "ile", "bir", "bu", "şu", "o", "da", "de", "ki", "mi", "mı", "mu", "mü",
    "için", "gibi", "kadar", "daha", "çok", "ama", "fakat", "ise", "en", "the",
    # English
    "a", "an", "of", "to", "in", "on", "is", "are", "was", "were", "and", "or",
    "for", "with", "as", "at", "by", "it", "that", "this",
}


def _content_tokens(text: str) -> list[str]:
    return [t for t in _TOKEN_RE.findall(text.lower()) if t not in _STOPWORDS]


def _numbers(text: str) -> set[str]:
    # Normalise decimal separators so "5.8" and "5,8" compare equal.
    return {n.replace(",", ".") for n in _NUM_RE.findall(text)}


class HallucinationDetector:
    """Scores the faithfulness of a response against a reference context."""

    name = "hallucination"

    def __init__(self, config: HallucinationConfig | None = None):
        self.config = config or HallucinationConfig()

    def check(self, response: str, context: str | None = None) -> GuardResult:
        """Return a result. ``config.threshold`` is the *minimum* faithfulness.

        Without a ``context`` the detector cannot judge grounding and returns a
        safe (but low-confidence) result.
        """
        if not self.config.enabled or not response:
            return GuardResult.safe_result(detector=self.name)
        if not context:
            return GuardResult.safe_result(
                detector=self.name,
                confidence=0.5,
                details="No context provided; grounding not evaluated",
            )

        resp_tokens = _content_tokens(response)
        ctx_tokens = set(_content_tokens(context))
        if not resp_tokens:
            return GuardResult.safe_result(detector=self.name)

        supported = [t for t in resp_tokens if t in ctx_tokens]
        overlap = len(supported) / len(resp_tokens)

        # Numeric consistency: any number claimed but not present in context.
        resp_nums = _numbers(response)
        ctx_nums = _numbers(context)
        unsupported_nums = resp_nums - ctx_nums

        faithfulness = overlap
        if unsupported_nums:
            # Unsupported figures sharply reduce faithfulness.
            faithfulness = min(faithfulness, 0.4)

        if faithfulness >= self.config.threshold:
            return GuardResult.safe_result(
                detector=self.name,
                confidence=faithfulness,
                details=f"Faithful to context (score={faithfulness:.2f})",
                metadata={"faithfulness": round(faithfulness, 3)},
            )

        confidence = 1.0 - faithfulness
        detail = f"Low faithfulness to context (score={faithfulness:.2f})"
        if unsupported_nums:
            detail += f"; unsupported figures: {', '.join(sorted(unsupported_nums))}"
        return GuardResult.threat_result(
            threat="hallucination",
            confidence=confidence,
            detector=self.name,
            details=detail,
            metadata={
                "faithfulness": round(faithfulness, 3),
                "overlap": round(overlap, 3),
                "unsupported_numbers": sorted(unsupported_nums),
                "method": self.config.method,
            },
        )
