import os
# 引用所有的 Service
from .gemini_service import GeminiService
from .groq_service import GroqService
from .hf_service import HuggingFaceService

def get_llm_service(provider: str):
    """
    工廠方法：根據 provider 字串回傳對應的 Service 實例
    """
    if provider == "Google Gemini":
        api_key = os.getenv("GOOGLE_API_KEY")
        return GeminiService(api_key) # 假設你原本的 GeminiService 繼承了 Base 並改了方法名
        
    elif provider == "Groq (LPU)":
        return GroqService()
        
    elif provider == "Hugging Face (Open Source)":
        return HuggingFaceService()
        
    else:
        raise ValueError("未知的 LLM 提供者")