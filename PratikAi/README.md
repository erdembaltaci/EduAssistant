# 🎓 PratikAi - Akıllı Öğrenme Asistanı

**Üretken Yapay Zeka Tabanlı Kişiselleştirilmiş Eğitim Etmeni**

PratikAi, eğitim materyallerinden (metin, PDF, görsel) otomatik olarak sınav soruları ve özetler üreten bir yapay zeka asistanıdır. Proje, **Üretken Yapay Zeka** ve **Etmen Tabanlı Sistem** mimarisi kullanılarak geliştirilmiştir.

## ✨ Özellikler

- 📝 **Metin/PDF/Görsel'den Soru Üretimi**: Çoktan seçmeli sorular otomatik oluşturulur
- 📄 **Özet Üretimi**: Metinlerden kısa ve öz özetler çıkarılır
- 🤖 **Etmen Tabanlı Mimari**: LearningAgent, MultiAgentSystem, MemorySystem
- 🔄 **Yedekli AI Sistemi**: Gemini çökerse otomatik Mock moduna geçer
- 📊 **Bloom Taksonomisi Analizi**: Soruların pedagojik analizi
- 📥 **PDF İndirme**: Üretilen soruları PDF olarak indirebilirsiniz
- 🎯 **Kişiselleştirilebilir**: Soru sayısı, zorluk seviyesi, soru tipi seçilebilir

## 🏗️ Mimari

```
Frontend (Next.js) → Backend API (FastAPI) → AI Provider Manager
                                                    ↓
                                    ┌───────────────┴───────────────┐
                                    │                               │
                            Gemini Provider              Mock Provider
                            (Birincil)                   (Fallback)
```

## 🚀 Kurulum

### Gereksinimler

- Python 3.11+
- Node.js 18+
- Google Gemini API Key

### Backend Kurulumu

```bash
cd PratikAi/backend

# Virtual environment oluştur (opsiyonel)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Paketleri yükle
pip install -r ../requirements.txt

# .env dosyası oluştur
echo GOOGLE_API_KEY=your_api_key_here > .env

# Backend'i başlat
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend: http://localhost:8000  
API Dokümantasyonu: http://localhost:8000/docs

### Frontend Kurulumu

```bash
cd PratikAi/frontend

# Paketleri yükle
npm install

# Frontend'i başlat
npm run dev
```

Frontend: http://localhost:3000

## 📚 API Endpoint'leri

### Klasik Endpoint'ler

- `POST /api/v1/generate-quiz-from-text` - Metinden sınav üret
- `POST /api/v1/generate-quiz-from-file` - Dosyadan sınav üret
- `POST /api/v1/generate-summary-from-text` - Metinden özet üret
- `POST /api/v1/download-quiz-pdf` - PDF indir
- `GET /api/v1/health` - Sistem durumu

### Etmen Tabanlı Endpoint'ler

- `GET /api/v1/agent/state` - Etmen durumu
- `POST /api/v1/agent/generate-quiz` - Etmen ile sınav üret
- `GET /api/v1/tools` - Kullanılabilir araçlar

### Çoklu Etmen Endpoint'leri

- `GET /api/v1/multi-agent/system-info` - Sistem bilgisi
- `POST /api/v1/multi-agent/process` - Çoklu etmen ile işlem

### Bellek Sistemi Endpoint'leri

- `GET /api/v1/memory/global-context` - Küresel bağlam
- `GET /api/v1/memory/session-context` - Oturum bağlamı
- `POST /api/v1/memory/store` - Belleğe kaydet

## 🛡️ Yedekli AI Sistemi

PratikAi, **fallback mekanizması** ile çalışır:

1. **Gemini Provider** (Birincil): Google Gemini API kullanır
2. **Mock Provider** (Fallback): Gemini çökerse otomatik devreye girer

Gemini API çökse bile proje çalışmaya devam eder! Mock modu basit sorular üretir.

Detaylar için: [README_FALLBACK.md](backend/README_FALLBACK.md)

## 📁 Proje Yapısı

```
PratikAi/
├── backend/
│   ├── main.py                    # FastAPI uygulaması
│   ├── services/
│   │   ├── gemini_service.py     # Gemini API entegrasyonu
│   │   ├── ai_provider.py         # Yedekli AI sistemi
│   │   ├── learning_agent.py      # Temel etmen
│   │   ├── multi_agent_system.py  # Çoklu etmen sistemi
│   │   ├── memory_system.py       # Bellek mimarisi
│   │   ├── tools.py               # Araç kullanımı
│   │   ├── file_processor.py      # Dosya işleme (PDF/OCR)
│   │   └── pdf_generator.py       # PDF oluşturma
│   └── .env                       # API anahtarları
│
└── frontend/
    ├── app/
    │   ├── page.js                # Ana sayfa
    │   └── components/
    │       ├── InputPanel.js      # Giriş paneli
    │       ├── QuizScreen.js       # Sınav ekranı
    │       ├── ResultsScreen.js    # Sonuç ekranı
    │       └── OutputDisplay.js   # Çıktı gösterimi
    └── package.json
```

## 🎓 Ders İçeriği Uygulaması

| Hafta | Konu | Kod Konumu |
|-------|------|------------|
| Hafta 1 | Üretici YZ Temelleri | `gemini_service.py` |
| Hafta 2 | Etmen Sistemleri | `learning_agent.py` |
| Hafta 3 | Akıllı Etmen Bileşenleri | `learning_agent.py` |
| Hafta 5 | Araç Kullanımı ve Planlama | `tools.py`, `learning_agent.py` |
| Hafta 6 | Çoklu Etmen İşbirliği | `multi_agent_system.py` |
| Hafta 7 | İleri Etmen Tasarımı | `memory_system.py` |

## 🔧 Kullanılan Teknolojiler

### Backend
- **FastAPI**: RESTful API framework
- **Google Gemini API**: Üretici yapay zeka modeli
- **PyMuPDF**: PDF işleme
- **EasyOCR**: Görsel OCR (opsiyonel)
- **FPDF**: PDF oluşturma

### Frontend
- **Next.js 15**: React framework
- **React 19**: UI kütüphanesi
- **Tailwind CSS**: Styling framework

## 📝 Kullanım Örneği

1. Frontend'te metin girin veya dosya yükleyin
2. Soru sayısı, zorluk seviyesi seçin
3. "Sınav Oluştur" butonuna tıklayın
4. Üretilen soruları görüntüleyin
5. PDF olarak indirin veya sınavı çözün

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

## 👤 Yazar

**Ali Erdem BALTACI**  
Öğrenci No: 21360859011

## 🔗 Bağlantılar

- **GitHub**: https://github.com/erdembaltaci/EduAssistant
- **API Dokümantasyonu**: http://localhost:8000/docs (Backend çalışırken)

## ⚠️ Notlar

- `.env` dosyası git'e eklenmez (güvenlik)
- EasyOCR opsiyoneldir (C compiler gerektirir)
- Gemini API key gereklidir (ücretsiz tier mevcut)

---

**⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın!**

