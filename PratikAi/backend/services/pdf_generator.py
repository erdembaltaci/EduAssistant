from fpdf import FPDF
from typing import List, Dict, Any

def create_quiz_pdf(quiz_data: List[Dict[str, Any]]) -> str:
    """
    Verilen sınav verisinden bir PDF dosyası oluşturur ve dosya yolunu döndürür.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Türkçe karakterler için fontu ekliyoruz.
    # Bu dosyanın ana 'backend' klasöründe olduğundan emin ol.
    try:
        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        pdf.set_font('DejaVu', '', 12)
    except RuntimeError:
        print("HATA: DejaVuSans.ttf font dosyası bulunamadı. Lütfen backend klasörüne ekleyin.")
        pdf.set_font('Arial', '', 12) # Hata durumunda varsayılan font
    
    pdf.cell(0, 10, 'PratikAi Sınavı', ln=True, align='C')
    pdf.ln(10)

    for i, q in enumerate(quiz_data):
        # Ham metin varsa (çoktan seçmeli değilse), onu yazdır
        if q.get('raw_text'):
            pdf.multi_cell(0, 8, f"{i+1}. {q.get('raw_text')}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(10)
            continue
        
        # Çoktan seçmeli soru ve şıklarını yazdır
        pdf.multi_cell(0, 8, f"{i+1}. {q.get('question', '')}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)
        options = q.get('options', {})
        for key, value in options.items():
            pdf.multi_cell(0, 8, f"  {key}) {value}", new_x="LMARGIN", new_y="NEXT")
        
        # Cevap Anahtarını ekle
        pdf.ln(5)
        pdf.multi_cell(0, 8, f"--> Doğru Cevap: {q.get('correct_answer', '')}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)

    pdf_file_path = "temp_quiz.pdf"
    pdf.output(pdf_file_path)
    return pdf_file_path