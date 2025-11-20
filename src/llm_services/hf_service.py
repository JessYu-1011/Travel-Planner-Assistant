import os
import json
from huggingface_hub import InferenceClient
from .base_service import BaseLLMService
# 引入工具
from src.tools import search_flights, search_activity_tickets, search_flight_average_cost, search_internet

class HuggingFaceService(BaseLLMService):
    def __init__(self):
        self.client = InferenceClient(api_key=os.getenv("HF_TOKEN"))
        # Qwen-2.5-72B 是目前 HuggingFace 上指令遵循能力最強的開源模型之一
        self.model = "Qwen/Qwen2.5-72B-Instruct"

        # 定義工具
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_flights",
                    "description": "產生機票比價連結",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "origin": {"type": "string"},
                            "destination": {"type": "string"},
                            "departure_date": {"type": "string"}
                        },
                        "required": ["origin", "destination", "departure_date"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_activity_tickets",
                    "description": "搜尋景點門票",
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
            {
                "type": "function",
                "function": {
                    "name": "search_flight_average_cost",
                    "description": "搜尋網路上關於該航線的平均機票價格行情",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "origin": {"type": "string"},
                            "destination": {"type": "string"}
                        },
                        "required": ["origin", "destination"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_internet",
                    "description": "通用搜尋工具，用於查詢景點經緯度、介紹或天氣",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    def generate_trip(self, user_prompt: str, enable_flights: bool = True) -> str:
        flight_instr = "請呼叫 search_flights 產生連結，並呼叫 search_flight_average_cost 估算預算。" if enable_flights else "忽略機票。"
        
        # === 關鍵修改：提供超詳細的 JSON 範例，強迫模型填寫內容 ===
        system_prompt = f"""
        你是一個專業旅遊規劃師。
        
        【執行規則】
        1. 付費景點務必呼叫 `search_activity_tickets`。
        2. {flight_instr}
        3. 如果不知道景點的經緯度，請呼叫 `search_internet` 查詢，**不要憑空捏造**。
        
        【輸出格式要求】
        請直接輸出 JSON 格式，不要包含任何 Markdown 標記（如 ```json）。
        
        【JSON 結構範例 (請嚴格遵守)】
        {{
            "trip_name": "大阪京都五天四夜深度遊",
            "flight": {{ "airline": "長榮航空", "price": "約 TWD 15,000", "link": "..." }},
            "budget_analysis": "預算充足，機票約佔...",
            "activities": [ 
                {{ "name": "環球影城", "platform": "klook", "price": "TWD 2,500", "link": "..." }} 
            ],
            "daily_itinerary": [
                {{
                    "day": 1,
                    "theme": "抵達與道頓堀美食",
                    "attractions": [
                        {{
                            "name": "道頓堀",
                            "time": "18:00",
                            "description": "大阪最熱鬧的美食街，必吃章魚燒。",
                            "latitude": 34.6687,
                            "longitude": 135.5013
                        }},
                        {{
                            "name": "心齋橋",
                            "time": "20:00",
                            "description": "購物天堂，藥妝店林立。",
                            "latitude": 34.6710,
                            "longitude": 135.5010
                        }}
                    ]
                }},
                {{
                    "day": 2,
                    "theme": "環球影城一日遊",
                    "attractions": [
                        {{ "name": "日本環球影城", "time": "09:00", "description": "...", "latitude": 34.6654, "longitude": 135.4323 }}
                    ]
                }}
            ]
        }}
        
        **重要提示：** 1. `daily_itinerary` 陣列**絕對不能為空**。
        2. 請根據使用者的天數，生成對應天數的行程（例如 5 天就要有 5 個 object）。
        3. 每個景點都**必須**包含 `latitude` 和 `longitude` (浮點數)，地圖才能顯示。
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # 第一輪：思考與工具呼叫
        response = self.client.chat_completion(
            model=self.model,
            messages=messages,
            tools=self.tools,
            tool_choice="auto",
            max_tokens=4000,
            temperature=0.2 # 降低隨機性，讓格式更穩
        )

        message = response.choices[0].message
        tool_calls = message.tool_calls

        if tool_calls:
            messages.append(message)
            
            for tool_call in tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)
                print(f"🤗 [HF] 呼叫工具: {fn_name}")

                # 執行對應工具
                if fn_name == "search_flights":
                    res = search_flights(**fn_args)
                elif fn_name == "search_activity_tickets":
                    res = search_activity_tickets(**fn_args)
                elif fn_name == "search_flight_average_cost":
                    res = search_flight_average_cost(**fn_args)
                elif fn_name == "search_internet":
                    res = search_internet(**fn_args) # 記得要引入 search_internet
                else:
                    res = {"error": "Unknown tool"}
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": fn_name,
                    "content": json.dumps(res, ensure_ascii=False)
                })

            # 第二輪：生成最終 JSON
            final_response = self.client.chat_completion(
                model=self.model,
                messages=messages,
                max_tokens=4000,
                temperature=0.2
            )
            return final_response.choices[0].message.content
        
        return message.content