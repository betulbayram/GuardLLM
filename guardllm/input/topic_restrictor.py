"""Topic restrictor — enforce allowed/blocked conversation topics.

Two modes:

* ``blocklist`` — block prompts that match any *blocked* topic.
* ``allowlist`` — block prompts that do **not** match any *allowed* topic
  (i.e. off-topic requests), useful for narrow-domain assistants.

Topics are defined by keyword lists. This rule-based baseline needs no ML;
an embedding-based semantic matcher can be layered on via ``guardllm[ml]``.
"""

from __future__ import annotations

import re

from guardllm.config import TopicConfig
from guardllm.result import GuardResult


class TopicRestrictor:
    name = "topic_restrictor"

    def __init__(self, config: TopicConfig | None = None):
        self.config = config or TopicConfig()
        self._patterns: dict[str, re.Pattern[str]] = {}
        for topic, keywords in self.config.topics.items():
            if not keywords:
                continue
            alt = "|".join(re.escape(k) for k in keywords)
            self._patterns[topic] = re.compile(
                rf"(?<!\w)(?:{alt})(?!\w)", re.IGNORECASE | re.UNICODE
            )

    def _matched_topics(self, text: str) -> dict[str, int]:
        """Return {topic: hit_count} for topics meeting ``min_keywords``."""
        matched: dict[str, int] = {}
        for topic, pattern in self._patterns.items():
            hits = len(pattern.findall(text))
            if hits >= self.config.min_keywords:
                matched[topic] = hits
        return matched

    def check(self, text: str) -> GuardResult:
        if not self.config.enabled or not text or not self._patterns:
            return GuardResult.safe_result(detector=self.name)

        matched = self._matched_topics(text)

        if self.config.mode == "allowlist":
            allowed = set(self.config.allowed) or set(self._patterns)
            on_topic = [t for t in matched if t in allowed]
            if on_topic:
                return GuardResult.safe_result(
                    detector=self.name,
                    details=f"On-topic: {', '.join(sorted(on_topic))}",
                )
            return GuardResult.threat_result(
                threat="off_topic",
                confidence=0.85,
                detector=self.name,
                details="Prompt does not match any allowed topic",
                metadata={"allowed_topics": sorted(allowed)},
            )

        # blocklist mode (default)
        blocked = set(self.config.blocked) or set(self._patterns)
        fired = [t for t in matched if t in blocked]
        if not fired:
            return GuardResult.safe_result(
                detector=self.name, details="No restricted topic matched"
            )

        total_hits = sum(matched[t] for t in fired)
        confidence = min(0.99, 0.8 + 0.05 * (total_hits - 1))
        return GuardResult.threat_result(
            threat="restricted_topic",
            confidence=confidence,
            detector=self.name,
            details=f"Restricted topic(s) detected: {', '.join(sorted(fired))}",
            metadata={"topics": sorted(fired), "hits": total_hits},
        )
