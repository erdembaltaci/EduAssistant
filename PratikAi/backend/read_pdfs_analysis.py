import sys
import os
sys.path.append(os.path.dirname(__file__))

import fitz

def read_pdf(pdf_path):
    """PDF dosyasını oku ve metnini döndür"""
    try:
        full_path = os.path.join(os.path.dirname(__file__), '..', '..', pdf_path)
        doc = fitz.open(full_path)
        text = '\n'.join([page.get_text() for page in doc])
        doc.close()
        return text
    except Exception as e:
        return f"Error reading {pdf_path}: {e}"

if __name__ == "__main__":
    # Proje öneri formu
    print("=" * 80)
    print("PROJE ÖNERİ FORMU")
    print("=" * 80)
    proje_formu = read_pdf("ProjeOneriFormu_AliErdemBaltaci_21360859011.pdf")
    print(proje_formu)
    
    # Hafta dosyalarını oku
    haftalar = {
        "Hafta 1": "Hafta 1.pdf",
        "Hafta 2": "hafta 2.pdf", 
        "Hafta 3": "Hafta 3.pptx.pdf",
        "Hafta 5": "Hafta 5.pdf",
        "Hafta 6": "Hafta 6.pdf",
        "Hafta 7": "Hafta 7.pdf"
    }
    
    hafta_icerikleri = {}
    for hafta_adi, dosya_adi in haftalar.items():
        print("\n\n" + "=" * 80)
        print(hafta_adi.upper())
        print("=" * 80)
        icerik = read_pdf(dosya_adi)
        print(icerik)
        hafta_icerikleri[hafta_adi] = icerik
    
    # Analiz için dosyaya kaydet
    with open(os.path.join(os.path.dirname(__file__), '..', '..', 'analiz_raporu.txt'), 'w', encoding='utf-8') as f:
        f.write("PROJE ÖNERİ FORMU\n")
        f.write("=" * 80 + "\n")
        f.write(proje_formu)
        f.write("\n\n")
        
        for hafta_adi, icerik in hafta_icerikleri.items():
            f.write("\n\n" + "=" * 80 + "\n")
            f.write(f"{hafta_adi.upper()}\n")
            f.write("=" * 80 + "\n")
            f.write(icerik)
    
    print("\n\nAnaliz tamamlandı! İçerik 'analiz_raporu.txt' dosyasına kaydedildi.")


