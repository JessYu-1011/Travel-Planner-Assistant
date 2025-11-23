from ollama import Client
import json
from .base_service import BaseLLMService
from src.tools.tools import search_flights, search_activity_tickets, search_flight_average_cost, search_internet
from src.tools.prompt import *
from src.tools.tools_list import get_tool_lists

class OllamaService(BaseLLMService):
    def __init__(self, model_name="llama3:8b", host="http://localhost:11434", auth_token=None):
        """
        Init the instance for calling ollama
        :param model_name
        :param host
        :param auth_token: access token(if needed)
        """
        self.model = model_name
        
        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
            
        # The address of the ollama server
        self.client = Client(host=host, headers=headers)
        
        self.tools = get_tool_lists()

    def generate_trip(self, user_prompt: str, enable_flights: bool = True) -> str:
        system_prompt=get_system_prompt(enable_flights)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        print(f"🚀 [Remote Ollama] 連線至 {self.client._client.base_url} (Model: {self.model})...")

        try:
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

            final_response = self.client.chat(
                model=self.model,
                messages=messages,
                format="json", 
                options={"temperature": 0.1}
            )
            return final_response['message']['content']
        
        return response['message']['content']