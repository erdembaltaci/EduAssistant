# 🔄 Yedekli AI Sistemi (Fallback Mechanism)

## 📋 Genel Bakış

Bu sistem, **Gemini API çökerse veya erişilemez olursa** otomatik olarak alternatif AI provider'lara geçer. Böylece proje **hiçbir zaman tamamen durmaz**.

## 🏗️ Mimari

```
Kullanıcı İsteği
    ↓
AI Provider Manager
    ↓
┌─────────────────────────────────┐
│  1. Gemini Provider (Birincil) │ → Çökerse ↓
└─────────────────────────────────┘
    ↓ (Fallback)
┌─────────────────────────────────┐
│  2. Mock Provider (Son Çare)   │ → Her zaman çalışır ✅
└─────────────────────────────────┘
```

**Not:** OpenAI provider şu anda implement edilmedi. İhtiyaç halinde eklenebilir.

## 🎯 Özellikler

### ✅ Otomatik Failover
- Gemini çökerse → Mock moduna geçer
- Mock modu her zaman çalışır (offline)
- Proje hiçbir zaman tamamen durmaz

### ✅ Health Check
- `/api/v1/health` endpoint'i hangi provider'ın aktif olduğunu gösterir
- Provider durumunu gerçek zamanlı takip eder

### ✅ Provider Abstraction
- Yeni provider eklemek kolay (Claude, Anthropic, vs.)
- Tüm provider'lar aynı interface'i kullanır

## 📝 Kullanım

### Environment Variables

```bash
# Birincil Provider (Gemini)
GOOGLE_API_KEY=your_gemini_key

# Mock Provider için API key gerekmez (her zaman çalışır)
```

### Kod Kullanımı

```python
from services.ai_provider import get_ai_provider_manager

manager = get_ai_provider_manager()

# Otomatik fallback ile soru üret
result = manager.generate_questions_with_fallback(
    text="Ders metni...",
    num_questions=5,
    question_type="çoktan seçmeli",
    difficulty="orta"
)

# Hangi provider kullanıldı?
print(result["provider"])  # "gemini" veya "mock"
```

## 🔍 Test Senaryoları

### Senaryo 1: Gemini Çalışıyor
```
✅ Gemini Provider aktif
→ Normal çalışma
```

### Senaryo 2: Gemini Çöktü
```
❌ Gemini hatası
🔄 Mock moduna geçiliyor...
✅ Mock Provider aktif (Basit sorular üretir)
→ Proje çalışmaya devam eder!
```

## 🛡️ Güvenlik

- API anahtarları `.env` dosyasında saklanır
- `.env` dosyası git'e eklenmez (`.gitignore`)
- Her provider kendi API anahtarını kullanır

## 📊 Monitoring

Health check endpoint'i ile provider durumunu kontrol edebilirsiniz:

```bash
curl http://localhost:8000/api/v1/health
```

Response:
```json
{
  "status": "OK",
  "ai_provider": "GeminiProvider",
  "ai_available": true
}
```

## 🚀 Gelecek Geliştirmeler

- [ ] OpenAI provider tam implementasyonu
- [ ] Claude/Anthropic provider ekleme
- [ ] Provider health check periyodik kontrolü
- [ ] Cache mekanizması (aynı metin için tekrar istek yapmama)
- [ ] Load balancing (birden fazla provider'a paralel istek)
- [ ] Metrics ve logging (hangi provider ne kadar kullanıldı)

## 💡 Önemli Notlar

1. **Mock Provider**: Gerçek AI kullanmaz, basit mock sorular üretir. Test ve offline çalışma için idealdir.

2. **OpenAI Provider**: Şu anda implement edilmedi. İhtiyaç halinde eklenebilir.

3. **Fallback Sırası**: Gemini → Mock (değiştirilebilir)

4. **Error Handling**: Her provider hatası yakalanır ve bir sonrakine geçilir.

