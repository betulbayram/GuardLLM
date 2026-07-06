"""Monitor — ties event logging, metrics and alerting together."""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from typing import Optional, Union

from guardllm.config import MonitorConfig
from guardllm.monitor.alerts import Alert, AlertCallback, AlertManager
from guardllm.monitor.event import GuardEvent
from guardllm.monitor.logger import build_logger
from guardllm.monitor.metrics import MetricsCollector
from guardllm.result import GuardResult


class Monitor:
    """Records guard checks: logs them, aggregates metrics, fires alerts.

    A :class:`~guardllm.guard.Guard` owns a Monitor when
    ``config.monitor.enabled`` is true and calls :meth:`record` for every
    decision. It can also be used standalone.
    """

    def __init__(
        self,
        config: Optional[MonitorConfig] = None,
        alert_callbacks: Optional[list[AlertCallback]] = None,
        recent_size: int = 100,
    ) -> None:
        self.config = config or MonitorConfig(enabled=True)
        self.metrics = MetricsCollector()
        self.alerts = AlertManager(
            threshold=self.config.alert_threshold,
            window_seconds=self.config.alert_window_seconds,
            callbacks=alert_callbacks,
        )
        self.logger = build_logger(self.config)
        self._recent: deque[GuardEvent] = deque(maxlen=recent_size)

    def record(
        self,
        result: GuardResult,
        stage: str,
        text: Optional[str] = None,
    ) -> GuardEvent:
        """Record a single guard decision and return the created event."""
        event = GuardEvent.from_result(
            result, stage=stage, text=text, store_text=self.config.store_text
        )
        self.logger.log(event)
        self.metrics.record(event)
        self._recent.append(event)
        if not result.safe:
            self.alerts.record_threat(event)
        return event

    def stats(self) -> dict:
        """Aggregated metrics + alert summary for dashboards/APIs."""
        snap = self.metrics.snapshot()
        snap["alerts_fired"] = self.alerts.alerts_fired
        snap["last_alert"] = (
            self.alerts.last_alert.message if self.alerts.last_alert else None
        )
        return snap

    def recent(self, n: int = 20) -> list[dict]:
        """Most recent events (newest last), for a 'blocked requests' feed."""
        events = list(self._recent)[-n:]
        return [e.to_dict() for e in events]

    def export_json(self, path: Union[str, Path]) -> None:
        """Dump recent events + current stats to a JSON file."""
        path = Path(path)
        payload = {"stats": self.stats(), "recent_events": self.recent(len(self._recent))}
        with path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)

    def on_alert(self, callback: AlertCallback) -> None:
        """Register an alert callback (e.g. send to Slack/email)."""
        self.alerts.add_callback(callback)

    def close(self) -> None:
        self.logger.close()

    # Support use as a context manager.
    def __enter__(self) -> Monitor:
        return self

    def __exit__(self, *exc) -> None:
        self.close()


__all__ = ["Monitor", "Alert"]
