from ollama import Client
import json
from .base_service import BaseLLMService
from src.tools import search_flights, search_activity_tickets, search_flight_average_cost, search_internet

class OllamaService(BaseLLMService):
    def __init__(self, model_name="llama3:8b", host="http://localhost:11434", auth_token=None):
        """
        初始化 Ollama 服務
        :param model_name: 模型名稱
        :param host: Ollama 伺服器地址
        :param auth_token: 若需要驗證 (如 Cloudflare Tunnel)，請傳入 Bearer Token
        """
        self.model = model_name
        
        # 設定 Headers
        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
            
        # 建立 Client 實例，傳入 host 和 headers
        self.client = Client(host=host, headers=headers)
        
        # 定義工具 (Schema)
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
            {
                "type": "function",
                "function": {
                    "name": "search_flight_average_cost",
                    "description": "搜尋網路上的平均機票價格行情",
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
                    "description": "通用搜尋工具，查詢天氣、景點介紹等",
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
        flight_instr = "請呼叫 search_flights 產連結，並用 search_flight_average_cost 估預算。" if enable_flights else "忽略機票。"
        
        system_prompt = f"""
        You are a professional travel planner.
        
        【Rules】
        1. Use `search_activity_tickets` for paid attractions.
        2. {flight_instr}
        3. If you need info, use `search_internet`.
        4. **IMPORTANT:** Output ONLY valid JSON. No markdown.
        
        Please obey the rules strickly
        【JSON Example】
        {{
            "trip_name": "Trip Title",
            "flight": {{ "airline": "...", "price": "TWD 15000", "link": "..." }},
            "budget_analysis": "...",
            "activities": [ {{ "name": "...", "platform": "klook", "price": "...", "link": "..." }} ],
            "daily_itinerary": [ {{ "day": 1, "theme": "...", "attractions": [ {{ "name": "...", "time": "10:00", "description": "...", "latitude": 25.0, "longitude": 121.0 }} ] }} ]
        }}
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        print(f"🚀 [Remote Ollama] 連線至 {self.client._client.base_url} (Model: {self.model})...")

        try:
            # 第一輪：呼叫模型
            response = self.client.chat(
                model=self.model,
                messages=messages,
                tools=self.tools,
                options={"temperature": 0.1}
            )
        except Exception as e:
            return json.dumps({"trip_name": "連線錯誤", "daily_itinerary": [], "budget_analysis": f"無法連接遠端 Ollama: {e}"}, ensure_ascii=False)

        tool_calls = response['message'].get('tool_calls')

        if tool_calls:
            messages.append(response['message'])

            for tool in tool_calls:
                fn_name = tool.function.name
                fn_args = tool.function.arguments
                print(f"🚀 [Remote Ollama] 呼叫工具: {fn_name}")

                if fn_name == "search_flights":
                    res = search_flights(**fn_args)
                elif fn_name == "search_activity_tickets":
                    res = search_activity_tickets(**fn_args)
                elif fn_name == "search_flight_average_cost":
                    res = search_flight_average_cost(**fn_args)
                elif fn_name == "search_internet":
                    res = search_internet(**fn_args)
                else:
                    res = {"error": "Unknown tool"}

                messages.append({
                    "role": "tool",
                    "content": json.dumps(res, ensure_ascii=False)
                })

            # 第二輪：生成最終 JSON
            final_response = self.client.chat(
                model=self.model,
                messages=messages,
                format="json", 
                options={"temperature": 0.1}
            )
            return final_response['message']['content']
        
        return response['message']['content']