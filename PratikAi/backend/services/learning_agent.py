"""
Basit Eğitim Etmeni (Learning Agent) - Hafta 2: Etmen Sistemleri
Bu modül, dersin temel etmen kavramlarını gösterir.
"""

from typing import Dict, List, Any, Optional
from enum import Enum


class AgentState(Enum):
    """Etmen durumları - Hafta 2: Otonomi ve Durum Yönetimi"""
    IDLE = "idle"  # Beklemede
    PERCEIVING = "perceiving"  # Algılıyor
    REASONING = "reasoning"  # Akıl yürütüyor
    ACTING = "acting"  # Eylem alıyor
    LEARNING = "learning"  # Öğreniyor


class LearningAgent:
    """
    Eğitim Etmeni - Hafta 2: Etmen Sistemlerine Giriş
    Chapter 4: Reflection and Introspection özellikleri eklendi
    
    Bu sınıf, dersin temel etmen kavramlarını gösterir:
    - Algılama (Perception)
    - Akıl Yürütme (Reasoning)
    - Eylem (Action)
    - Öğrenme (Learning)
    - Self-Explanation (Chapter 4: Transparency)
    - Meta-Reasoning (Chapter 4: Reflection)
    - Self-Modeling (Chapter 4: Self-Modeling)
    """
    
    def __init__(self, agent_id: str = "learning_agent_1"):
        """
        Etmen başlatma - Hafta 2: Etmen Özellikleri
        Chapter 4: Self-Modeling ile genişletildi
        - Otonomi: Kendi kararlarını verebilir
        - Niyet Odaklı: Hedefleri vardır
        - Sorumluluk: Görevlerini yerine getirir
        """
        self.agent_id = agent_id
        self.state = AgentState.IDLE
        self.knowledge_base = {}  # Hafta 3: Bilgi Temsili
        self.goals = []  # Hafta 2: Hedefler
        self.memory = []  # Hafta 7: Epizodik Bellek (basit)
        
        # Chapter 4: Self-Modeling - Agent'ın kendi modeli
        self.self_model = {
            "goals": {
                "personalized_recommendations": True,
                "optimize_user_satisfaction": True,
                "adaptive_difficulty": True  # Zorluk seviyesini kullanıcıya göre ayarla
            },
            "preference_weights": {
                "text_length": 0.4,      # Metin uzunluğu ağırlığı
                "user_preference": 0.3,   # Kullanıcı tercihi ağırlığı
                "default_strategy": 0.3   # Varsayılan strateji ağırlığı
            },
            "knowledge_base": {
                "user_preferences": {},
                "learning_history": []
            }
        }
        
        # Chapter 4: Meta-Reasoning için feedback geçmişi
        self.feedback_history = []
        
    def perceive(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Algılama (Perception) - Hafta 2: Tepkisellik (Reactivity)
        Çevreden gelen veriyi algılar ve işler.
        """
        self.state = AgentState.PERCEIVING
        
        perceived_data = {
            "text": input_data.get("text", ""),
            "file_type": input_data.get("file_type", None),
            "user_preferences": input_data.get("preferences", {}),
            "timestamp": input_data.get("timestamp", None)
        }
        
        # Bilgi tabanına ekle - Hafta 3: Bilgi Temsili
        self.knowledge_base["last_input"] = perceived_data
        
        self.state = AgentState.IDLE
        return perceived_data
    
    def reason(self, perceived_data: Dict[str, Any], goal: str) -> Dict[str, Any]:
        """
        Akıl Yürütme (Reasoning) - Hafta 3: Akıl Yürütme Mekanizmaları
        Chapter 4: Self-Explanation ile genişletildi
        Algılanan veriyi analiz eder ve hedefe göre karar verir.
        """
        self.state = AgentState.REASONING
        
        # Basit akıl yürütme: Metin uzunluğuna göre strateji belirleme
        text_length = len(perceived_data.get("text", ""))
        user_preferences = perceived_data.get("user_preferences", {})
        
        # Kullanıcı tercihlerini self_model'den al (Chapter 4: Self-Modeling)
        stored_preferences = self.self_model["knowledge_base"].get("user_preferences", {})
        if stored_preferences:
            user_preferences = {**stored_preferences, **user_preferences}
        
        # Ağırlıklı karar verme (Chapter 4: Meta-Reasoning)
        weights = self.self_model["preference_weights"]
        
        reasoning_result = {
            "strategy": "default",
            "num_questions": 5,
            "difficulty": "orta",
            "explanation": ""  # Chapter 4: Self-Explanation
        }
        
        # Metin uzunluğuna göre strateji (ağırlıklı)
        if text_length < 500:
            reasoning_result["strategy"] = "short_text"
            reasoning_result["num_questions"] = 3
            reasoning_result["difficulty"] = "kolay"
            reasoning_result["explanation"] = f"Metin kısa ({text_length} karakter), bu yüzden 3 kolay soru üretiyorum."
        elif text_length > 2000:
            reasoning_result["strategy"] = "long_text"
            reasoning_result["num_questions"] = 10
            reasoning_result["difficulty"] = "zor"
            reasoning_result["explanation"] = f"Metin uzun ({text_length} karakter), bu yüzden 10 zor soru üretiyorum."
        else:
            reasoning_result["explanation"] = f"Metin orta uzunlukta ({text_length} karakter), bu yüzden 5 orta zorlukta soru üretiyorum."
        
        # Kullanıcı tercihlerini uygula (eğer varsa)
        if user_preferences.get("num_questions"):
            reasoning_result["num_questions"] = user_preferences["num_questions"]
            reasoning_result["explanation"] += f" Kullanıcı tercihi: {reasoning_result['num_questions']} soru."
        
        if user_preferences.get("difficulty"):
            reasoning_result["difficulty"] = user_preferences["difficulty"]
            reasoning_result["explanation"] += f" Kullanıcı tercihi: {reasoning_result['difficulty']} zorluk."
        
        # Chapter 4: Self-Explanation - Kararın detaylı açıklaması
        reasoning_result["explanation"] += f" Strateji: {reasoning_result['strategy']} (metin uzunluğu ağırlığı: {weights['text_length']:.1%}, kullanıcı tercihi ağırlığı: {weights['user_preference']:.1%})."
        
        # Bilgi tabanına akıl yürütme sonucunu kaydet
        self.knowledge_base["reasoning_result"] = reasoning_result
        
        self.state = AgentState.IDLE
        return reasoning_result
    
    def plan(self, goal: str, reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Planlama (Planning) - Hafta 5: Planlama Algoritmaları
        Basit HTN (Hierarchical Task Network) benzeri planlama
        """
        plan = []
        
        # Plan adımları
        plan.append({
            "step": 1,
            "task": "metin_analizi",
            "description": "Metni analiz et ve ana konuları belirle"
        })
        
        plan.append({
            "step": 2,
            "task": "soru_uretim",
            "description": f"{reasoning_result['num_questions']} adet soru üret",
            "parameters": {
                "num_questions": reasoning_result["num_questions"],
                "difficulty": reasoning_result["difficulty"]
            }
        })
        
        plan.append({
            "step": 3,
            "task": "analiz",
            "description": "Soruları Bloom taksonomisine göre analiz et"
        })
        
        plan.append({
            "step": 4,
            "task": "tavsiye_olustur",
            "description": "Öğrenci için öneriler oluştur"
        })
        
        return plan
    
    def act(self, plan: List[Dict[str, Any]], external_function) -> Dict[str, Any]:
        """
        Eylem (Action) - Hafta 2: Eylem Alma
        Planı adım adım uygular.
        """
        self.state = AgentState.ACTING
        
        results = {}
        for step in plan:
            task = step["task"]
            
            if task == "soru_uretim":
                # Dış fonksiyonu çağır - Hafta 5: Araç Kullanımı
                params = step.get("parameters", {})
                results[task] = external_function(**params)
            else:
                results[task] = {"status": "completed", "step": step["step"]}
        
        # Epizodik belleğe kaydet - Hafta 7: Epizodik Bellek
        self.memory.append({
            "plan": plan,
            "results": results,
            "timestamp": None  # Gerçek uygulamada datetime kullanılır
        })
        
        self.state = AgentState.IDLE
        return results
    
    def learn(self, experience: Dict[str, Any]) -> None:
        """
        Öğrenme (Learning) - Hafta 3: Öğrenme Mekanizmaları
        Chapter 4: Meta-Reasoning ve Self-Modeling ile genişletildi
        Deneyimlerden öğrenir ve bilgi tabanını günceller.
        """
        self.state = AgentState.LEARNING
        
        # Chapter 4: Meta-Reasoning - Feedback'e göre ağırlıkları güncelle
        if "user_feedback" in experience:
            feedback = experience["user_feedback"]
            self.feedback_history.append(feedback)
            
            # Feedback'i analiz et ve ağırlıkları güncelle
            self._meta_reasoning(feedback)
            
            # Kullanıcı tercihlerini güncelle (Chapter 4: Self-Modeling)
            if "preferred_difficulty" in feedback:
                self.self_model["knowledge_base"]["user_preferences"]["difficulty"] = feedback["preferred_difficulty"]
            if "preferred_num_questions" in feedback:
                self.self_model["knowledge_base"]["user_preferences"]["num_questions"] = feedback["preferred_num_questions"]
            
            # Öğrenme geçmişine ekle
            self.self_model["knowledge_base"]["learning_history"].append({
                "feedback": feedback,
                "timestamp": experience.get("timestamp")
            })
        
        # Basit öğrenme: Kullanıcı tercihlerini hatırla (geriye dönük uyumluluk)
        if "user_feedback" in experience:
            feedback = experience["user_feedback"]
            if "preferred_difficulty" in feedback:
                self.knowledge_base["user_preferences"] = {
                    "difficulty": feedback["preferred_difficulty"]
                }
        
        self.state = AgentState.IDLE
    
    def _meta_reasoning(self, feedback: Dict[str, Any]) -> None:
        """
        Chapter 4: Meta-Reasoning - Feedback'e göre ağırlıkları güncelle
        Feedback pozitifse ilgili ağırlıkları artır, negatifse azalt
        """
        adjustment_factor = 0.1  # Ağırlık değişim oranı
        
        # Feedback tipine göre ağırlıkları güncelle
        if feedback.get("satisfaction") == "positive":
            # Pozitif feedback: Kullanıcı tercihi ağırlığını artır
            self.self_model["preference_weights"]["user_preference"] = min(
                0.7,  # Maksimum %70
                self.self_model["preference_weights"]["user_preference"] + adjustment_factor
            )
            # Metin uzunluğu ağırlığını azalt
            self.self_model["preference_weights"]["text_length"] = max(
                0.1,  # Minimum %10
                self.self_model["preference_weights"]["text_length"] - adjustment_factor * 0.5
            )
        elif feedback.get("satisfaction") == "negative":
            # Negatif feedback: Varsayılan strateji ağırlığını artır
            self.self_model["preference_weights"]["default_strategy"] = min(
                0.5,
                self.self_model["preference_weights"]["default_strategy"] + adjustment_factor
            )
            # Kullanıcı tercihi ağırlığını azalt
            self.self_model["preference_weights"]["user_preference"] = max(
                0.1,
                self.self_model["preference_weights"]["user_preference"] - adjustment_factor
            )
        
        # Ağırlıkları normalize et (toplam 1.0 olmalı)
        total = sum(self.self_model["preference_weights"].values())
        for key in self.self_model["preference_weights"]:
            self.self_model["preference_weights"][key] /= total
    
    def update_goals(self, new_preferences: Dict[str, Any]) -> None:
        """
        Chapter 4: Self-Modeling - Agent'ın hedeflerini güncelle
        Kullanıcı tercihlerine göre agent'ın hedeflerini dinamik olarak değiştir
        """
        if new_preferences.get("prefer_difficult"):
            self.self_model["goals"]["adaptive_difficulty"] = True
            print("Hedef güncellendi: Zorluk seviyesini kullanıcıya göre ayarla")
        
        if new_preferences.get("prefer_personalized"):
            self.self_model["goals"]["personalized_recommendations"] = True
            print("Hedef güncellendi: Kişiselleştirilmiş öneriler öncelikli")
    
    def get_explanation(self) -> str:
        """
        Chapter 4: Self-Explanation - Agent'ın son kararının açıklamasını döndür
        """
        reasoning_result = self.knowledge_base.get("reasoning_result", {})
        return reasoning_result.get("explanation", "Açıklama mevcut değil.")
    
    def get_state(self) -> Dict[str, Any]:
        """Etmen durumunu döndürür - Hafta 2: Durum Yönetimi
        Chapter 4: Self-Modeling bilgileri eklendi"""
        return {
            "agent_id": self.agent_id,
            "state": self.state.value,
            "goals": self.goals,
            "knowledge_base_keys": list(self.knowledge_base.keys()),
            "memory_count": len(self.memory),
            # Chapter 4: Self-Modeling bilgileri
            "self_model": {
                "goals": self.self_model["goals"],
                "preference_weights": self.self_model["preference_weights"],
                "user_preferences": self.self_model["knowledge_base"].get("user_preferences", {})
            },
            "feedback_count": len(self.feedback_history),
            "last_explanation": self.get_explanation()
        }


def create_learning_agent() -> LearningAgent:
    """Etmen fabrika fonksiyonu"""
    return LearningAgent()


