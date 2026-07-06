"""Threat metrics collector — aggregates GuardEvents for dashboards/stats."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any

from guardllm.monitor.event import GuardEvent


class MetricsCollector:
    """In-memory aggregation of guard events.

    Cheap to update on the hot path; :meth:`snapshot` produces a JSON-friendly
    summary suitable for the ``/monitor/stats`` endpoint and the dashboard.
    """

    def __init__(self) -> None:
        self.total_checks = 0
        self.blocked = 0
        self.by_threat: Counter[str] = Counter()
        self.by_stage: Counter[str] = Counter()
        self.by_detector: Counter[str] = Counter()
        # threats per calendar hour (UTC), keyed "YYYY-MM-DDTHH"
        self.by_hour: dict[str, int] = defaultdict(int)

    def record(self, event: GuardEvent) -> None:
        self.total_checks += 1
        self.by_stage[event.stage] += 1
        if not event.safe:
            self.blocked += 1
            if event.threat:
                self.by_threat[event.threat] += 1
            if event.detector:
                self.by_detector[event.detector] += 1
            hour = datetime.fromtimestamp(
                event.timestamp, tz=timezone.utc
            ).strftime("%Y-%m-%dT%H")
            self.by_hour[hour] += 1

    @property
    def block_rate(self) -> float:
        return round(self.blocked / self.total_checks, 4) if self.total_checks else 0.0

    def snapshot(self) -> dict[str, Any]:
        return {
            "total_checks": self.total_checks,
            "blocked": self.blocked,
            "block_rate": self.block_rate,
            "by_threat": dict(self.by_threat),
            "by_stage": dict(self.by_stage),
            "by_detector": dict(self.by_detector),
            "top_threats": self.by_threat.most_common(5),
            "threats_by_hour": dict(self.by_hour),
        }

    def reset(self) -> None:
        self.__init__()
