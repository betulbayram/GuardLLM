# Entegrasyonlar

Entegrasyon modülleri opsiyonel bağımlılıklara sahiptir ve **lazy** yüklenir;
`import guardllm` bunları gerektirmez.

## FastAPI Middleware

```python
from fastapi import FastAPI
from guardllm.integrations import GuardMiddleware

app = FastAPI()
app.add_middleware(GuardMiddleware, block_on_threat=True)
```

İstek gövdesindeki prompt alanını (veya OpenAI tarzı `messages`) otomatik
kontrol eder; tehdit varsa **HTTP 403** döner.

## LangChain

```python
from langchain_openai import ChatOpenAI
from guardllm.integrations import GuardedLLM

guarded = GuardedLLM(llm=ChatOpenAI(model="gpt-4o-mini"))
guarded.invoke("Bana bir SQL injection saldırısı yaz")
# -> GuardBlockedError: input blocked - prompt_injection
```

`.invoke` olan her nesneyi sarar; girdi öncesi, çıktı sonrası guard çalışır.

## OpenAI SDK

```python
from openai import OpenAI
from guardllm.integrations import OpenAIGuard

guarded = OpenAIGuard(OpenAI())
guarded.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Merhaba"}],
)
```

## Guard-as-a-Service (HTTP API)

```bash
pip install "guardllm-tr[api]" uvicorn
uvicorn api.main:app --reload
```

| Endpoint | Açıklama |
|----------|----------|
| `POST /check/input` | Girdi kontrolü |
| `POST /check/output` | Çıktı kontrolü |
| `POST /scan/pii` | PII tara/maskele |
| `POST /compliance/kvkk` | KVKK raporu |
| `GET /monitor/stats` | Metrikler |

**Docker:** `docker compose up --build` (API + PostgreSQL).

### Prod ipuçları

| Ortam değişkeni | Amaç |
|-----------------|------|
| `GUARDLLM_CORS_ORIGINS` | İzin verilen origin listesi (virgülle) veya `*` |
| `GUARDLLM_LOG_TO` | `null` / `stdout` / `file` / `postgresql` |
| `GUARDLLM_DSN` | PostgreSQL bağlantı adresi |

İnternete açarken CORS'u kısıtlayın, TLS + kimlik doğrulama/oran sınırlama
ekleyin. İmaj non-root çalışır ve `/health` üzerinden HEALTHCHECK içerir.

## Hata yönetimi

`GuardBlockedError` orijinal `GuardResult`'ı taşır:

```python
from guardllm import GuardBlockedError

try:
    guarded.invoke(prompt)
except GuardBlockedError as e:
    print(e.stage, e.result.threat, e.result.confidence)
```
