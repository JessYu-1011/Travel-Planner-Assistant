# src/gemini_service.py
import google.generativeai as genai
import json
from .base_service import BaseLLMService
from src.tools import *

class GeminiService(BaseLLMService):
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        
        # 1. 註冊所有工具 (這是關鍵，沒註冊 AI 就無法使用)
        self.tools = [
            search_flights, 
            search_activity_tickets,
            search_flight_average_cost,
            search_internet,
            search_internet_average_cost
        ]
        
        # 2. 初始化模型
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash', 
            tools=self.tools
        )
        
        # 3. 開啟自動工具呼叫 (Automatic Function Calling)
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)

    def generate_trip(self, user_prompt: str, enable_flights: bool = True) -> str:
        """
        產生行程 (介面需與 BaseLLMService 一致)
        """
        # 根據開關決定 Prompt
        flight_instr = "請呼叫 `get_skyscanner_lowest_price` 查價，並用 `search_flights` 產連結。" if enable_flights else "使用者不查機票，忽略 flight 欄位 (填 null)。"
        
        full_prompt = f"""
        你是一個專業旅遊規劃師。
        
        【執行指令】
        1. **做功課**：遇到不確定的景點資訊或天氣，請務必呼叫 `search_internet`。
        2. **票券**：付費景點請呼叫 `search_activity_tickets` (Klook/KKday) 進行比價。
        3. **機票**：{flight_instr}
        4. **預算**：請根據查到的資訊估算總花費，並填寫 `budget_analysis` 欄位。
        
        【輸出格式】
        請 **只輸出純 JSON 字串**，不要包含 Markdown 標記 (如 ```json)。
        JSON 結構範例：
        {{
            "trip_name": "...",
            "budget_analysis": "預算充足...",
            "flight": {{ "price": 15000, "link": "..." }},
            "daily_itinerary": [...],
            "activities": [...]
        }}
        """
        
        try:
            # 發送訊息 (SDK 會自動處理工具呼叫的來回溝通)
            response = self.chat.send_message(f"{full_prompt}\n\n使用者需求: {user_prompt}")
            return response.text
            
        except Exception as e:
            # 捕捉 API 錯誤 (例如 API Key 無效或 Quota Exceeded)
            error_msg = str(e)
            print(f"❌ [Gemini Error] {error_msg}")
            
            # 回傳一個假 JSON 讓 UI 顯示錯誤，而不是直接 Crash
            return json.dumps({
                "trip_name": "規劃失敗 (Gemini)",
                "daily_itinerary": [],
                "activities": [],
                "budget_analysis": f"Gemini API 呼叫發生錯誤：{error_msg}。請檢查 API Key 或網路連線。"
            }, ensure_ascii=False)