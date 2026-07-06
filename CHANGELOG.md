# Changelog

Bu proje [Keep a Changelog](https://keepachangelog.com/) formatını ve
[Semantic Versioning](https://semver.org/) kurallarını izler.

## [0.3.0]

### Eklendi
- **Topic Restrictor** — konu bazlı kısıtlama (blocklist / allowlist modları).
- **KVKK uyumluluk modülü** — kişisel verileri genel (Madde 5) ve özel nitelikli
  (Madde 6) kategorilere ayıran denetim + madde referanslı uyumluluk raporu.
- **React dashboard** — Threat Monitor, Log Viewer, Settings ve interaktif
  **Playground (Test Et)** sekmesi; canlı API'ye bağlanır.
- **Benchmark suite** — 271 etiketli test case + precision/recall/F1 runner ve
  regresyon testleri.
- **GitHub Actions CI** (test + lint matrisi, dashboard build) ve `publish.yml`
  (PyPI trusted publishing).
- **MkDocs Material** dokümantasyon sitesi.
- `POST /compliance/kvkk` API endpoint'i.
- PEP 561 `py.typed` işaretçisi; yapılandırılabilir CORS; Docker sıkılaştırma.

### Düzeltildi
- Varsayılan PII yapılandırmasında `kredi_karti` eksikliği.
- Telefon regex'inin kart numarası içindeki rakam dizilerini yakalaması.

## [0.2.0]

### Eklendi
- **Entegrasyonlar**: FastAPI `GuardMiddleware`, LangChain `GuardedLLM`,
  `OpenAIGuard`.
- **Monitoring**: olay loglama (null/stdout/file/PostgreSQL), tehdit metrikleri,
  kayan-pencere alert sistemi.
- **Guard-as-a-Service API** (FastAPI) ve Docker Compose (API + PostgreSQL).
- `GuardBlockedError` istisnası.

## [0.1.0]

### Eklendi
- Çekirdek `Guard`, `GuardResult`, YAML tabanlı `GuardConfig`.
- Input dedektörleri: prompt injection, jailbreak, PII scanner (TC Kimlik
  algoritma + Luhn doğrulama).
- Output dedektörleri: hallucination (faithfulness), toxicity.
- Kural-tabanlı çekirdek (ağır bağımlılık yok); ML backend'leri opsiyonel.
