"""
Araç Kullanımı Servisi - Hafta 5: Araç Kullanımı ve Planlama
Function Calling ve Araç Tanımlamaları
"""

from typing import Dict, List, Any, Optional
from services.gemini_service import (
    generate_questions_from_gemini,
    generate_summary_from_gemini,
    get_recommendations,
    analyze_question_types
)


# Araç Tanımlamaları - Hafta 5: Araç Kataloğu
TOOLS = [
    {
        "name": "generate_quiz",
        "description": "Metinden çoktan seçmeli sorular üretir. Bloom taksonomisine göre sorular hazırlar.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Soru üretilecek metin içeriği"
                },
                "num_questions": {
                    "type": "integer",
                    "description": "Üretilecek soru sayısı (varsayılan: 5)",
                    "default": 5
                },
                "difficulty": {
                    "type": "string",
                    "description": "Zorluk seviyesi: kolay, orta, zor",
                    "enum": ["kolay", "orta", "zor"],
                    "default": "orta"
                },
                "question_type": {
                    "type": "string",
                    "description": "Soru tipi",
                    "enum": ["çoktan seçmeli", "açık uçlu"],
                    "default": "çoktan seçmeli"
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "generate_summary",
        "description": "Metinden kısa ve öz bir özet oluşturur. Ana fikirleri çıkarır.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Özetlenecek metin içeriği"
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "analyze_text",
        "description": "Metni analiz eder ve öneriler oluşturur. Anahtar kelimeler çıkarır ve kaynak önerileri sunar.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Analiz edilecek metin içeriği"
                }
            },
            "required": ["text"]
        }
    }
]


def call_tool(tool_name: str, parameters: Dict[str, Any], model: Optional[Any] = None) -> Dict[str, Any]:
    """
    Araç çağırma fonksiyonu - Hafta 5: Function Calling
    
    Args:
        tool_name: Çağrılacak aracın adı
        parameters: Araç parametreleri
        model: Gemini modeli (opsiyonel, şu anda kullanılmıyor)
    
    Returns:
        Araç sonucu
    """
    if tool_name == "generate_quiz":
        text = parameters.get("text", "")
        num_questions = parameters.get("num_questions", 5)
        difficulty = parameters.get("difficulty", "orta")
        question_type = parameters.get("question_type", "çoktan seçmeli")
        
        result = generate_questions_from_gemini(text, num_questions, question_type, difficulty)
        return {
            "tool": "generate_quiz",
            "status": "success",
            "result": result
        }
    
    elif tool_name == "generate_summary":
        text = parameters.get("text", "")
        summary = generate_summary_from_gemini(text)
        recommendations = get_recommendations(text)
        
        return {
            "tool": "generate_summary",
            "status": "success",
            "summary": summary,
            "recommendations": recommendations
        }
    
    elif tool_name == "analyze_text":
        text = parameters.get("text", "")
        recommendations = get_recommendations(text)
        
        return {
            "tool": "analyze_text",
            "status": "success",
            "recommendations": recommendations,
            "text_length": len(text),
            "word_count": len(text.split())
        }
    
    else:
        return {
            "tool": tool_name,
            "status": "error",
            "error": f"Bilinmeyen araç: {tool_name}"
        }


def get_tool_descriptions() -> List[Dict[str, Any]]:
    """
    Araç tanımlamalarını döndürür - Hafta 5: Araç Kataloğu
    
    Returns:
        Araç tanımlamaları listesi
    """
    return TOOLS


def get_tool_by_name(tool_name: str) -> Optional[Dict[str, Any]]:
    """
    İsme göre araç bulma - Hafta 5: Araç Arama
    
    Args:
        tool_name: Aranacak araç adı
    
    Returns:
        Araç tanımı veya None
    """
    for tool in TOOLS:
        if tool["name"] == tool_name:
            return tool
    return None

