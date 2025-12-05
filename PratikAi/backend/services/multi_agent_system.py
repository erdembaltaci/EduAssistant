"""
Çoklu Etmen Sistemi - Hafta 6: Çoklu Etmen İşbirliği ve Koordinasyon
CWD (Coordinator-Worker-Delegator) Modeli
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from services.learning_agent import LearningAgent


class AgentRole(Enum):
    """Etmen Rolleri - Hafta 6: Rol Tabanlı Tasarım"""
    COORDINATOR = "coordinator"  # Koordinatör
    DELEGATOR = "delegator"  # Delege Eden
    WORKER = "worker"  # Çalışan


class WorkerAgent(LearningAgent):
    """
    Çalışan Etmen - Hafta 6: CWD Modeli
    Belirli görevleri yerine getiren uzman etmen
    """
    
    def __init__(self, agent_id: str, specialization: str):
        """
        Uzman etmen oluşturma - Hafta 6: Uzmanlaşma
        
        Args:
            agent_id: Etmen kimliği
            specialization: Uzmanlık alanı (örn: "question_generator", "summary_generator")
        """
        super().__init__(agent_id)
        self.specialization = specialization
        self.role = AgentRole.WORKER
        self.backstory = self._create_backstory(specialization)
    
    def _create_backstory(self, specialization: str) -> str:
        """Rol ve geçmiş hikayesi oluştur - Hafta 6: Role + Backstory"""
        backstories = {
            "question_generator": "Eğitim içeriğinden kaliteli sorular üretme konusunda uzman. Bloom taksonomisine göre soru hazırlar.",
            "summary_generator": "Metinleri özetleme ve ana fikirleri çıkarma konusunda uzman. Kısa ve öz özetler üretir.",
            "analyzer": "Soruları analiz etme ve pedagojik geri bildirim oluşturma konusunda uzman.",
            "recommender": "Öğrenciler için kaynak önerileri oluşturma konusunda uzman."
        }
        return backstories.get(specialization, "Genel amaçlı çalışan etmen")
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Görev yürütme - Hafta 6: Çalışan Etmen Davranışı
        Uzmanlık alanına göre görevi yerine getirir
        """
        task_type = task.get("type", "")
        
        if self.specialization == "question_generator" and task_type == "generate_questions":
            return self._generate_questions(task)
        elif self.specialization == "summary_generator" and task_type == "generate_summary":
            return self._generate_summary(task)
        elif self.specialization == "analyzer" and task_type == "analyze":
            return self._analyze(task)
        elif self.specialization == "recommender" and task_type == "recommend":
            return self._recommend(task)
        else:
            return {"error": f"Bu görev {self.specialization} uzmanlığına uygun değil"}
    
    def _generate_questions(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Soru üretme görevi"""
        from services.tools import call_tool
        return call_tool("generate_quiz", {
            "text": task.get("text", ""),
            "num_questions": task.get("num_questions", 5),
            "difficulty": task.get("difficulty", "orta")
        }, None)
    
    def _generate_summary(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Özet üretme görevi"""
        from services.tools import call_tool
        return call_tool("generate_summary", {
            "text": task.get("text", "")
        }, None)
    
    def _analyze(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analiz görevi"""
        from services.gemini_service import analyze_question_types
        questions = task.get("questions", [])
        feedback = analyze_question_types(questions)
        return {"feedback": feedback}
    
    def _recommend(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Öneri görevi"""
        from services.tools import call_tool
        return call_tool("analyze_text", {
            "text": task.get("text", "")
        }, None)


class DelegatorAgent(LearningAgent):
    """
    Delege Eden Etmen - Hafta 6: CWD Modeli
    Koordinatör ve çalışanlar arasında aracı
    """
    
    def __init__(self, agent_id: str = "delegator_1"):
        super().__init__(agent_id)
        self.role = AgentRole.DELEGATOR
        self.worker_agents: List[WorkerAgent] = []
    
    def register_worker(self, worker: WorkerAgent):
        """Çalışan etmen kaydet - Hafta 6: İşbirliği"""
        self.worker_agents.append(worker)
    
    def delegate_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Görev delege etme - Hafta 6: Delegasyon
        Görevi uygun çalışana atar
        """
        task_type = task.get("type", "")
        
        # Uygun çalışanı bul - Hafta 6: Koordinasyon
        suitable_worker = None
        for worker in self.worker_agents:
            if worker.specialization == task_type.split("_")[0] + "_generator" or \
               worker.specialization == task_type.split("_")[0]:
                suitable_worker = worker
                break
        
        if not suitable_worker:
            # Genel amaçlı çalışan bul
            suitable_worker = self.worker_agents[0] if self.worker_agents else None
        
        if suitable_worker:
            return suitable_worker.execute_task(task)
        else:
            return {"error": "Uygun çalışan bulunamadı"}
    
    def coordinate_workers(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Çalışanları koordine etme - Hafta 6: Koordinasyon
        Birden fazla görevi paralel veya sıralı olarak dağıtır
        """
        results = []
        for task in tasks:
            result = self.delegate_task(task)
            results.append(result)
        return results


class CoordinatorAgent(LearningAgent):
    """
    Koordinatör Etmen - Hafta 6: CWD Modeli
    Genel süreç yönetimi ve strateji belirleme
    """
    
    def __init__(self, agent_id: str = "coordinator_1"):
        super().__init__(agent_id)
        self.role = AgentRole.COORDINATOR
        self.delegator: Optional[DelegatorAgent] = None
    
    def set_delegator(self, delegator: DelegatorAgent):
        """Delege eden etmeni ayarla - Hafta 6: Hiyerarşik Organizasyon"""
        self.delegator = delegator
    
    def manage_process(self, goal: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Süreç yönetimi - Hafta 6: Koordinasyon
        Genel planı oluşturur ve delegatöre iletir
        """
        # 1. Algılama
        perceived_data = self.perceive(input_data)
        
        # 2. Akıl yürütme
        reasoning_result = self.reason(perceived_data, goal)
        
        # 3. Planlama - Görevleri belirle
        plan = self.plan(goal, reasoning_result)
        
        # 4. Görevleri delegatöre ilet
        if self.delegator:
            tasks = []
            for step in plan:
                task_type = step["task"].replace("_", "")
                tasks.append({
                    "type": task_type,
                    "text": perceived_data.get("text", ""),
                    "parameters": step.get("parameters", {})
                })
            
            # Delegatör görevleri çalışanlara dağıtır
            results = self.delegator.coordinate_workers(tasks)
            
            return {
                "coordinator_state": self.get_state(),
                "plan": plan,
                "results": results
            }
        else:
            return {"error": "Delegator atanmamış"}


class MultiAgentSystem:
    """
    Çoklu Etmen Sistemi - Hafta 6: MAS
    CWD modelini yöneten ana sistem
    """
    
    def __init__(self):
        """Sistemi başlat - Hafta 6: Sistem Kurulumu"""
        self.coordinator = CoordinatorAgent()
        self.delegator = DelegatorAgent()
        
        # Çalışan etmenleri oluştur - Hafta 6: Uzmanlaşma
        self.workers = [
            WorkerAgent("worker_1", "question_generator"),
            WorkerAgent("worker_2", "summary_generator"),
            WorkerAgent("worker_3", "analyzer"),
            WorkerAgent("worker_4", "recommender")
        ]
        
        # Hiyerarşiyi kur - Hafta 6: Hiyerarşik Organizasyon
        self.coordinator.set_delegator(self.delegator)
        for worker in self.workers:
            self.delegator.register_worker(worker)
    
    def process_request(self, goal: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        İstek işleme - Hafta 6: Çoklu Etmen İşbirliği
        Koordinatör üzerinden tüm süreci yönetir
        """
        return self.coordinator.manage_process(goal, input_data)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Sistem bilgisi - Hafta 6: Sistem Durumu"""
        return {
            "coordinator": self.coordinator.get_state(),
            "delegator": self.delegator.get_state(),
            "workers": [w.get_state() for w in self.workers],
            "total_agents": 1 + 1 + len(self.workers)  # Coordinator + Delegator + Workers
        }


# Global sistem instance
_multi_agent_system: Optional[MultiAgentSystem] = None


def get_multi_agent_system() -> MultiAgentSystem:
    """Çoklu etmen sistemini al veya oluştur"""
    global _multi_agent_system
    if _multi_agent_system is None:
        _multi_agent_system = MultiAgentSystem()
    return _multi_agent_system


