"""Jailbreak detector (rule-based, Turkish + English).

Catches persona/roleplay tricks (DAN, "act as an evil AI"), explicit
"no restrictions" phrasing, and common exploit templates. Embedding-based
similarity to a corpus of known jailbreaks can be added via ``guardllm[ml]``.
"""

from __future__ import annotations

from guardllm.config import JailbreakConfig
from guardllm.result import GuardResult
from guardllm.utils import patterns


class JailbreakDetector:
    """Detects attempts to bypass safety via roleplay/persona/encoding."""

    name = "jailbreak"

    def __init__(self, config: JailbreakConfig | None = None):
        self.config = config or JailbreakConfig()

    def check(self, text: str) -> GuardResult:
        if not self.config.enabled or not text:
            return GuardResult.safe_result(detector=self.name)

        matched: list[str] = []
        for rule_name, pattern in patterns.JAILBREAK_PATTERNS:
            if pattern.search(text):
                matched.append(rule_name)

        if not matched:
            return GuardResult.safe_result(
                detector=self.name, details="No jailbreak pattern matched"
            )

        confidence = min(0.99, 0.82 + 0.08 * (len(matched) - 1))
        if confidence < self.config.threshold:
            return GuardResult.safe_result(
                detector=self.name,
                confidence=1.0 - confidence,
                details=f"Below threshold ({confidence:.2f} < {self.config.threshold})",
                metadata={"weak_matches": matched},
            )

        return GuardResult.threat_result(
            threat="jailbreak",
            confidence=confidence,
            detector=self.name,
            details=f"Jailbreak pattern(s) detected: {', '.join(matched)}",
            metadata={"matched_rules": matched},
        )
