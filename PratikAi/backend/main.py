import os
import re
from fastapi import FastAPI, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List, Dict, Any
from dotenv import load_dotenv
from pathlib import Path

# Servis dosyalarımızdaki fonksiyonları import ediyoruz
from services.gemini_service import init_gemini, generate_questions_from_gemini, generate_summary_from_gemini, get_recommendations
from services.file_processor import process_uploaded_file
from services.pdf_generator import create_quiz_pdf
from services.learning_agent import LearningAgent, create_learning_agent
from services.tools import call_tool, get_tool_descriptions
from services.multi_agent_system import get_multi_agent_system
from services.memory_system import get_memory_system

# .env dosyasını manuel olarak yükle
load_dotenv()

# API anahtarını burada oku
api_key = os.getenv("GOOGLE_API_KEY")

# Gemini servisini okuduğumuz anahtarla başlat (eski kod - uyumluluk için)
init_gemini(api_key)

# AI Provider Manager'ı başlat (Fallback mekanizması)
from services.ai_provider import get_ai_provider_manager
ai_provider_manager = get_ai_provider_manager()

# Etmen oluştur - Hafta 2: Etmen Sistemleri
learning_agent = create_learning_agent()

# Çoklu Etmen Sistemi - Hafta 6: MAS
multi_agent_system = get_multi_agent_system()

# Bellek Sistemi - Hafta 7: Bellek Mimarisi
memory_system = get_memory_system()

app = FastAPI(title="PratikAi API")

# CORS Ayarları
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API ENDPOINT'LERİ ---

@app.get("/api/v1/health", tags=["General"])
def read_health():
    """Uygulamanın ayakta olup olmadığını kontrol eder."""
    # AI Provider durumunu kontrol et
    current_provider = ai_provider_manager.get_provider()
    provider_name = current_provider.__class__.__name__ if current_provider else "None"
    
    return {
        "status": "OK",
        "ai_provider": provider_name,
        "ai_available": current_provider.is_available() if current_provider else False
    }

@app.post("/api/v1/generate-quiz-from-text", tags=["Quiz Generation"])
def generate_quiz_from_text(
    text: str = Form(...),
    num_questions: int = Form(5),
    question_type: str = Form("çoktan seçmeli"),
    difficulty: str = Form("orta"),
    user_id: str = Form(None)  # Chapter 4: Kullanıcı tercihlerini hatırlama
):
    """
    Doğrudan metin alıp sınav ve tavsiye üretir.
    Chapter 4: Self-Explanation ve Memory System entegrasyonu
    """
    # Chapter 4: Kullanıcı tercihlerini Memory System'den al
    user_preferences = {}
    if user_id:
        user_profile = memory_system.long_term.get_user_profile(user_id)
        if user_profile:
            user_preferences = user_profile.get("preferences", {})
            # Kullanıcı tercihlerini uygula
            if "preferred_num_questions" in user_preferences:
                num_questions = user_preferences["preferred_num_questions"]
            if "preferred_difficulty" in user_preferences:
                difficulty = user_preferences["preferred_difficulty"]
    
    # Agent ile akıl yürütme (Chapter 4: Self-Explanation için)
    perceived_data = learning_agent.perceive({
        "text": text,
        "file_type": "text",
        "preferences": user_preferences
    })
    reasoning_result = learning_agent.reason(perceived_data, goal="generate_quiz")
    
    # Kullanıcı seçimlerini uygula
    reasoning_result["num_questions"] = num_questions
    reasoning_result["difficulty"] = difficulty
    
    # Soruları üret
    result = generate_questions_from_gemini(text, num_questions, question_type, difficulty)
    
    # Chapter 4: Self-Explanation ekle
    result["explanation"] = reasoning_result.get("explanation", "")
    result["reasoning"] = {
        "strategy": reasoning_result.get("strategy"),
        "weights": learning_agent.self_model["preference_weights"]
    }
    
    # Memory System'e kaydet
    if user_id:
        memory_system.long_term.store_learning_history(user_id, {
            "action": "generate_quiz",
            "num_questions": num_questions,
            "difficulty": difficulty,
            "text_length": len(text)
        })
    
    return result

