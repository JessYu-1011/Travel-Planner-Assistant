import google.generativeai as genai
import json
from .base_service import BaseLLMService
from src.tools.tools import *
from src.tools.prompt import *

class GeminiService(BaseLLMService):
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        # All tools that can be used
        self.tools = [
            search_flights, 
            search_activity_tickets,
            search_flight_average_cost,
            search_internet,
            search_internet_average_cost
        ]
        
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash', 
            tools=self.tools
        )
        
        # Automatic Function Calling
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)

    def generate_trip(self, user_prompt: str, enable_flights: bool = True) -> str:
        """
        Generate the journey
        """
        full_prompt = get_system_prompt(enable_flights)
        
        try:
            # The SDK will call functions automatically
            response = self.chat.send_message(f"{full_prompt}\n\n使用者需求: {user_prompt}")
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ [Gemini Error] {error_msg}")
            
            # Fake JSON for error case
            return json.dumps({
                "trip_name": "規劃失敗 (Gemini)",
                "daily_itinerary": [],
                "activities": [],
                "budget_analysis": f"Gemini API 呼叫發生錯誤：{error_msg}。請檢查 API Key 或網路連線。"
            }, ensure_ascii=False)