"""Shared FastAPI dependencies."""

from __future__ import annotations

from fastapi import Request

from guardllm.guard import Guard


def get_guard(request: Request) -> Guard:
    """Return the process-wide Guard instance stored on ``app.state``."""
    return request.app.state.guard
