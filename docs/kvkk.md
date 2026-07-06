# KVKK Uyumluluk Modülü

GuardLLM, Türkiye'deki **6698 sayılı Kişisel Verilerin Korunması Kanunu (KVKK)**
kapsamında metinlerdeki kişisel verileri tespit eden ve uyumluluk raporu üreten
bir modül içerir.

> ⚖️ **Not:** Bu modül otomatik bir yardımcıdır, hukuki danışmanlık değildir.
> Nihai uyumluluk değerlendirmesi için hukuk uzmanına başvurun.

## Kullanım

```python
from guardllm import Guard, KVKKChecker

# Guard üzerinden
report = Guard().check_kvkk("Hastanın sağlık raporu ve TC 10000000146 kayıtlı.")

# veya doğrudan
report = KVKKChecker().check("Müşteri e-postası ali@firma.com")
```

## Veri kategorileri

### Genel nitelikli kişisel veriler (Madde 5)

| Kategori | Örnek | Tespit |
|----------|-------|--------|
| Kimlik verisi | TC Kimlik No | Regex + algoritma doğrulama |
| İletişim verisi | telefon, e-posta | Regex |
| Finansal veri | IBAN, kredi kartı | Regex + Luhn doğrulama |

### Özel nitelikli kişisel veriler (Madde 6)

Kural olarak yalnızca ilgilinin **açık rızası** ile işlenebilir:

| Kategori | Örnek ifadeler |
|----------|----------------|
| Sağlık verisi | teşhis, tedavi, ilaç, kan grubu, kanser, diyabet, engelli |
| Biyometrik veri | parmak izi, yüz tanıma, retina, DNA |
| Ceza mahkûmiyeti | sabıka, mahkûmiyet, adli sicil, hükümlü |
| Din / inanç | dini inanç, mezhep, felsefi inanç |
| Irk / etnik köken | ırk, etnik köken |
| Sendika üyeliği | sendika üyeliği |

## Rapor içeriği

`ComplianceReport`:

- `compliant` — kişisel veri yoksa `True`
- `risk_level` — `yok` / `orta` (genel) / `yüksek` (özel nitelikli)
- `requires_explicit_consent` — özel nitelikli veri varsa `True`
- `findings` — tespit edilen kategoriler ve madde referansları
- `recommendations` — KVKK maddelerine dayalı öneriler
- `redacted` — maskelenmiş metin
- `to_dict()` / `to_markdown()` — dışa aktarım

## İlgili KVKK maddeleri

- **Madde 4** — Genel ilkeler (hukuka uygunluk, amaçla sınırlılık, ölçülülük)
- **Madde 5** — Kişisel verilerin işlenme şartları
- **Madde 6** — Özel nitelikli kişisel verilerin işlenmesi
- **Madde 12** — Veri güvenliği yükümlülükleri

## HTTP API

```bash
curl -X POST localhost:8000/compliance/kvkk \
  -H "content-type: application/json" \
  -d '{"text": "Hastanın kanser teşhisi kondu."}'
```
