# GuardLLM Dashboard

Real-time threat monitoring UI for the GuardLLM API (Vite + React + TypeScript + Recharts).

## Çalıştırma

```bash
# 1) API'yi başlat (ayrı terminalde)
uvicorn api.main:app --reload           # http://localhost:8000

# 2) Dashboard
cd dashboard
npm install
cp .env.example .env                     # gerekiyorsa VITE_API_URL değiştir
npm run dev                              # http://localhost:5173
```

API çalışmıyorsa panel otomatik olarak **demo veriyle** açılır (sağ üstte
"Demo modu" göstergesi).

## Sayfalar

- **Test Et (Playground)** — metin yazıp canlı olarak guard'ları çalıştır:
  girdi / çıktı / PII / KVKK. Sonuç (verdict, güven skoru, detay, maskeleme,
  KVKK raporu) anında gösterilir. *API çalışıyor olmalı.*
- **Threat Monitor** — özet kartlar, saatlik tehdit grafiği (area), tehdit türü
  dağılımı (pie), canlı alert banner, son engellenen istekler tablosu
- **Log Viewer** — tüm guard olaylarının kaydı
- **Settings** — API bağlantısı ve monitör durumu (salt-okunur)

Veri kaynağı: `/monitor/stats`, `/monitor/recent`, `/monitor/alerts` (5 sn'de bir
poll edilir).
