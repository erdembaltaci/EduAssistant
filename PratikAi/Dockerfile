# Python'un resmi, hafif bir versiyonunu temel al
FROM python:3.11-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Ana dizindeki requirements.txt dosyasını kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projenin Backend klasörünün tamamını kopyala
COPY Backend/ .

# Uvicorn sunucusunu 7860 portunda çalıştır
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