@app.post("/api/v1/generate-quiz-from-file", tags=["Quiz Generation"])
async def generate_quiz_from_file(
    file: UploadFile = File(...),
    num_questions: int = Form(5),
    question_type: str = Form("çoktan seçmeli"),
    difficulty: str = Form("orta")
):
    """Dosya (resim, pdf) alıp metni çıkarır ve sınav/tavsiye üretir."""
    extracted_text = await process_uploaded_file(file)
    return generate_questions_from_gemini(extracted_text, num_questions, question_type, difficulty)

@app.post("/api/v1/generate-summary-from-text", tags=["Summary Generation"])
def generate_summary_from_text(text: str = Form(...)):
    """Doğrudan metin alıp özet ve tavsiye üretir."""
    summary = generate_summary_from_gemini(text)
    recommendations = get_recommendations(text)
    return {"summary": summary, "recommendations": recommendations}

@app.post("/api/v1/generate-summary-from-file", tags=["Summary Generation"])
async def generate_summary_from_file(file: UploadFile = File(...)):
    """Dosya (resim, pdf) alıp metni çıkarır ve özet/tavsiye üretir."""
    extracted_text = await process_uploaded_file(file)
    summary = generate_summary_from_gemini(extracted_text)
    recommendations = get_recommendations(extracted_text)
    return {"summary": summary, "recommendations": recommendations}

@app.post("/api/v1/download-quiz-pdf", tags=["PDF Generation"])
def download_quiz_pdf(quiz_data: List[Dict[str, Any]] = Body(...)):
    """Sınav verisini (JSON) alıp PDF dosyasına dönüştürür."""
    pdf_path = create_quiz_pdf(quiz_data)
    return FileResponse(path=pdf_path, media_type='application/pdf', filename='PratikAi_Sinavi.pdf')

# --- ETMEN TABANLI ENDPOINT'LER - Hafta 2, 3, 5 ---

@app.get("/api/v1/agent/state", tags=["Agent"])
def get_agent_state():
    """Etmen durumunu döndürür - Hafta 2: Etmen Durum Yönetimi"""
    return learning_agent.get_state()

@app.post("/api/v1/agent/generate-quiz", tags=["Agent"])
async def agent_generate_quiz(
    text: str = Form(...),
    num_questions: int = Form(5),
    difficulty: str = Form("orta"),
    user_id: str = Form(None)  # Chapter 4: Kullanıcı tercihlerini hatırlama
):
    """
    Etmen tabanlı sınav üretimi - Hafta 2, 3, 5: Etmen Mimarisi
    Chapter 4: Self-Explanation, Meta-Reasoning, Self-Modeling eklendi
    
    Bu endpoint, dersin temel kavramlarını gösterir:
    - Algılama (Perception)
    - Akıl Yürütme (Reasoning)
    - Planlama (Planning)
    - Eylem (Action)
    - Self-Explanation (Chapter 4: Transparency)
    """
    # Chapter 4: Kullanıcı tercihlerini Memory System'den al
    user_preferences = {}
    if user_id:
        user_profile = memory_system.long_term.get_user_profile(user_id)
        if user_profile:
            user_preferences = user_profile.get("preferences", {})
    
    # 1. Algılama (Perception) - Hafta 2
    perceived_data = learning_agent.perceive({
        "text": text,
        "file_type": "text",
        "preferences": user_preferences
    })
    
    # 2. Akıl Yürütme (Reasoning) - Hafta 3, Chapter 4: Self-Explanation
    reasoning_result = learning_agent.reason(perceived_data, goal="generate_quiz")
    
    # Planlama parametrelerini güncelle
    reasoning_result["num_questions"] = num_questions
    reasoning_result["difficulty"] = difficulty
    
    # 3. Planlama (Planning) - Hafta 5
    plan = learning_agent.plan("generate_quiz", reasoning_result)
    
    # 4. Eylem (Action) - Hafta 2, 5: Araç Kullanımı
    def external_function(**kwargs):
        return call_tool("generate_quiz", {
            "text": text,
            "num_questions": kwargs.get("num_questions", num_questions),
            "difficulty": kwargs.get("difficulty", difficulty)
        }, None)
    
    results = learning_agent.act(plan, external_function)
    
    # Chapter 4: Self-Explanation ekle
    explanation = learning_agent.get_explanation()
    
    return {
        "agent_state": learning_agent.get_state(),
        "perception": perceived_data,
        "reasoning": reasoning_result,
        "plan": plan,
        "results": results.get("soru_uretim", {}),
        "explanation": explanation,  # Chapter 4: Self-Explanation
        "self_model": learning_agent.self_model  # Chapter 4: Self-Modeling
    }

