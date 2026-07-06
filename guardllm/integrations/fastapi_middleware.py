"""FastAPI/Starlette middleware that runs the input guard on every request.

Usage::

    from fastapi import FastAPI
    from guardllm.integrations import GuardMiddleware

    app = FastAPI()
    app.add_middleware(GuardMiddleware, block_on_threat=True)

The middleware inspects the JSON body of incoming requests, extracts the
prompt field(s) and runs :meth:`Guard.check_input`. If a threat is found and
``block_on_threat`` is set, it short-circuits with an HTTP 403 response.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Optional

try:
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
    from starlette.responses import JSONResponse
except ImportError as exc:  # pragma: no cover - exercised only without extra
    raise ImportError(
        "GuardMiddleware requires FastAPI/Starlette. "
        'Install with: pip install "guardllm[api]"'
    ) from exc

from guardllm.config import GuardConfig
from guardllm.guard import Guard
from guardllm.result import GuardResult

# JSON keys that commonly carry a user prompt.
_DEFAULT_FIELDS = ("prompt", "message", "input", "query", "text", "content")


class GuardMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        guard: Optional[Guard] = None,
        config: Optional[GuardConfig] = None,
        block_on_threat: bool = True,
        prompt_fields: Iterable[str] = _DEFAULT_FIELDS,
        status_code: int = 403,
    ):
        super().__init__(app)
        self.guard = guard or Guard(config)
        self.block_on_threat = block_on_threat
        self.prompt_fields = tuple(prompt_fields)
        self.status_code = status_code

    def _extract_prompt(self, payload: object) -> Optional[str]:
        """Pull the first matching prompt field from a parsed JSON body."""
        if isinstance(payload, str):
            return payload
        if isinstance(payload, dict):
            for field in self.prompt_fields:
                value = payload.get(field)
                if isinstance(value, str) and value.strip():
                    return value
            # OpenAI-style chat payloads: messages=[{role, content}, ...]
            messages = payload.get("messages")
            if isinstance(messages, list):
                user_msgs = [
                    m.get("content", "")
                    for m in messages
                    if isinstance(m, dict) and m.get("role") == "user"
                ]
                if user_msgs:
                    return "\n".join(user_msgs)
        return None

    async def dispatch(self, request: Request, call_next):
        # Only inspect requests that can carry a body.
        if request.method in ("POST", "PUT", "PATCH"):
            body = await request.body()
            if body:
                try:
                    payload = json.loads(body)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    payload = None

                prompt = self._extract_prompt(payload) if payload is not None else None
                if prompt:
                    result: GuardResult = self.guard.check_input(prompt)
                    if not result.safe and self.block_on_threat:
                        return JSONResponse(
                            status_code=self.status_code,
                            content={
                                "detail": "Request blocked by GuardLLM",
                                "threat": result.threat,
                                "confidence": round(result.confidence, 4),
                                "reason": result.details,
                            },
                        )

            # Re-inject the consumed body so downstream handlers can read it.
            async def receive():
                return {"type": "http.request", "body": body, "more_body": False}

            request._receive = receive  # noqa: SLF001 - documented Starlette pattern

        return await call_next(request)
