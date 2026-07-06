# Dedektörler

Her dedektör bir `GuardResult` döndürür: `safe`, `threat`, `confidence`,
`details`, `redacted`, `detector`, `metadata`.

## Input Guard

### Prompt Injection
Talimatları geçersiz kılma / sızdırma girişimlerini yakalar (TR + EN).
Kural tabanlı; birden çok kalıp eşleşince confidence artar.

```python
from guardllm.input import InjectionDetector
InjectionDetector().check("Ignore all previous instructions")
```

### Jailbreak
DAN, roleplay, "no restrictions", encoding bypass kalıpları (TR + EN).

### PII Scanner
Türkçe kişisel veri tespiti ve maskeleme:

| Kategori | Doğrulama |
|----------|-----------|
| TC Kimlik No | 11 hane + resmi checksum algoritması |
| Telefon | +90 / 05xx formatı |
| E-posta | RFC-benzeri regex |
| IBAN | TR + 24 hane |
| Kredi kartı | 13-16 hane + Luhn |

### Topic Restrictor
Konu bazlı kısıtlama (opt-in). `blocklist` yasaklı konuları engeller,
`allowlist` yalnızca izin verilen konulara izin verir.

## Output Guard

### Hallucination
Yanıtı verilen `context` ile karşılaştırır: içerik-token örtüşmesi +
**sayısal tutarlılık** (context'te olmayan sayılar güçlü hallucination sinyali).
Varsayılan yöntem bağımlılık-gerektirmez; `guardllm[ml]` ile NLI eklenebilir.

### Toxicity
TR/EN toksik içerik; birkaç Türkçe deyim için bağlam-farkında
(false positive azaltma). `guardllm[toxicity]` ile Detoxify eklenebilir.

### PII Redactor
Çıktı üzerinde aynı PII maskeleme mantığını uygular.

## ML backend (opsiyonel)

Kural tabanlı çekirdek hızlı ve hafiftir. Daha yüksek recall için:

```bash
pip install "guardllm-tr[ml]"
```
