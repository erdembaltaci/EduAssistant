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
    
    Bu sınıf, dersin temel etmen kavramlarını gösterir:
    - Algılama (Perception)
    - Akıl Yürütme (Reasoning)
    - Eylem (Action)
    - Öğrenme (Learning)
    """
    
    def __init__(self, agent_id: str = "learning_agent_1"):
        """
        Etmen başlatma - Hafta 2: Etmen Özellikleri
        - Otonomi: Kendi kararlarını verebilir
        - Niyet Odaklı: Hedefleri vardır
        - Sorumluluk: Görevlerini yerine getirir
        """
        self.agent_id = agent_id
        self.state = AgentState.IDLE
        self.knowledge_base = {}  # Hafta 3: Bilgi Temsili
        self.goals = []  # Hafta 2: Hedefler
        self.memory = []  # Hafta 7: Epizodik Bellek (basit)
        
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
        Algılanan veriyi analiz eder ve hedefe göre karar verir.
        """
        self.state = AgentState.REASONING
        
        # Basit akıl yürütme: Metin uzunluğuna göre strateji belirleme
        text_length = len(perceived_data.get("text", ""))
        
        reasoning_result = {
            "strategy": "default",
            "num_questions": 5,
            "difficulty": "orta"
        }
        
        if text_length < 500:
            reasoning_result["strategy"] = "short_text"
            reasoning_result["num_questions"] = 3
            reasoning_result["difficulty"] = "kolay"
        elif text_length > 2000:
            reasoning_result["strategy"] = "long_text"
            reasoning_result["num_questions"] = 10
            reasoning_result["difficulty"] = "zor"
        
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
        Deneyimlerden öğrenir ve bilgi tabanını günceller.
        """
        self.state = AgentState.LEARNING
        
        # Basit öğrenme: Kullanıcı tercihlerini hatırla
        if "user_feedback" in experience:
            feedback = experience["user_feedback"]
            if "preferred_difficulty" in feedback:
                self.knowledge_base["user_preferences"] = {
                    "difficulty": feedback["preferred_difficulty"]
                }
        
        self.state = AgentState.IDLE
    
    def get_state(self) -> Dict[str, Any]:
        """Etmen durumunu döndürür - Hafta 2: Durum Yönetimi"""
        return {
            "agent_id": self.agent_id,
            "state": self.state.value,
            "goals": self.goals,
            "knowledge_base_keys": list(self.knowledge_base.keys()),
            "memory_count": len(self.memory)
        }


def create_learning_agent() -> LearningAgent:
    """Etmen fabrika fonksiyonu"""
    return LearningAgent()


