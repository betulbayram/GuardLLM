# Konfigürasyon

GuardLLM koddan veya YAML dosyasından yapılandırılabilir.

## YAML ile

```python
from guardllm import Guard

guard = Guard("configs/default_config.yaml")
```

Örnek yapılandırma:

```yaml
guards:
  input:
    prompt_injection:
      enabled: true
      threshold: 0.85
      languages: ["tr", "en"]
    jailbreak:
      enabled: true
      threshold: 0.80
    pii_scanner:
      enabled: true
      categories: ["tc_kimlik", "telefon", "email", "iban", "kredi_karti"]
      action: "mask" # mask | block | warn
    topic_restrictor:
      enabled: false
      mode: "blocklist" # blocklist | allowlist
      topics:
        tibbi_tavsiye: ["teşhis", "ilaç", "doz", "reçete"]
      blocked: ["tibbi_tavsiye"]

  output:
    hallucination:
      enabled: true
      threshold: 0.70
    toxicity:
      enabled: true
      threshold: 0.80
    pii_redactor:
      enabled: true
      action: "mask"

  monitor:
    enabled: false
    log_to: "stdout" # postgresql | file | stdout | null
    alert_threshold: 10
```

## Koddan

```python
from guardllm import Guard, GuardConfig

cfg = GuardConfig.default()
cfg.input.prompt_injection.threshold = 0.9
cfg.output.toxicity.enabled = False
guard = Guard(cfg)
```

## Threshold mantığı

- **Injection / Jailbreak / Toxicity:** confidence ≥ `threshold` olduğunda engellenir.
- **Hallucination:** `threshold` minimum *faithfulness* skorudur; altında kalırsa
  hallucination olarak işaretlenir.
- **PII:** `action` alanı davranışı belirler — `mask` (maskele ve tehdit olarak
  işaretle), `block`, veya `warn` (yalnızca uyar, güvenli sayılır).
