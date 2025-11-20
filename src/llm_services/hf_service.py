# src/hf_service.py
import os
import json
from huggingface_hub import InferenceClient
from .base_service import BaseLLMService
from src.tools import *

class HuggingFaceService(BaseLLMService):
    def __init__(self):
        self.client = InferenceClient(api_key=os.getenv("HF_TOKEN"))
        # 推薦模型：Qwen 2.5 72B (邏輯強) 或 Meta-Llama-3.1-70B
        self.model = "Qwen/Qwen2.5-72B-Instruct"

        # 定義工具 (OpenAI Compatible Format)
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
            }
        ]
        
    def generate_trip(self, user_prompt: str, enable_flights: bool = True) -> str:
        flight_instr = "請呼叫 search_flights 查詢機票。" if enable_flights else "使用者不查機票，忽略 flight 欄位填 null。"
        
        system_prompt = f"""
        你是一個專業旅遊規劃師。
        規則：
        1. 有付費景點請務必呼叫 search_activity_tickets (klook 和 kkday 各一次)。
        2. {flight_instr}
        3. 僅輸出純 JSON。
        
        JSON 範例：
        {{
            "trip_name": "...",
            "flight": {{ "airline": "...", "price": "...", "link": "..." }},
            "activities": [ {{ "name": "...", "platform": "klook", "price": "..." }} ],
            "daily_itinerary": [...]
        }}
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # 1. 第一輪推理 (Thinking)
        response = self.client.chat_completion(
            model=self.model,
            messages=messages,
            tools=self.tools,
            tool_choice="auto",
            max_tokens=4000
        )

        message = response.choices[0].message
        tool_calls = message.tool_calls

        # 2. 工具執行迴圈
        if tool_calls:
            messages.append(message) # 把 AI 說 "我要用工具" 這句話加進歷史
            
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
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": fn_name,
                    "content": json.dumps(res, ensure_ascii=False)
                })

            # 3. 第二輪推理 (Final JSON Generation)
            final_response = self.client.chat_completion(
                model=self.model,
                messages=messages,
                max_tokens=4000
            )
            return final_response.choices[0].message.content
        
        return message.content