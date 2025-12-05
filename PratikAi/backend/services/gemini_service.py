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
        # Güncel model adı
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
        except:
            try:
                model = genai.GenerativeModel('gemini-2.0-flash')
            except:
                model = genai.GenerativeModel('gemini-pro')
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
    """
    Ana sınav üretme fonksiyonu. 
    Fallback mekanizması ile çalışır: Gemini -> OpenAI -> Mock
    """
    if not text or len(text.strip()) < 20:
        return {"questions": [{"error": "Soru üretmek için yetersiz metin."}]}
    
    # Fallback mekanizması ile soru üret
    from services.ai_provider import get_ai_provider_manager
    
    try:
        manager = get_ai_provider_manager()
        result = manager.generate_questions_with_fallback(text, num_questions, question_type, difficulty)
        
        # Recommendations ekle (Gemini'den bağımsız)
        try:
            recommendations = get_recommendations(text)
            result["recommendations"] = recommendations
        except:
            result["recommendations"] = []
        
        return result
    except Exception as e:
        print(f"❌ Tüm AI provider'lar başarısız: {e}")
        return {
            "questions": [{"error": f"AI servisleri şu anda kullanılamıyor: {e}"}],
            "recommendations": [],
            "feedback": None,
            "provider": "none"
        }

def generate_summary_from_gemini(text: str) -> str:
    """
    Metin özeti üretme fonksiyonu.
    Fallback mekanizması ile çalışır: Gemini -> OpenAI -> Mock
    """
    if not text or len(text.strip()) < 20:
        return "Özet üretmek için yetersiz metin."
    
    # Fallback mekanizması ile özet üret
    from services.ai_provider import get_ai_provider_manager
    
    try:
        manager = get_ai_provider_manager()
        return manager.generate_summary_with_fallback(text)
    except Exception as e:
        print(f"❌ Tüm AI provider'lar başarısız: {e}")
        return f"AI servisleri şu anda kullanılamıyor: {e}"

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