"""Prompt injection detector (rule-based, Turkish + English).

An optional ML classifier can be layered on top later via the ``guardllm[ml]``
extra; the rule-based layer works with zero heavy dependencies and provides a
strong, fast baseline.
"""

from __future__ import annotations

from guardllm.config import InjectionConfig
from guardllm.result import GuardResult
from guardllm.utils import patterns


class InjectionDetector:
    """Detects attempts to override, ignore, or leak system instructions."""

    name = "prompt_injection"

    def __init__(self, config: InjectionConfig | None = None):
        self.config = config or InjectionConfig()

    def check(self, text: str) -> GuardResult:
        """Return a :class:`GuardResult` for ``text``.

        Each matched rule contributes to the confidence; multiple independent
        matches push confidence higher (capped at 0.99).
        """
        if not self.config.enabled or not text:
            return GuardResult.safe_result(detector=self.name)

        matched: list[str] = []
        for rule_name, pattern in patterns.INJECTION_PATTERNS:
            if pattern.search(text):
                matched.append(rule_name)

        if not matched:
            return GuardResult.safe_result(
                detector=self.name, details="No injection pattern matched"
            )

        # Base 0.85 for a single hit, +0.07 per additional distinct rule.
        confidence = min(0.99, 0.85 + 0.07 * (len(matched) - 1))
        if confidence < self.config.threshold:
            return GuardResult.safe_result(
                detector=self.name,
                confidence=1.0 - confidence,
                details=f"Below threshold ({confidence:.2f} < {self.config.threshold})",
                metadata={"weak_matches": matched},
            )

        return GuardResult.threat_result(
            threat="prompt_injection",
            confidence=confidence,
            detector=self.name,
            details=f"Injection pattern(s) detected: {', '.join(matched)}",
            metadata={"matched_rules": matched},
        )
