def get_tool_lists() -> list:
    return list([
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
        ])