"""
AI Provider Abstraction Layer - Yedekli AI Sistemi
Gemini çökerse otomatik olarak alternatif provider'a geçer
"""

import os
from typing import Dict, List, Any, Optional
from enum import Enum
from abc import ABC, abstractmethod


class AIProvider(Enum):
    """Desteklenen AI Provider'lar"""
    GEMINI = "gemini"
    MOCK = "mock"  # Offline test için
    # OPENAI ve CLAUDE gelecekte eklenebilir


class BaseAIProvider(ABC):
    """AI Provider için temel arayüz"""
    
    @abstractmethod
    def generate_questions(self, text: str, num_questions: int, question_type: str, difficulty: str) -> Dict[str, Any]:
        """Soru üret"""
        pass
    
    @abstractmethod
    def generate_summary(self, text: str) -> str:
        """Özet üret"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Provider kullanılabilir mi?"""
        pass


class GeminiProvider(BaseAIProvider):
    """Google Gemini Provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = None
        self._initialize()
    
    def _initialize(self):
        """Gemini'yi başlat"""
        try:
            if not self.api_key:
                raise ValueError("Gemini API anahtarı bulunamadı")
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
            print("✅ Gemini Provider başarıyla yapılandırıldı")
        except Exception as e:
            print(f"⚠️ Gemini Provider başlatılamadı: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """Gemini kullanılabilir mi?"""
        return self.model is not None
    
    def generate_questions(self, text: str, num_questions: int, question_type: str, difficulty: str) -> Dict[str, Any]:
        """Gemini ile soru üret"""
        if not self.is_available():
            raise Exception("Gemini kullanılamıyor")
        
        from services.gemini_service import parse_quiz_text, analyze_question_types, get_recommendations
        
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
            response = self.model.generate_content(prompt)
            recommendations = get_recommendations(text)
            
            if question_type == "çoktan seçmeli":
                parsed_questions = parse_quiz_text(response.text)
                feedback = analyze_question_types(parsed_questions)
                return {
                    "questions": parsed_questions,
                    "recommendations": recommendations,
                    "feedback": feedback,
                    "provider": "gemini"
                }
            else:
                return {
                    "questions": [{"raw_text": response.text}],
                    "recommendations": recommendations,
                    "feedback": None,
                    "provider": "gemini"
                }
        except Exception as e:
            print(f"❌ Gemini API hatası: {e}")
            raise
    
    def generate_summary(self, text: str) -> str:
        """Gemini ile özet üret"""
        if not self.is_available():
            raise Exception("Gemini kullanılamıyor")
        
        prompt = f"""
        Aşağıdaki metni analiz et ve ana fikirlerini içeren, yaklaşık 3-4 cümlelik kısa bir özet çıkar.
        Metin: "{text}"
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ Gemini API hatası: {e}")
            raise


class OpenAIProvider(BaseAIProvider):
    """OpenAI Provider (Fallback)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """OpenAI'yi başlat"""
        try:
            if not self.api_key:
                raise ValueError("OpenAI API anahtarı bulunamadı")
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
            print("✅ OpenAI Provider başarıyla yapılandırıldı")
        except ImportError:
            print("⚠️ OpenAI kütüphanesi yüklü değil. pip install openai")
            self.client = None
        except Exception as e:
            print(f"⚠️ OpenAI Provider başlatılamadı: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """OpenAI kullanılabilir mi?"""
        return self.client is not None
    
    def generate_questions(self, text: str, num_questions: int, question_type: str, difficulty: str) -> Dict[str, Any]:
        """OpenAI ile soru üret"""
        if not self.is_available():
            raise Exception("OpenAI kullanılamıyor")
        
        # OpenAI implementasyonu buraya eklenecek
        # Şimdilik Gemini ile aynı mantık
        raise NotImplementedError("OpenAI provider henüz tam implement edilmedi")
    
    def generate_summary(self, text: str) -> str:
        """OpenAI ile özet üret"""
        if not self.is_available():
            raise Exception("OpenAI kullanılamıyor")
        raise NotImplementedError("OpenAI provider henüz tam implement edilmedi")


class MockProvider(BaseAIProvider):
    """Mock Provider - Offline Test İçin"""
    
    def is_available(self) -> bool:
        """Mock her zaman kullanılabilir"""
        return True
    
    def generate_questions(self, text: str, num_questions: int, question_type: str, difficulty: str) -> Dict[str, Any]:
        """Mock sorular üret"""
        print("⚠️ Mock Provider kullanılıyor - Gerçek AI servisi çalışmıyor")
        
        # Basit mock sorular
        mock_questions = []
        for i in range(min(num_questions, 3)):  # Max 3 soru
            mock_questions.append({
                "question": f"Mock Soru {i+1}: Bu metnin ana konusu nedir?",
                "options": {
                    "A": "Konu A",
                    "B": "Konu B",
                    "C": "Konu C",
                    "D": "Konu D"
                },
                "correct_answer": "A"
            })
        
        return {
            "questions": mock_questions,
            "recommendations": [],
            "feedback": "Mock modunda çalışıyor. Gerçek AI servisi kullanılamıyor.",
            "provider": "mock"
        }
    
    def generate_summary(self, text: str) -> str:
        """Mock özet üret"""
        print("⚠️ Mock Provider kullanılıyor - Gerçek AI servisi çalışmıyor")
        return f"Mock Özet: Bu metin {len(text)} karakter uzunluğunda. Gerçek AI servisi şu anda kullanılamıyor."


class AIProviderManager:
    """AI Provider Yöneticisi - Fallback Mekanizması"""
    
    def __init__(self):
        self.providers: List[BaseAIProvider] = []
        self.current_provider: Optional[BaseAIProvider] = None
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Tüm provider'ları başlat ve öncelik sırasına göre ekle"""
        # Öncelik sırası: Gemini -> Mock
        # OpenAI şu anda implement edilmedi, sadece Gemini ve Mock kullanıyoruz
        self.providers = [
            GeminiProvider(),
            MockProvider()  # Son çare - her zaman çalışır
        ]
        
        # İlk kullanılabilir provider'ı seç
        for provider in self.providers:
            if provider.is_available():
                self.current_provider = provider
                print(f"✅ Aktif Provider: {provider.__class__.__name__}")
                break
        
        if not self.current_provider:
            print("❌ Hiçbir provider kullanılamıyor!")
    
    def get_provider(self) -> Optional[BaseAIProvider]:
        """Mevcut provider'ı döndür"""
        return self.current_provider
    
    def switch_provider(self):
        """Bir sonraki provider'a geç (failover)"""
        if not self.current_provider:
            return False
        
        current_index = self.providers.index(self.current_provider)
        next_index = current_index + 1
        
        if next_index < len(self.providers):
            next_provider = self.providers[next_index]
            if next_provider.is_available():
                print(f"🔄 Provider değiştiriliyor: {self.current_provider.__class__.__name__} -> {next_provider.__class__.__name__}")
                self.current_provider = next_provider
                return True
        
        return False
    
    def generate_questions_with_fallback(self, text: str, num_questions: int, question_type: str, difficulty: str) -> Dict[str, Any]:
        """Fallback mekanizması ile soru üret"""
        if not self.current_provider:
            raise Exception("Hiçbir AI provider kullanılamıyor")
        
        # İlk provider ile dene
        try:
            return self.current_provider.generate_questions(text, num_questions, question_type, difficulty)
        except Exception as e:
            print(f"❌ {self.current_provider.__class__.__name__} hatası: {e}")
            
            # Fallback: Bir sonraki provider'a geç
            if self.switch_provider():
                try:
                    return self.current_provider.generate_questions(text, num_questions, question_type, difficulty)
                except Exception as e2:
                    print(f"❌ Fallback provider da hatası: {e2}")
                    raise Exception(f"Tüm provider'lar başarısız. Son hata: {e2}")
            else:
                raise Exception(f"Fallback mümkün değil. Hata: {e}")
    
    def generate_summary_with_fallback(self, text: str) -> str:
        """Fallback mekanizması ile özet üret"""
        if not self.current_provider:
            raise Exception("Hiçbir AI provider kullanılamıyor")
        
        try:
            return self.current_provider.generate_summary(text)
        except Exception as e:
            print(f"❌ {self.current_provider.__class__.__name__} hatası: {e}")
            
            if self.switch_provider():
                try:
                    return self.current_provider.generate_summary(text)
                except Exception as e2:
                    print(f"❌ Fallback provider da hatası: {e2}")
                    raise Exception(f"Tüm provider'lar başarısız. Son hata: {e2}")
            else:
                raise Exception(f"Fallback mümkün değil. Hata: {e}")


# Global AI Provider Manager instance
_ai_provider_manager: Optional[AIProviderManager] = None


def get_ai_provider_manager() -> AIProviderManager:
    """AI Provider Manager'ı al veya oluştur"""
    global _ai_provider_manager
    if _ai_provider_manager is None:
        _ai_provider_manager = AIProviderManager()
    return _ai_provider_manager

