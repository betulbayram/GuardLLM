# Güvenlik Politikası

## Güvenlik açığı bildirimi

GuardLLM bir güvenlik aracı olduğundan, açıkları sorumlu şekilde bildirmenizi
rica ederiz.

- Güvenlik açıklarını **herkese açık issue olarak açmayın.**
- Bunun yerine GitHub'ın **"Report a vulnerability"** (Security Advisories)
  özelliğini kullanın veya bakımcıya özel olarak ulaşın.
- Mümkünse yeniden üretim adımlarını ve etki değerlendirmesini ekleyin.

Bildirimlere makul sürede yanıt vermeye çalışırız.

## Kapsam ve sınırlamalar

GuardLLM **savunmayı katmanlar halinde güçlendiren** bir araçtır; tek başına
tam koruma garanti etmez:

- Kural-tabanlı dedektörler, pattern listesi dışındaki saldırıları kaçırabilir
  (bkz. benchmark recall değerleri). Kritik sistemlerde ML backend'i ve insan
  denetimiyle birlikte kullanın.
- KVKK modülü hukuki danışmanlık değildir; nihai uyumluluk için uzman görüşü
  alın.
- API'yi internete açarken CORS'u (`GUARDLLM_CORS_ORIGINS`) kısıtlayın, kimlik
  doğrulama/oran sınırlama ekleyin ve TLS kullanın.

## Desteklenen sürümler

En güncel `0.x` sürümü desteklenir.
