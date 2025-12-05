"""
PDF analiz scripti - Proje öneri formu ve hafta içeriklerini okur
"""
import sys
import os

# Backend dizinini path'e ekle
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# PyMuPDF'i import et
try:
    import fitz
except ImportError:
    print("PyMuPDF (fitz) modülü bulunamadı. Lütfen requirements.txt'deki paketleri yükleyin.")
    sys.exit(1)

def read_pdf_content(pdf_path):
    """PDF dosyasını oku ve metnini döndür"""
    try:
        if not os.path.exists(pdf_path):
            return f"Dosya bulunamadı: {pdf_path}"
        
        doc = fitz.open(pdf_path)
        pages_text = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            pages_text.append(f"--- Sayfa {page_num + 1} ---\n{text}")
        doc.close()
        return "\n\n".join(pages_text)
    except Exception as e:
        return f"Hata ({pdf_path}): {str(e)}"

def main():
    # Ana dizin
    base_dir = os.path.dirname(os.path.dirname(backend_dir))
    
    # PDF dosyalarının yolları
    pdfs = {
        "Proje Öneri Formu": os.path.join(base_dir, "ProjeOneriFormu_AliErdemBaltaci_21360859011.pdf"),
        "Hafta 1": os.path.join(base_dir, "Hafta 1.pdf"),
        "Hafta 2": os.path.join(base_dir, "hafta 2.pdf"),
        "Hafta 3": os.path.join(base_dir, "Hafta 3.pptx.pdf"),
        "Hafta 5": os.path.join(base_dir, "Hafta 5.pdf"),
        "Hafta 6": os.path.join(base_dir, "Hafta 6.pdf"),
        "Hafta 7": os.path.join(base_dir, "Hafta 7.pdf"),
    }
    
    results = {}
    
    print("PDF dosyaları okunuyor...\n")
    
    for name, path in pdfs.items():
        print(f"Okunuyor: {name}...")
        content = read_pdf_content(path)
        results[name] = content
        print(f"✓ {name} okundu ({len(content)} karakter)\n")
    
    # Sonuçları dosyaya kaydet
    output_file = os.path.join(base_dir, "pdf_analiz_raporu.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        for name, content in results.items():
            f.write("\n" + "=" * 100 + "\n")
            f.write(f"{name.upper()}\n")
            f.write("=" * 100 + "\n\n")
            f.write(content)
            f.write("\n\n")
    
    print(f"\n✓ Tüm PDF'ler okundu ve '{output_file}' dosyasına kaydedildi.")
    
    return results

if __name__ == "__main__":
    results = main()


