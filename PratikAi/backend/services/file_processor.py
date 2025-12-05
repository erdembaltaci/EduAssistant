import easyocr
import fitz
import os
import shutil
from fastapi import UploadFile

# OCR modelini bu dosyada yüklüyoruz
reader = easyocr.Reader(['tr', 'en'])
print("OCR Modeli başarıyla yüklendi.")

async def process_uploaded_file(file: UploadFile) -> str:
    """
    Yüklenen bir dosyayı (PDF veya resim) işleyip metin içeriğini döndürür.
    Geçici bir dosya oluşturur ve işlem sonrası siler.
    """
    # Dosya adında güvenlik için sadece temel karakterlere izin ver
    safe_filename = "".join(c for c in file.filename if c.isalnum() or c in ('.', '_')).rstrip()
    file_path = f"temp_{safe_filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = ""
    try:
        if file.filename.lower().endswith('.pdf'):
            # PDF ise, PyMuPDF ile metni oku
            with fitz.open(file_path) as doc:
                for page in doc:
                    extracted_text += page.get_text()
        else:
            # Resim ise, EasyOCR ile metni oku
            result = reader.readtext(file_path)
            extracted_text = " ".join([item[1] for item in result])
    except Exception as e:
        print(f"Dosya işlenirken hata oluştu: {e}")
    finally:
        # Geçici dosyayı her durumda sil
        if os.path.exists(file_path):
            os.remove(file_path)
    
    return extracted_text