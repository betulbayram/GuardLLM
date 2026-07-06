# Benchmark

Dedektörler 271 etiketli test case üzerinde ölçülür. Test setleri bilinçli
olarak **zor parafrazlar** (recall'ı dürüst tutmak için) ve **benign tuzaklar**
(precision ölçümü için) içerir.

## Çalıştırma

```bash
python benchmarks/generate_datasets.py   # veri setlerini üret
python benchmarks/run_benchmarks.py       # metrikleri hesapla
```

## Sonuçlar (v0.1 kural-tabanlı)

| Detector | Precision | Recall | F1 | Latency | N |
|----------|-----------|--------|-----|---------|---|
| Prompt Injection | 100.0% | 70.3% | 82.6% | ~0.01ms | 124 |
| Jailbreak | 100.0% | 84.4% | 91.5% | ~0.01ms | 109 |
| PII (Turkish) | 100.0% | 100.0% | 100.0% | ~0.01ms | 21 |
| Hallucination | 100.0% | 100.0% | 100.0% | ~0.01ms | 12 |

!!! note "Precision vs Recall"
    Yüksek precision (benign metinlerde false positive yok) hedeflenir.
    Recall, pattern listesi dışındaki parafrazlarda düşer — ML backend
    (`guardllm[ml]`) tam olarak bunu iyileştirmek için tasarlanmıştır.

## Regresyon koruması

Metrik baseline'ları `tests/test_benchmarks.py` içinde test edilir; bir
değişiklik metriği düşürürse CI kırılır.

## Test setleri

- `benchmarks/injection_tests.json`
- `benchmarks/jailbreak_tests.json`
- `benchmarks/pii_tests_tr.json`
- `benchmarks/hallucination_tests.json`
