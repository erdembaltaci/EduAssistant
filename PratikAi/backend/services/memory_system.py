"""
Bellek Sistemi - Hafta 7: İleri Etmen Tasarım Teknikleri
Kısa Süreli, Uzun Süreli ve Epizodik Bellek
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import deque


class ShortTermMemory:
    """
    Kısa Süreli Bellek - Hafta 7: Çalışma Belleği
    Mevcut oturum için geçici veriler
    """
    
    def __init__(self, max_size: int = 10):
        """
        Kısa süreli bellek başlatma
        
        Args:
            max_size: Maksimum saklanacak öğe sayısı
        """
        self.memory = deque(maxlen=max_size)
        self.session_id: Optional[str] = None
        self.current_context: Dict[str, Any] = {}
    
    def store(self, key: str, value: Any):
        """Belleğe kaydet - Hafta 7: Bellek Depolama"""
        self.memory.append({
            "key": key,
            "value": value,
            "timestamp": datetime.now().isoformat()
        })
        self.current_context[key] = value
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Bellekten al - Hafta 7: Bellek Erişimi"""
        # Önce mevcut bağlamdan kontrol et
        if key in self.current_context:
            return self.current_context[key]
        
        # Sonra bellekten ara
        for item in reversed(self.memory):
            if item["key"] == key:
                return item["value"]
        
        return None
    
    def clear(self):
        """Belleği temizle - Hafta 7: Oturum Sonu"""
        self.memory.clear()
        self.current_context = {}
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Tüm belleği al"""
        return list(self.memory)


class LongTermMemory:
    """
    Uzun Süreli Bellek - Hafta 7: Bilgi Kümesi
    Kalıcı bilgiler (kullanıcı profilleri, öğrenme geçmişi)
    """
    
    def __init__(self):
        """Uzun süreli bellek başlatma"""
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        self.learning_history: Dict[str, List[Dict[str, Any]]] = {}
        self.knowledge_base: Dict[str, Any] = {}
    
    def store_user_profile(self, user_id: str, profile: Dict[str, Any]):
        """Kullanıcı profili kaydet - Hafta 7: Uzun Süreli Depolama"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {}
        self.user_profiles[user_id].update(profile)
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Kullanıcı profili al"""
        return self.user_profiles.get(user_id, {})
    
    def store_learning_history(self, user_id: str, event: Dict[str, Any]):
        """Öğrenme geçmişi kaydet"""
        if user_id not in self.learning_history:
            self.learning_history[user_id] = []
        event["timestamp"] = datetime.now().isoformat()
        self.learning_history[user_id].append(event)
    
    def get_learning_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Öğrenme geçmişi al"""
        history = self.learning_history.get(user_id, [])
        return history[-limit:]  # Son N kayıt
    
    def store_knowledge(self, key: str, value: Any):
        """Genel bilgi kaydet"""
        self.knowledge_base[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_knowledge(self, key: str) -> Optional[Any]:
        """Genel bilgi al"""
        knowledge = self.knowledge_base.get(key)
        return knowledge["value"] if knowledge else None


class EpisodicMemory:
    """
    Epizodik Bellek - Hafta 7: Etkileşim Geçmişi
    Geçmiş olaylar ve sonuçların kaydı
    """
    
    def __init__(self, max_episodes: int = 50):
        """
        Epizodik bellek başlatma
        
        Args:
            max_episodes: Maksimum saklanacak epizot sayısı
        """
        self.episodes = deque(maxlen=max_episodes)
    
    def store_episode(self, episode: Dict[str, Any]):
        """
        Epizot kaydet - Hafta 7: Deneyim Kaydı
        
        Args:
            episode: Epizot verisi (goal, actions, result, feedback)
        """
        episode["timestamp"] = datetime.now().isoformat()
        self.episodes.append(episode)
    
    def retrieve_similar_episodes(self, goal: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Benzer epizotları bul - Hafta 7: Deneyimden Öğrenme
        Geçmişte benzer hedeflerle yapılan işlemleri bulur
        """
        similar = []
        goal_lower = goal.lower()
        
        for episode in reversed(self.episodes):
            episode_goal = episode.get("goal", "").lower()
            if goal_lower in episode_goal or episode_goal in goal_lower:
                similar.append(episode)
                if len(similar) >= limit:
                    break
        
        return similar
    
    def get_all_episodes(self) -> List[Dict[str, Any]]:
        """Tüm epizotları al"""
        return list(self.episodes)


class MemorySystem:
    """
    Bellek Sistemi - Hafta 7: Bellek Mimarisi
    Üç katmanlı bellek sistemini yönetir
    """
    
    def __init__(self):
        """Bellek sistemini başlat"""
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        self.episodic = EpisodicMemory()
    
    def store_context(self, context_type: str, key: str, value: Any):
        """
        Bağlam kaydetme - Hafta 7: Bağlam Yönetimi
        
        Args:
            context_type: "short", "long", "episodic"
            key: Anahtar
            value: Değer
        """
        if context_type == "short":
            self.short_term.store(key, value)
        elif context_type == "long":
            self.long_term.store_knowledge(key, value)
        elif context_type == "episodic":
            self.episodic.store_episode(value)
    
    def retrieve_context(self, context_type: str, key: str) -> Optional[Any]:
        """Bağlam alma"""
        if context_type == "short":
            return self.short_term.retrieve(key)
        elif context_type == "long":
            return self.long_term.get_knowledge(key)
        else:
            return None
    
    def get_global_context(self) -> Dict[str, Any]:
        """
        Küresel Bağlam - Hafta 7: Bağlamsal Farkındalık
        Sistem genelindeki durumu döndürür
        """
        return {
            "short_term_size": len(self.short_term.get_all()),
            "long_term_knowledge_keys": list(self.long_term.knowledge_base.keys()),
            "episodic_count": len(self.episodic.get_all_episodes()),
            "current_session": self.short_term.current_context
        }
    
    def get_session_context(self) -> Dict[str, Any]:
        """
        Oturum Bağlamı - Hafta 7: Oturum Bağlamı
        Mevcut oturumun durumunu döndürür
        """
        return {
            "session_id": self.short_term.session_id,
            "context": self.short_term.current_context,
            "recent_memory": self.short_term.get_all()[-5:]  # Son 5 öğe
        }
    
    def get_task_context(self, task_id: str) -> Dict[str, Any]:
        """
        Görev Bağlamı - Hafta 7: Görev Bağlamı
        Belirli bir göreve ait bağlamı döndürür
        """
        # Epizodik bellekten görevle ilgili epizotları bul
        episodes = [ep for ep in self.episodic.get_all_episodes() 
                   if ep.get("task_id") == task_id]
        
        return {
            "task_id": task_id,
            "episodes": episodes,
            "related_context": self.short_term.retrieve(f"task_{task_id}")
        }
    
    def switch_context(self, new_session_id: str):
        """
        Bağlam Değiştirme - Hafta 7: Context Switching
        Yeni oturuma geçerken eski bağlamı kaydeder
        """
        # Mevcut oturumu epizodik belleğe kaydet
        if self.short_term.session_id:
            self.episodic.store_episode({
                "session_id": self.short_term.session_id,
                "context": self.short_term.current_context.copy(),
                "type": "session_end"
            })
        
        # Yeni oturumu başlat
        self.short_term.clear()
        self.short_term.session_id = new_session_id
    
    def merge_contexts(self, contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Bağlam Birleştirme - Hafta 7: Bağlam Birleştirme
        Birden fazla bağlamı birleştirir
        """
        merged = {}
        for context in contexts:
            merged.update(context)
        return merged


# Global bellek sistemi instance
_memory_system: Optional[MemorySystem] = None


def get_memory_system() -> MemorySystem:
    """Bellek sistemini al veya oluştur"""
    global _memory_system
    if _memory_system is None:
        _memory_system = MemorySystem()
    return _memory_system


