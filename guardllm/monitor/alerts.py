"""Alert system — fires when threat volume crosses a configurable threshold."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Callable, Optional

from guardllm.monitor.event import GuardEvent


@dataclass
class Alert:
    """A fired alert."""

    timestamp: float
    count: int
    window_seconds: int
    threshold: int
    last_threat: Optional[str]
    message: str


AlertCallback = Callable[[Alert], None]


class AlertManager:
    """Sliding-window threat-rate alerting.

    Records threat timestamps in a deque, evicts those older than
    ``window_seconds``, and fires (once) on the rising edge where the count in
    the window reaches ``threshold``. It re-arms after the count drops back
    below the threshold, so a sustained attack does not spam callbacks.
    """

    def __init__(
        self,
        threshold: int = 10,
        window_seconds: int = 3600,
        callbacks: Optional[list[AlertCallback]] = None,
    ) -> None:
        self.threshold = threshold
        self.window_seconds = window_seconds
        self.callbacks: list[AlertCallback] = list(callbacks or [])
        self._timestamps: deque[float] = deque()
        self._armed = True
        self.alerts_fired = 0
        self.last_alert: Optional[Alert] = None

    def add_callback(self, callback: AlertCallback) -> None:
        self.callbacks.append(callback)

    def record_threat(self, event: GuardEvent) -> Optional[Alert]:
        """Register a threat event; return an :class:`Alert` if one fires."""
        now = event.timestamp
        self._timestamps.append(now)
        cutoff = now - self.window_seconds
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()

        count = len(self._timestamps)
        if count < self.threshold:
            self._armed = True
            return None
        if not self._armed:
            return None

        # Rising edge -> fire once and disarm until it recovers.
        self._armed = False
        alert = Alert(
            timestamp=now,
            count=count,
            window_seconds=self.window_seconds,
            threshold=self.threshold,
            last_threat=event.threat,
            message=(
                f"GuardLLM alert: {count} threats in the last "
                f"{self.window_seconds}s (threshold {self.threshold}); "
                f"latest: {event.threat}"
            ),
        )
        self.alerts_fired += 1
        self.last_alert = alert
        for callback in self.callbacks:
            callback(alert)
        return alert
