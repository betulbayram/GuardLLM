"""GuardResult — the single result type returned by every guard check.

A :class:`GuardResult` is intentionally lightweight (a dataclass, not a
Pydantic model) because it sits on the hot path of every LLM request.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class GuardResult:
    """Outcome of a single guard check.

    Attributes:
        safe: ``True`` when no threat was detected above threshold.
        threat: Machine-readable threat type (e.g. ``"prompt_injection"``,
            ``"jailbreak"``, ``"pii_leak"``, ``"hallucination"``,
            ``"toxicity"``). ``None`` when ``safe`` is ``True``.
        confidence: Detector confidence in ``[0.0, 1.0]``. For a safe result
            this is the confidence that the content is safe.
        details: Human-readable explanation of the decision.
        redacted: Text with detected PII masked/redacted, when applicable.
        detector: Name of the detector that produced this result.
        metadata: Free-form extra data (matched patterns, scores, spans, ...).
    """

    safe: bool
    threat: Optional[str] = None
    confidence: float = 0.0
    details: str = ""
    redacted: Optional[str] = None
    detector: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __bool__(self) -> bool:
        """Truthiness follows safety: ``if guard.check_input(x): ...``."""
        return self.safe

    @property
    def blocked(self) -> bool:
        """Convenience inverse of :attr:`safe`."""
        return not self.safe

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict (JSON-friendly)."""
        return {
            "safe": self.safe,
            "threat": self.threat,
            "confidence": round(self.confidence, 4),
            "details": self.details,
            "redacted": self.redacted,
            "detector": self.detector,
            "metadata": self.metadata,
        }

    @classmethod
    def safe_result(
        cls,
        detector: Optional[str] = None,
        confidence: float = 1.0,
        details: str = "No threat detected",
        **kwargs: Any,
    ) -> GuardResult:
        """Factory for a passing (safe) result."""
        return cls(
            safe=True,
            threat=None,
            confidence=confidence,
            details=details,
            detector=detector,
            **kwargs,
        )

    @classmethod
    def threat_result(
        cls,
        threat: str,
        confidence: float,
        details: str = "",
        detector: Optional[str] = None,
        **kwargs: Any,
    ) -> GuardResult:
        """Factory for a failing (unsafe) result."""
        return cls(
            safe=False,
            threat=threat,
            confidence=confidence,
            details=details,
            detector=detector,
            **kwargs,
        )
