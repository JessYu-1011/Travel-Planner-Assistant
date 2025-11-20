# src/groq_service.py
import os
import json
from groq import Groq
from src.tools import *

class GroqService:
    def __init__(self):
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY"),
        )
        # 建議使用最新的 Llama 3.3 70B，邏輯最強
        self.model = "llama-3.3-70b-versatile" 

        # 定義工具 (OpenAI 格式 Schema)
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_flights",
                    "description": "產生機票比價連結 (Skyscanner/Google Flights)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "origin": {"type": "string", "description": "出發地 (TPE)"},
                            "destination": {"type": "string", "description": "目的地 (KIX)"},
                            "departure_date": {"type": "string", "description": "YYYY-MM-DD"}
                        },
                        "required": ["origin", "destination", "departure_date"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_activity_tickets",
                    "description": "搜尋景點門票 (Klook/KKday)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "keyword": {"type": "string"},
                            "platform": {"type": "string", "enum": ["klook", "kkday"]}
                        },
                        "required": ["keyword", "platform"]
                    }
                }
            },
            # === 新增工具註冊：搜尋機票行情 ===
            {
                "type": "function",
                "function": {
                    "name": "search_flight_average_cost",
                    "description": "搜尋網路上關於該航線的平均機票價格行情 (PTT/Dcard/Blog)，用於預算估算。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "origin": {"type": "string", "description": "出發地"},
                            "destination": {"type": "string", "description": "目的地"}
                        },
                        "required": ["origin", "destination"]
                    }
                }
            }, 
            {
                "type": "function",
                "function": {
                    "name": "search_internet",
                    "description": "搜尋網際網路以獲取未知或即時的資訊 (例如天氣、最新新聞、景點介紹)。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string", 
                                "description": "搜尋關鍵字 (例如: 大阪環球影城 營業時間)"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
    
    def generate_trip(self, user_prompt, enable_flights=True):
        """
        執行對話並處理工具呼叫 (Tool Calling Loop)
        """
        
        # 1. 構建系統提示詞 (System Prompt)
        flight_instruction = "請呼叫 search_flights 查詢機票。" if enable_flights else "使用者不查機票，請忽略 flight 欄位填 null。"
        
        system_prompt = f"""
        你是一個專業旅遊規劃師。請根據用戶需求規劃行程。
        【重要規則】
        1. 若有付費景點，請務必呼叫 search_activity_tickets 兩次 (klook 和 kkday 各一次) 進行比價。
        2. {flight_instruction}
        3. 最終輸出 **必須** 是純 JSON 格式，不要包含 markdown ```json 標記。
        
        JSON 結構範例：
        {{
            "trip_name": "...",
            "flight": {{ "airline": "...", "price": "...", "link": "..." }},
            "activities": [ {{ "name": "...", "platform": "klook", "link": "...", "image": "...", "price": "..." }} ],
            "daily_itinerary": [ {{ "day": 1, "theme": "...", "attractions": [ {{ "name": "...", "latitude": 25.0, "longitude": 121.0, "description": "..." }} ] }} ]
        }}
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # 2. 第一輪呼叫：看 AI 是否想用工具
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
            tool_choice="auto",
            temperature=0.2, # 降低隨機性，讓 JSON 格式更穩
            max_tokens=4096
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # 3. 如果 AI 決定要呼叫工具
        if tool_calls:
            # 把 AI 的「我想呼叫工具」這個念頭加入對話歷史
            messages.append(response_message)

            # 執行所有被要求的工具
            for tool_call in tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)
                
                # 3. 加入執行邏輯
                if fn_name == "search_flights":
                    res = search_flights(**fn_args)
                elif fn_name == "search_activity_tickets":
                    res = search_activity_tickets(**fn_args)
                elif fn_name == "search_flight_average_cost":
                    res = search_flight_average_cost(**fn_args)
                elif fn_name == "search_internet":  # <--- 新增這個判斷
                    res = search_internet(**fn_args)
                else:
                    res = {"error": "Unknown tool"}

                # 將工具執行結果 (JSON string) 加回對話歷史
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": fn_name,
                    "content": json.dumps(res, ensure_ascii=False)
                })

            # 4. 第二輪呼叫：把工具結果給 AI，請它生成最終 JSON
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2
            )
            return final_response.choices[0].message.content
        
        else:
            # 如果 AI 沒用工具，直接回傳結果
            return response_message.content