@app.get("/api/v1/tools", tags=["Agent"])
def list_tools():
    """Kullanılabilir araçları listeler - Hafta 5: Araç Kullanımı"""
    return {"tools": get_tool_descriptions()}

# --- ÇOKLU ETMEN SİSTEMİ ENDPOINT'LERİ - Hafta 6 ---

@app.get("/api/v1/multi-agent/system-info", tags=["Multi-Agent"])
def get_multi_agent_system_info():
    """Çoklu etmen sistemi bilgisi - Hafta 6: MAS Durumu"""
    return multi_agent_system.get_system_info()

@app.post("/api/v1/multi-agent/process", tags=["Multi-Agent"])
async def multi_agent_process(
    text: str = Form(...),
    goal: str = Form("generate_quiz"),
    num_questions: int = Form(5),
    difficulty: str = Form("orta")
):
    """
    Çoklu etmen sistemi ile işlem - Hafta 6: CWD Modeli
    
    Bu endpoint, CWD (Coordinator-Worker-Delegator) modelini gösterir:
    - Coordinator: Genel süreç yönetimi
    - Delegator: Görev dağıtımı
    - Workers: Uzman etmenler (soru üretici, özet üretici, analizci, önerici)
    """
    input_data = {
        "text": text,
        "file_type": "text",
        "preferences": {
            "num_questions": num_questions,
            "difficulty": difficulty
        }
    }
    
    result = multi_agent_system.process_request(goal, input_data)
    
    # Bellek sistemine kaydet - Hafta 7
    memory_system.store_context("episodic", "multi_agent_request", {
        "goal": goal,
        "input": input_data,
        "result": result
    })
    
    return result

# --- BELLEK SİSTEMİ ENDPOINT'LERİ - Hafta 7 ---

@app.get("/api/v1/memory/global-context", tags=["Memory"])
def get_global_context():
    """Küresel bağlam - Hafta 7: Küresel Bağlam"""
    return memory_system.get_global_context()

@app.get("/api/v1/memory/session-context", tags=["Memory"])
def get_session_context():
    """Oturum bağlamı - Hafta 7: Oturum Bağlamı"""
    return memory_system.get_session_context()

@app.get("/api/v1/memory/task-context/{task_id}", tags=["Memory"])
def get_task_context(task_id: str):
    """Görev bağlamı - Hafta 7: Görev Bağlamı"""
    return memory_system.get_task_context(task_id)

@app.post("/api/v1/memory/store", tags=["Memory"])
def store_memory(
    context_type: str = Form(...),
    key: str = Form(...),
    value: str = Form(...)
):
    """Belleğe kaydet - Hafta 7: Bellek Depolama"""
    import json
    try:
        value_dict = json.loads(value)
    except:
        value_dict = {"text": value}
    
    memory_system.store_context(context_type, key, value_dict)
    return {"status": "stored", "context_type": context_type, "key": key}

