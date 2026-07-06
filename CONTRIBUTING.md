# Katkı Rehberi

GuardLLM'e katkıda bulunduğunuz için teşekkürler! 🛡️

## Geliştirme ortamı

```bash
git clone https://github.com/betulbayram/GuardLLM.git
cd GuardLLM
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Kaliteyi doğrula

Bir PR açmadan önce:

```bash
ruff check .          # lint
ruff format .         # (opsiyonel) biçimlendirme
pytest                # testler
pytest --cov=guardllm # coverage (hedef: %80+)
```

Dashboard üzerinde çalışıyorsanız:

```bash
cd dashboard && npm ci && npm run build
```

## Yeni bir dedektör eklerken

1. `guardllm/input/` veya `guardllm/output/` altına ekleyin.
2. Bir `GuardResult` döndürün (`safe`, `threat`, `confidence`, `details`).
3. **Ağır bağımlılık gerektirmeyen** bir baseline ile başlayın; ML backend'i
   `guardllm[ml]` opsiyonel extra'sının arkasına, lazy import ile ekleyin.
4. Testler ve mümkünse `benchmarks/` altına örnekler ekleyin.

## PR kuralları

- Küçük, odaklı PR'lar tercih edilir.
- Yeni davranış için test ekleyin.
- CI (test + lint) yeşil olmalı.
- Değişikliği `CHANGELOG.md`'ye işleyin.

## Lisans

Katkılarınız [MIT](LICENSE) lisansı altında yayımlanır.
