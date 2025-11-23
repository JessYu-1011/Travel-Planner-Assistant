# System Flow Chart

```mermaid
graph TD
    subgraph User_Interface [Streamlit UI (src/ui/app.py)]
        Start([Start App]) --> Input[User Inputs: Destination, Budget, Interests, etc.]
        Input --> SelectLLM[Select LLM Provider]
        SelectLLM --> ClickStart[Click 'Start Planning']
    end

    subgraph Logic_Layer [Application Logic]
        ClickStart --> Factory[LLM Factory (src/llm_services/llm_factory.py)]
        Factory -->|Instantiate| Service{LLM Service}
        
        Service -->|Gemini| Gemini[Gemini Service]
        Service -->|Groq| Groq[Groq Service]
        Service -->|HuggingFace| HF[Hugging Face Service]
        Service -->|Ollama| Ollama[Ollama Service]
        
        Gemini & Groq & HF & Ollama --> Prompt[Generate User Prompt]
        Prompt --> LLM_Call[Call LLM API]
    end

    subgraph Tools_Layer [Tools (src/tools.py)]
        LLM_Call -.->|Function Call / Tool Use| Tools
        
        Tools --> Search[search_internet (DuckDuckGo)]
        Tools --> FlightCost[search_flight_average_cost (PTT/Dcard)]
        Tools --> FlightLink[search_flights (Link Gen)]
        Tools --> Tickets[search_activity_tickets (Klook/KKday)]
        
        Search & FlightCost & FlightLink & Tickets --> ToolResult[Return Tool Outputs]
        ToolResult --> LLM_Call
    end

    subgraph Output_Layer [Result Processing]
        LLM_Call -->|JSON Response| Parser[Parse JSON Response]
        Parser --> BudgetCalc[Calculate Budget & Remaining]
        
        BudgetCalc --> RenderUI[Render Results]
        RenderUI --> ShowBudget[Budget Dashboard]
        RenderUI --> ShowFlight[Flight Info]
        RenderUI --> ShowCards[Activity Cards (Jinja2)]
        RenderUI --> ShowItinerary[Daily Itinerary]
        RenderUI --> ShowMap[Interactive Map (Folium)]
    end

    subgraph Export_Layer [Export]
        RenderUI --> ExportMD[Export Markdown]
        RenderUI --> ExportPDF[Export PDF (fpdf2)]
    end
```