@app.get("/api/v1/memory/retrieve", tags=["Memory"])
def retrieve_memory(
    context_type: str,
    key: str
):
    """Bellekten al - Hafta 7: Bellek Erişimi"""
    value = memory_system.retrieve_context(context_type, key)
    return {"key": key, "value": value}

@app.post("/api/v1/memory/switch-context", tags=["Memory"])
def switch_context(session_id: str = Form(...)):
    """Bağlam değiştir - Hafta 7: Context Switching"""
    memory_system.switch_context(session_id)
    return {"status": "switched", "new_session_id": session_id}

# --- CHAPTER 4: REFLECTION AND INTROSPECTION ENDPOINT'LERİ ---

@app.post("/api/v1/feedback", tags=["Chapter 4"])
def submit_feedback(
    satisfaction: str = Form(...),  # "positive", "negative", "neutral"
    preferred_difficulty: str = Form(None),
    preferred_num_questions: int = Form(None),
    user_id: str = Form(None),
    explanation: str = Form(None)  # Kullanıcının açıklaması
):
    """
    Chapter 4: Meta-Reasoning - Kullanıcı feedback'i al ve agent'ı öğret
    Feedback'e göre agent'ın ağırlıklarını ve tercihlerini günceller
    """
    feedback_data = {
        "satisfaction": satisfaction,
        "preferred_difficulty": preferred_difficulty,
        "preferred_num_questions": preferred_num_questions,
        "user_explanation": explanation
    }
    
    # Agent'a feedback'i öğret (Chapter 4: Meta-Reasoning)
    learning_agent.learn({
        "user_feedback": feedback_data,
        "timestamp": None  # Gerçek uygulamada datetime kullanılır
    })
    
    # Memory System'e kaydet
    if user_id:
        # Kullanıcı profili güncelle
        memory_system.long_term.store_user_profile(user_id, {
            "preferences": {
                "preferred_difficulty": preferred_difficulty,
                "preferred_num_questions": preferred_num_questions
            },
            "last_feedback": feedback_data
        })
        
        # Öğrenme geçmişine ekle
        memory_system.long_term.store_learning_history(user_id, {
            "action": "feedback",
            "feedback": feedback_data
        })
    
    return {
        "status": "feedback_received",
        "agent_updated": True,
        "new_weights": learning_agent.self_model["preference_weights"],
        "message": "Agent feedback'inize göre öğrendi ve ağırlıklarını güncelledi."
    }

@app.get("/api/v1/agent/explanation", tags=["Chapter 4"])
def get_agent_explanation():
    """
    Chapter 4: Self-Explanation - Agent'ın son kararının açıklamasını döndür
    """
    return {
        "explanation": learning_agent.get_explanation(),
        "reasoning_result": learning_agent.knowledge_base.get("reasoning_result", {}),
        "preference_weights": learning_agent.self_model["preference_weights"]
    }

@app.post("/api/v1/agent/update-goals", tags=["Chapter 4"])
def update_agent_goals(
    prefer_difficult: bool = Form(False),
    prefer_personalized: bool = Form(True)
):
    """
    Chapter 4: Self-Modeling - Agent'ın hedeflerini güncelle
    """
    learning_agent.update_goals({
        "prefer_difficult": prefer_difficult,
        "prefer_personalized": prefer_personalized
    })
    
    return {
        "status": "goals_updated",
        "new_goals": learning_agent.self_model["goals"]
    }

@app.get("/api/v1/agent/self-model", tags=["Chapter 4"])
def get_agent_self_model():
    """
    Chapter 4: Self-Modeling - Agent'ın kendi modelini döndür
    """
    return {
        "self_model": learning_agent.self_model,
        "feedback_history_count": len(learning_agent.feedback_history),
        "last_feedback": learning_agent.feedback_history[-1] if learning_agent.feedback_history else None
    }