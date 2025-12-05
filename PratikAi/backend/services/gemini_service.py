import os
import re
from typing import List, Dict, Any
import google.generativeai as genai

# --- GLOBAL DEĞİŞKENLER VE MODEL YÜKLEME ---

# Uygulama genelinde kullanılacak Gemini modelini başlangıçta None olarak tanımlıyoruz.
model = None

def init_gemini(api_key: str):
    """
    Verilen API anahtarıyla Gemini modelini yapılandırır ve başlatır.
    Bu fonksiyon ana uygulama (main.py) tarafından sadece bir kez çağrılır.
    """
    global model
    try:
        if not api_key:
            raise ValueError("API anahtarı bulunamadı veya boş.")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        print("Google Gemini API başarıyla yapılandırıldı.")
    except Exception as e:
        print(f"HATA: Google Gemini API yapılandırılamadı. Hata: {e}")
        model = None

# --- YARDIMCI FONKSİYONLAR ---

def parse_quiz_text(raw_text: str) -> List[Dict[str, Any]]:
    """
    Gemini API'den gelen ham metin formatındaki sınavı, yapısal bir listeye dönüştürür.
    Regex kullanarak soru, şıklar ve cevapları ayrıştırır.
    """
    questions = []
    # Gelen metni, her sorunun başlangıcını belirten desene göre böler.
    question_blocks = re.split(r'\*\*\d+\.\s+Soru:\*\*', raw_text)

    for block in question_blocks:
        if not block.strip():
            continue
        try:
            # Regex desenleri ile her bir bileşeni (soru, şıklar, cevap) yakala
            question_text = re.search(r'(.*?)\nA\)', block, re.DOTALL).group(1).strip()
            option_a = re.search(r'A\)\s(.*?)\nB\)', block, re.DOTALL).group(1).strip()
            option_b = re.search(r'B\)\s(.*?)\nC\)', block, re.DOTALL).group(1).strip()
            option_c = re.search(r'C\)\s(.*?)\nD\)', block, re.DOTALL).group(1).strip()
            option_d = re.search(r'D\)\s(.*?)\n', block, re.DOTALL).group(1).strip()
            correct_answer = re.search(r'\*\*Doğru Cevap:\s+([A-D])\*\*', block).group(1).strip()

            questions.append({
                "question": question_text,
                "options": {"A": option_a, "B": option_b, "C": option_c, "D": option_d},
                "correct_answer": correct_answer
            })
        except AttributeError:
            # Eğer API'den gelen format beklenenden farklıysa ve bir blok ayrıştırılamazsa,
            # hatayı terminale yazdır ve diğer sorularla devam et.
            print(f"Aşağıdaki blok ayrıştırılamadı:\n{block}")
            continue
    return questions

def analyze_question_types(questions: List[Dict[str, Any]]) -> str:
    """
    Üretilen soruları anahtar kelimelere göre analiz eder ve metnin kalitesi
    hakkında pedagojik bir geri bildirim oluşturur.
    """
    if not questions:
        return None

    # Bloom Taksonomisine göre basit bir sınıflandırma
    knowledge_keywords = ["nedir", "kimdir", "nerede", "ne zaman", "hangisidir", "tanımla"]
    comprehension_keywords = ["neden", "nasıl", "açıkla", "karşılaştır", "yorumla", "örnek ver"]

    knowledge_count = 0
    comprehension_count = 0

    for q_data in questions:
        question_text = q_data.get("question", "").lower()
        if any(keyword in question_text for keyword in comprehension_keywords):
            comprehension_count += 1
        elif any(keyword in question_text for keyword in knowledge_keywords):
            knowledge_count += 1
    
    total_questions = len(questions)
    if total_questions == 0:
        return None

    knowledge_percentage = (knowledge_count / total_questions) * 100
    
    if knowledge_percentage > 70:
        return f"Üretilen soruların ~%{int(knowledge_percentage)}'i bilgi düzeyindedir. Metninize neden-sonuç ilişkileri ekleyerek kavrama düzeyindeki (neden, nasıl) soruları artırabilirsiniz."
    elif knowledge_percentage < 30:
         return f"Üretilen soruların büyük çoğunluğu kavrama ve analiz düzeyindedir. Bu, öğrencilerin konuyu derinlemesine anlama yeteneğini ölçmek için harikadır."
    
    return "Üretilen sorular, hem bilgi hem de kavrama düzeyini ölçen dengeli bir dağılıma sahiptir."

