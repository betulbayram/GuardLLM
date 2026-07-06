"""/monitor/* endpoints — expose metrics and alerts for dashboards."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from api.deps import get_guard
from guardllm.guard import Guard

router = APIRouter(prefix="/monitor", tags=["monitor"])


def _require_monitor(guard: Guard):
    if guard.monitor is None:
        raise HTTPException(status_code=503, detail="Monitoring is disabled")
    return guard.monitor


@router.get("/stats")
def stats(guard: Guard = Depends(get_guard)):
    """Aggregated threat metrics (counts, block rate, top threats, hourly)."""
    return _require_monitor(guard).stats()


@router.get("/recent")
def recent(
    n: int = Query(20, ge=1, le=100), guard: Guard = Depends(get_guard)
):
    """Most recent guard events (for a live 'blocked requests' feed)."""
    return _require_monitor(guard).recent(n)


@router.get("/alerts")
def alerts(guard: Guard = Depends(get_guard)):
    """Alert summary: how many fired and the most recent one."""
    monitor = _require_monitor(guard)
    last = monitor.alerts.last_alert
    return {
        "alerts_fired": monitor.alerts.alerts_fired,
        "threshold": monitor.alerts.threshold,
        "window_seconds": monitor.alerts.window_seconds,
        "last_alert": last.message if last else None,
        "last_alert_at": last.timestamp if last else None,
    }
