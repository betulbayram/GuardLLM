# Kullanım Kılavuzu (Production)

GuardLLM **görünmez bir güvenlik ara katmanıdır.** Son kullanıcı onu görmez;
kendi uygulamanızın içinde, her LLM çağrısının önünde ve arkasında sessizce
çalışır. Bu sayfa, gerçek bir uygulamaya nasıl entegre edileceğini gösterir.

## Zihinsel model

```
Kullanıcı → [Senin uygulaman:  GuardLLM → LLM → GuardLLM]  → Kullanıcı
                                 ↑ input        ↑ output
```

GuardLLM **senin modelini çağırmaz**; sadece girdi/çıktıyı denetler. Model
senindir (OpenAI, Anthropic, yerel model…).

## 1. Kurulum

Uygulamanızın bağımlılıklarına ekleyin:

```bash
pip install guardllm-tr
```

## 2. Uygulamanıza gömme (kütüphane — en yaygın yol)

Örnek: OpenAI kullanan bir müşteri-destek chatbot'u (FastAPI).

```python
from fastapi import FastAPI
from openai import OpenAI
from guardllm import Guard

app = FastAPI()
llm = OpenAI()
guard = Guard("configs/strict.yaml")  # kendi politikanız

@app.post("/chat")
def chat(message: str):
    # 1) Kullanıcı girdisini kontrol et
    check = guard.check_input(message)
    if not check.safe:
        # Logla, kullanıcıya nazik bir mesaj dön
        return {"error": "Mesajınız güvenlik filtresine takıldı.",
                "reason": check.threat}

    # 2) KENDİ modelinizi çağırın
    completion = llm.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": message}],
    )
    answer = completion.choices[0].message.content

    # 3) Yanıtı kontrol et (toxicity, PII, hallucination)
    out = guard.check_output(response=answer, prompt=message)
    if not out.safe:
        answer = out.redacted or "Bu soruyu şu an güvenli şekilde yanıtlayamıyorum."

    return {"answer": answer}
```

Uygulamanızı normalde nasıl deploy ediyorsanız (kendi sunucunuz, AWS, container)
öyle deploy edin — **ekstra bir servis çalıştırmanız gerekmez.** GuardLLM
uygulamanızla aynı process içinde çalışır.

## 3. Daha da kısa: otomatik sarma

Her çağrının etrafına elle `if` yazmak istemiyorsanız:

=== "LangChain"

    ```python
    from langchain_openai import ChatOpenAI
    from guardllm.integrations import GuardedLLM

    guarded = GuardedLLM(llm=ChatOpenAI(model="gpt-4o-mini"))
    guarded.invoke("Merhaba")   # input+output guard otomatik çalışır
    ```

=== "FastAPI middleware"

    ```python
    from guardllm.integrations import GuardMiddleware
    app.add_middleware(GuardMiddleware, block_on_threat=True)
    # Tehdit içeren istekler otomatik 403 döner
    ```

=== "OpenAI SDK"

    ```python
    from guardllm.integrations import OpenAIGuard
    guarded = OpenAIGuard(OpenAI())
    guarded.create(model="gpt-4o-mini", messages=[...])
    ```

## 4. Alternatif: ayrı servis olarak (çok dilli ekipler)

Uygulamanız Python değilse (Node, Java, Go…) veya güvenlik politikasını merkezî
tutmak istiyorsanız, GuardLLM'i bir HTTP servisi olarak çalıştırın:

```bash
docker compose up -d      # API + PostgreSQL
```

Uygulamanız her istekte servise HTTP çağrısı yapar:

```bash
curl -X POST https://guard.sirketiniz.com/check/input \
  -H "content-type: application/json" \
  -d '{"text": "kullanıcının mesajı"}'
```

!!! warning "Prod güvenliği"
    Servisi internete açarken `GUARDLLM_CORS_ORIGINS` ile CORS'u kısıtlayın,
    önüne TLS + kimlik doğrulama/oran sınırlama koyun.

## 5. İzleme (ops ekibi için)

Monitör'ü açın; her karar PostgreSQL'e loglanır ve dashboard bunu gösterir:

```yaml
monitor:
  enabled: true
  log_to: "postgresql"
  alert_threshold: 20
```

- **Dashboard** (React) = **iç ekibinizin** izleme paneli; son kullanıcı görmez.
- **Playground / Test Et sekmesi** = geliştirici/QA test aracı; prod trafiği değil.

## Ne, prod'da nerede çalışır?

| Bileşen | Prod rolü | Kim görür |
|---------|-----------|-----------|
| Kütüphane (`pip`) | Uygulamanızın içinde, her istekte | Kimse (görünmez) |
| API + Docker | Opsiyonel merkezî servis | Diğer uygulamalar (HTTP) |
| Dashboard | İzleme paneli | İç ekip |
| Playground | Test/demo | Geliştiriciler |

## Özet

1. `pip install guardllm-tr`
2. `check_input` → kendi LLM'in → `check_output`
3. Uygulamanla birlikte deploy et (ekstra altyapı yok), veya Docker servisi çalıştır
4. İstersen monitör + dashboard ile izle
