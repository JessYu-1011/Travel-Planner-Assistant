from abc import ABC, abstractmethod

class BaseLLMService(ABC):
    """
    所有 LLM 服務的抽象基底類別 (Interface)
    """
    
    @abstractmethod
    def generate_trip(self, user_prompt: str, enable_flights: bool = True) -> str:
        """
        統一的介面方法。
        回傳值必須是 JSON String。
        """
        pass