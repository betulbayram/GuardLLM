"""GuardEvent — a single recorded guard check."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from guardllm.result import GuardResult


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


@dataclass
class GuardEvent:
    """An immutable record of one guard decision.

    Raw text is **not** stored by default (it may contain PII); only a short
    SHA-256 fingerprint is kept for correlation/deduplication. Set
    ``store_text=True`` on the monitor config to also keep a truncated preview.
    """

    timestamp: float
    iso_time: str
    stage: str  # "input" | "output"
    safe: bool
    threat: Optional[str]
    confidence: float
    detector: Optional[str]
    details: str
    text_hash: Optional[str] = None
    text_preview: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_result(
        cls,
        result: GuardResult,
        stage: str,
        text: Optional[str] = None,
        store_text: bool = False,
        preview_len: int = 120,
    ) -> GuardEvent:
        now = time.time()
        text_hash = _hash_text(text) if text else None
        preview = None
        if store_text and text:
            preview = text[:preview_len]
        return cls(
            timestamp=now,
            iso_time=datetime.fromtimestamp(now, tz=timezone.utc).isoformat(),
            stage=stage,
            safe=result.safe,
            threat=result.threat,
            confidence=round(result.confidence, 4),
            detector=result.detector,
            details=result.details,
            text_hash=text_hash,
            text_preview=preview,
            metadata=dict(result.metadata),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "iso_time": self.iso_time,
            "stage": self.stage,
            "safe": self.safe,
            "threat": self.threat,
            "confidence": self.confidence,
            "detector": self.detector,
            "details": self.details,
            "text_hash": self.text_hash,
            "text_preview": self.text_preview,
            "metadata": self.metadata,
        }
