# src/groq_service.py
import os
import json
from groq import Groq
from src.tools.tools import *
from src.tools.prompt import *
from src.tools.tools_list import get_tool_lists

class GroqService:
    def __init__(self):
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY"),
        )
        self.model = "llama-3.3-70b-versatile" 

        self.tools = get_tool_lists()
        
    def generate_trip(self, user_prompt, enable_flights=True):
        """
        執行對話並處理工具呼叫 (Tool Calling Loop)
        """
        
        # 1. 構建系統提示詞 (System Prompt)
        
        system_prompt = get_system_prompt(enable_flights)

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