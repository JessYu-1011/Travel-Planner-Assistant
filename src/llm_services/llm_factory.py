import os
from .gemini_service import GeminiService
from .groq_service import GroqService
from .hf_service import HuggingFaceService
from .ollama_service import OllamaService

def get_llm_service(provider: str):
    if provider == "Google Gemini":
        api_key = os.getenv("GOOGLE_API_KEY")
        return GeminiService(api_key)
        
    elif provider == "Groq (LPU)":
        return GroqService()
        
    elif provider == "Hugging Face (Open Source)":
        return HuggingFaceService()

    elif "Local Ollama" in provider:
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        model_name = "qwen2.5:14b" # 或 llama3.1
        return OllamaService(model_name=model_name, host=ollama_host)

    elif "Remote Ollama" in provider:
        host = os.getenv("REMOTE_OLLAMA_HOST")
        token = os.getenv("REMOTE_OLLAMA_TOKEN")
        model = os.getenv("REMOTE_OLLAMA_MODEL", "llama3:8b")
        
        if not host or not token:
            raise ValueError("請在 .env 設定 REMOTE_OLLAMA_HOST 和 REMOTE_OLLAMA_TOKEN")
            
        return OllamaService(model_name=model, host=host, auth_token=token)
        
    else:
        raise ValueError("未知的 LLM 提供者")