# --- ANA SERVİS FONKSİYONLARI ---

def generate_questions_from_gemini(text: str, num_questions: int, question_type: str, difficulty: str) -> Dict[str, Any]:
    """Ana sınav üretme fonksiyonu. Gemini'ye istek gönderir ve sonuçları işler."""
    if not model or not text or len(text.strip()) < 20:
        return {"questions": [{"error": "Soru üretmek için yetersiz metin veya API hatası."}]}
    
    prompt = f"""
    Aşağıdaki metni analiz et ve bu metinden {num_questions} adet {difficulty} zorluk seviyesinde {question_type} soru oluştur.
    Eğer soru tipi çoktan seçmeli ise 4 şık ve doğru cevabı belirt.
    Metin: "{text}"
    Çoktan seçmeli için örnek çıktı formatı:
    **1. Soru:** Soru metni burada yer alacak?
    A) Şık A
    B) Şık B
    C) Şık C
    D) Şık D
    **Doğru Cevap: B**
    """
    try:
        response = model.generate_content(prompt)
        recommendations = get_recommendations(text)
        
        if question_type == "çoktan seçmeli":
            parsed_questions = parse_quiz_text(response.text)
            feedback = analyze_question_types(parsed_questions)
            return {"questions": parsed_questions, "recommendations": recommendations, "feedback": feedback}
        else:
            # Diğer soru tipleri için şimdilik ham metni ve tavsiyeleri döndür.
            # Geri bildirim şimdilik sadece çoktan seçmeli için çalışıyor.
            return {"questions": [{"raw_text": response.text}], "recommendations": recommendations, "feedback": None}
    except Exception as e:
        print(f"Gemini API isteği sırasında hata: {e}")
        return {"questions": [{"error": f"Yapay zeka ile iletişim kurulurken bir hata oluştu: {e}"}]}

def generate_summary_from_gemini(text: str) -> str:
    """Metni Gemini API'ye gönderip özetini alır."""
    if not model or not text or len(text.strip()) < 20:
        return "Özet üretmek için yetersiz metin veya API hatası."
    
    prompt = f"""
    Aşağıdaki metni analiz et ve ana fikirlerini içeren, yaklaşık 3-4 cümlelik kısa bir özet çıkar.
    Metin: "{text}"
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API isteği sırasında hata: {e}")
        return f"Yapay zeka ile iletişim kurulurken bir hata oluştu: {e}"

def get_recommendations(text: str) -> List[Dict[str, str]]:
    """Metinden anahtar kelimeler çıkarır ve arama linkleri oluşturur."""
    if not model or not text or len(text.strip()) < 20:
        return []
    
    prompt = f"""
    Aşağıdaki metnin ana konusunu ve en önemli 3 anahtar kelimesini belirle. 
    Cevabı sadece virgülle ayrılmış şekilde ver. Örnek: Biyoloji, Hücre Yapısı, Metabolizma
    Metin: "{text}"
    """
    try:
        response = model.generate_content(prompt)
        keywords = [kw.strip() for kw in response.text.split(',') if kw.strip()]
        
        recommendations = []
        for kw in keywords:
            # URL'lerdeki özel karakter sorunlarını önlemek için metni encode et
            encoded_kw = re.sub(r'\s+', '+', kw)
            recommendations.append({
                "title": f"'{kw}' için Google'da Ara",
                "url": f"https://www.google.com/search?q={encoded_kw}"
            })
            recommendations.append({
                "title": f"'{kw}' için YouTube'da Video Ara",
                "url": f"https://www.youtube.com/results?search_query={encoded_kw}"
            })
        return recommendations
    except Exception as e:
        print(f"Tavsiye üretilirken hata: {e}")
        return []