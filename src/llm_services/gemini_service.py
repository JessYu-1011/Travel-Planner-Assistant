# src/gemini_service.py
import google.generativeai as genai
from src.tools import *

class GeminiService:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        
        # 定義工具包 (Tools)
        # 即使前端關閉機票搜尋，我們還是掛載 search_flights，
        # 但會透過 Prompt 控制模型不要去呼叫它。
        self.tools = [search_flights, search_activity_tickets, search_internet_average_cost,
                    search_flight_average_cost, search_internet_average_cost]
        
        # 初始化模型
        # 建議使用 gemini-1.5-flash，速度快且支援 Function Calling 穩定
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',
            tools=self.tools,
        )
        
        # 開啟自動 Function Calling
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)

    def generate_trip(self, prompt, enable_flights=True):
        """
        生成旅遊行程與訂票資訊。
        
        Args:
            prompt (str): 使用者的旅遊需求 (地點、天數、興趣...)
            enable_flights (bool): 是否啟用機票搜尋。
                                   如果為 False，會指示模型忽略機票。
        """
        
        # 1. 根據開關決定 Prompt 的指令
        if enable_flights:
            flight_instruction = "2. 請務必呼叫 `search_flights` 工具查詢去程機票價格與資訊。"
        else:
            flight_instruction = "2. 使用者選擇**不查詢機票**。請直接忽略機票部分，JSON 輸出中的 `flight` 欄位請填入 `null`。"

        # 2. 組合完整 Prompt
        full_prompt = f"""
        {prompt}
        
        【重要指令 - 請嚴格遵守】
        1. 如果行程中有付費景點，請針對該景點**分別呼叫** `search_activity_tickets` 工具**兩次**：
           - 一次參數 platform='klook'
           - 一次參數 platform='kkday'
           (這是為了進行比價，請務必執行兩次)
           
        {flight_instruction}
        
        3. 請將最終結果整理成 JSON 格式輸出。
        
        【JSON 結構範例】
        {{
            "trip_name": "大阪五天四夜之旅",
            "flight": {{ 
                "airline": "長榮航空", 
                "price": "TWD 12,000", 
                "link": "http://..." 
            }}, 
            "activities": [
                {{ 
                    "name": "環球影城", 
                    "platform": "klook", 
                    "ticket_link": "http://...", 
                    "price": "查看優惠" 
                }},
                {{ 
                    "name": "環球影城", 
                    "platform": "kkday", 
                    "ticket_link": "http://...", 
                    "price": "查看優惠" 
                }}
            ],
            "daily_itinerary": [
                {{
                    "day": 1,
                    "theme": "抵達與市區觀光",
                    "attractions": [
                        {{ 
                            "name": "道頓堀", 
                            "time": "18:00", 
                            "latitude": 34.6687, 
                            "longitude": 135.5013, 
                            "description": "熱鬧的美食街..." 
                        }}
                    ]
                }}
            ]
        }}
        """
        
        # 3. 發送訊息給模型
        # Gemini 會自動判斷是否需要呼叫工具 (Function Calling)
        # 如果 enable_flights=False，因為 Prompt 禁止了，它就不會去呼叫 search_flights
        response = self.chat.send_message(full_prompt)
        
        # 回傳生成的文字 (即 JSON String)
        return response.text