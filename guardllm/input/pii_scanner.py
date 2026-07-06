"""PII scanner for Turkish personal data (KVKK-oriented).

Detects and masks TC Kimlik No, phone numbers, e-mail, IBAN and credit-card
numbers using validated regex patterns. Name (NER) detection is optional and
requires the ``guardllm[ml]`` / ``guardllm[pii]`` extras.
"""

from __future__ import annotations

from dataclasses import dataclass

from guardllm.config import PIIConfig
from guardllm.result import GuardResult
from guardllm.utils import patterns


@dataclass
class PIIMatch:
    category: str
    value: str
    start: int
    end: int


# Categories that carry an extra validation step beyond the regex.
_VALIDATORS = {
    "tc_kimlik": patterns.validate_tc_kimlik,
    "kredi_karti": patterns.luhn_check,
}

# Detection priority (higher-specificity / validated categories first) so that
# overlapping spans are resolved deterministically.
_PRIORITY = ["email", "iban", "tc_kimlik", "telefon", "kredi_karti"]


class PIIScanner:
    """Scans text for Turkish PII and produces a masked (redacted) version."""

    name = "pii_scanner"

    def __init__(self, config: PIIConfig | None = None):
        self.config = config or PIIConfig()

    def _find_matches(self, text: str) -> list[PIIMatch]:
        active = [c for c in _PRIORITY if c in self.config.categories]
        pattern_map = dict(patterns.PII_PATTERNS)
        found: list[PIIMatch] = []
        occupied: list[tuple[int, int]] = []

        for category in active:
            pattern = pattern_map.get(category)
            if pattern is None:
                continue
            validator = _VALIDATORS.get(category)
            for m in pattern.finditer(text):
                start, end = m.start(), m.end()
                if validator and not validator(m.group()):
                    continue
                # Skip spans overlapping an already-claimed (higher-priority) one.
                if any(start < oe and os < end for os, oe in occupied):
                    continue
                found.append(PIIMatch(category, m.group(), start, end))
                occupied.append((start, end))

        found.sort(key=lambda x: x.start)
        return found

    def scan(self, text: str) -> GuardResult:
        """Scan ``text``; return a result with a ``redacted`` version.

        The result is ``safe=False`` when PII is found *and* the configured
        action is ``block``; for ``mask``/``warn`` it is still surfaced as a
        threat so callers can act, but ``redacted`` holds the safe text.
        """
        if not self.config.enabled or not text:
            return GuardResult.safe_result(detector=self.name, redacted=text)

        matches = self._find_matches(text)
        if not matches:
            return GuardResult.safe_result(
                detector=self.name, details="No PII detected", redacted=text
            )

        # Build the redacted string by replacing spans right-to-left.
        redacted = text
        for m in sorted(matches, key=lambda x: x.start, reverse=True):
            label = patterns.PII_LABELS.get(m.category, "[PII]")
            redacted = redacted[: m.start] + label + redacted[m.end :]

        categories = sorted({m.category for m in matches})
        details = f"PII detected ({self.config.action}): {', '.join(categories)}"
        metadata = {
            "action": self.config.action,
            "categories": categories,
            "count": len(matches),
            "spans": [
                {"category": m.category, "start": m.start, "end": m.end}
                for m in matches
            ],
        }

        # 'warn' surfaces the finding but does not block the pipeline.
        safe = self.config.action == "warn"
        confidence = 0.95
        return GuardResult(
            safe=safe,
            threat=None if safe else "pii_leak",
            confidence=confidence,
            details=details,
            redacted=redacted,
            detector=self.name,
            metadata=metadata,
        )

    # Alias so callers can use ``check`` uniformly with other detectors.
    check = scan
