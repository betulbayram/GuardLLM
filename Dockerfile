# GuardLLM API image
FROM python:3.12-slim

# Runtime hygiene
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install the package with API extras first (better layer caching).
COPY pyproject.toml README.md ./
COPY guardllm ./guardllm
RUN pip install --no-cache-dir ".[api]" "psycopg[binary]>=3.1"

# App code
COPY api ./api
COPY configs ./configs

# Run as a non-root user
RUN useradd --create-home --uid 10001 appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
