import os
import json
from huggingface_hub import InferenceClient
from .base_service import BaseLLMService
from src.tools.tools import search_flights, search_activity_tickets, search_flight_average_cost, search_internet
from src.tools.prompt import *
from src.tools.tools_list import get_tool_lists

class HuggingFaceService(BaseLLMService):
    def __init__(self):
        self.client = InferenceClient(api_key=os.getenv("HF_TOKEN"))
        self.model = "meta-llama/Llama-3.3-70B-Instruct:groq"

        self.tools = get_tool_lists()

    def generate_trip(self, user_prompt: str, enable_flights: bool = True) -> str:        
        system_prompt = get_system_prompt(enable_flights)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.client.chat_completion(
            model=self.model,
            messages=messages,
            tools=self.tools,
            tool_choice="auto",
            max_tokens=4000,
            temperature=0.2
        )

        message = response.choices[0].message
        tool_calls = message.tool_calls

        if tool_calls:
            messages.append(message)
            
            for tool_call in tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)
                print(f"🤗 [HF] 呼叫工具: {fn_name}")

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
                    "tool_call_id": tool_call.id,
                    "name": fn_name,
                    "content": json.dumps(res, ensure_ascii=False)
                })

            final_response = self.client.chat_completion(
                model=self.model,
                messages=messages,
                max_tokens=4000,
                temperature=0.2
            )
            return final_response.choices[0].message.content
        
        return message.content