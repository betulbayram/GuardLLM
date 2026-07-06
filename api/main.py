"""FastAPI application factory for GuardLLM-as-a-service.

Run:
    pip install "guardllm[api]" uvicorn
    uvicorn api.main:app --reload

Endpoints:
    POST /check/input     POST /check/output    POST /scan/pii
    GET  /monitor/stats   GET  /monitor/recent  GET  /monitor/alerts
    GET  /health
"""

from __future__ import annotations

import os
from typing import Optional, Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import check as check_routes
from api.routes import monitor as monitor_routes
from guardllm import __version__
from guardllm.config import GuardConfig, load_config
from guardllm.guard import Guard


def create_app(config: Optional[Union[str, GuardConfig]] = None) -> FastAPI:
    """Build the API app with a shared, monitored :class:`Guard`."""
    cfg = load_config(config)
    # The service always monitors so /monitor/* endpoints have data.
    cfg.monitor.enabled = True
    # Allow the log backend/DSN to be overridden by the environment (Docker).
    if os.getenv("GUARDLLM_LOG_TO"):
        cfg.monitor.log_to = os.environ["GUARDLLM_LOG_TO"]
    if os.getenv("GUARDLLM_DSN"):
        cfg.monitor.dsn = os.environ["GUARDLLM_DSN"]

    app = FastAPI(
        title="GuardLLM API",
        description="Security guardrails for LLM applications, as a service.",
        version=__version__,
    )
    # CORS lets the React dashboard (a separate origin) call the API. Restrict
    # it in production via GUARDLLM_CORS_ORIGINS (comma-separated list of
    # origins); defaults to "*" for easy local/dev use.
    origins_env = os.getenv("GUARDLLM_CORS_ORIGINS", "*").strip()
    allow_origins = (
        ["*"]
        if origins_env == "*"
        else [o.strip() for o in origins_env.split(",") if o.strip()]
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    app.state.guard = Guard(cfg)

    app.include_router(check_routes.router)
    app.include_router(monitor_routes.router)

    @app.get("/health", tags=["meta"])
    def health():
        return {"status": "ok", "version": __version__}

    @app.get("/", tags=["meta"])
    def root():
        return {
            "name": "GuardLLM API",
            "version": __version__,
            "docs": "/docs",
        }

    return app


# Module-level app for `uvicorn api.main:app`.
app = create_app()
