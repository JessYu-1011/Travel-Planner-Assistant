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
        Tool Calling Loop
        """

        system_prompt = get_system_prompt(enable_flights)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]


        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
            tool_choice="auto",
            temperature=0.2, # Lower down the randomness
            max_tokens=4096
        )
        response_message = response.choices[0].messaget
        # Whether LLM wants to use tools
        tool_calls = response_message.tool_calls

        # If it wants to call tools
        if tool_calls:
            # Append the response to chat history
            messages.append(response_message)

            # Execute all tools used
            for tool_call in tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)

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

                # Add the result of tools to the history
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": fn_name,
                    "content": json.dumps(res, ensure_ascii=False)
                })

            # 4. Add the results from tools to the LLM
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2
            )
            return final_response.choices[0].message.content

        # If there are no tool calls, return directly
        else:
            return response_message.content