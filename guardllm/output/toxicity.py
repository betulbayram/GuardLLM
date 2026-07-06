"""Toxicity filter.

Ships a lightweight lexical baseline for Turkish + English that works with no
ML dependencies. When ``guardllm[toxicity]`` (Detoxify) is installed, a
stronger model-based score can be layered on top later.

The lexicon is intentionally small and focused on unambiguous profanity/slurs;
it is context-aware for a few common Turkish idioms to reduce false positives.
"""

from __future__ import annotations

import re

from guardllm.config import ToxicityConfig
from guardllm.result import GuardResult

# Unambiguous toxic tokens (lowercased, ascii-folded matching). Kept short and
# maintainable; the real strength comes from the optional ML backend.
_TOXIC_TERMS: set[str] = {
    # English
    "idiot",
    "moron",
    "stupid",
    "retard",
    "bastard",
    "asshole",
    # Turkish (roots; matched as word-ish substrings below)
    "aptal",
    "salak",
    "gerizekali",
    "orospu",
    "piç",
    "yavşak",
    "şerefsiz",
    "gerzek",
}

# Idioms where a toxic-looking root is actually benign → suppress.
_BENIGN_CONTEXT: list[re.Pattern[str]] = [
    re.compile(r"siktiri\s+çekmek", re.IGNORECASE),
]

_TOKEN_RE = re.compile(r"[a-zçğıöşü]+", re.IGNORECASE)


class ToxicityFilter:
    """Flags toxic / hateful content in model output."""

    name = "toxicity"

    def __init__(self, config: ToxicityConfig | None = None):
        self.config = config or ToxicityConfig()

    def check(self, text: str) -> GuardResult:
        if not self.config.enabled or not text:
            return GuardResult.safe_result(detector=self.name)

        lowered = text.lower()
        if any(p.search(lowered) for p in _BENIGN_CONTEXT):
            return GuardResult.safe_result(
                detector=self.name, details="Benign idiomatic usage"
            )

        tokens = _TOKEN_RE.findall(lowered)
        hits = [t for t in tokens if any(term in t for term in _TOXIC_TERMS)]
        if not hits:
            return GuardResult.safe_result(detector=self.name, details="No toxic terms")

        # Score scales with density of toxic tokens.
        density = len(hits) / max(len(tokens), 1)
        confidence = min(0.99, 0.8 + density)
        if confidence < self.config.threshold:
            return GuardResult.safe_result(
                detector=self.name,
                confidence=1.0 - confidence,
                details=f"Below threshold ({confidence:.2f} < {self.config.threshold})",
            )

        return GuardResult.threat_result(
            threat="toxicity",
            confidence=confidence,
            detector=self.name,
            details=f"Toxic term(s) detected: {', '.join(sorted(set(hits)))}",
            metadata={"terms": sorted(set(hits)), "density": round(density, 3)},
        )
