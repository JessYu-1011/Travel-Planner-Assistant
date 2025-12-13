from abc import ABC, abstractmethod

class BaseLLMService(ABC):
    """
    Interface for all llm services.
    """
    
    @abstractmethod
    def generate_trip(self, user_prompt: str, enable_flights: bool = True) -> str:
        """
        :return json structure
        """
        pass