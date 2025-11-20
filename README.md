✈️ AI 全能旅遊規劃師 (AI Smart Travel Planner)
這是一個基於 Streamlit 與 大型語言模型 (LLM) 的智慧旅遊規劃 Agent。它不僅能根據你的預算與興趣生成每日行程，還具備聯網搜尋、即時票價比價 (Klook/KKday)、機票行情估算以及互動式地圖功能。

系統採用 工廠模式 (Factory Pattern) 設計，支援無縫切換多種 AI 後端（Google Gemini、Groq LPU、Hugging Face Open Source）。

✨ 功能亮點 (Features)
🤖 多模型支援 (Model Agnostic)：

Google Gemini 1.5 Flash：綜合能力強，支援原生 Function Calling。

Groq (Llama 3)：推論速度極快 (LPU)，適合即時互動。

Hugging Face (Qwen 2.5)：支援開源強大模型。

🎫 智慧票券比價：自動搜尋 Klook 與 KKday 的對應行程，並以精美的圖文卡片呈現價格與連結。

💰 預算控制與估算：

透過爬蟲 (DuckDuckGo) 搜尋網路遊記與機票行情，提供有憑有據的預算分析。

自動計算總花費，若超支會發出警告。

🗺️ 互動式地圖：使用 Folium 自動繪製每日路線圖，視覺化行程動線。

📄 多格式匯出：支援一鍵下載 Markdown 筆記或排版精美的 PDF 行程表（支援繁體中文）。

🌐 聯網能力：具備通用搜尋工具，遇未知景點會自動上網查詢最新資訊（營業時間、天氣等）。

🏗️ 系統架構 (Architecture)
專案採用 微服務導向 (Service-Oriented) 與 UI/Logic 分離 的架構：

Plaintext

Final-Project/
├── main.py               # [Entry] 程式入口，僅負責啟動 UI
├── font.ttf              # [Resource] 繁體中文字型 (必須自行放入)
├── .env                  # [Config] API Key 設定檔
├── requirements.txt      # [Dependency] 套件清單
└── src/
    ├── ui/               # [UI Layer] Streamlit 介面邏輯
    │   └── app.py
    ├── llm_factory.py    # [Factory] 負責產生對應的 LLM Service 實例
    ├── gemini_service.py # [Service] Google Gemini 實作
    ├── groq_service.py   # [Service] Groq 實作
    ├── hf_service.py     # [Service] Hugging Face 實作
    ├── tools.py          # [Tools] 網路爬蟲與 API 工具 (DDG, SerpApi)
    ├── map_utils.py      # [Utils] 地圖繪製邏輯
    ├── pdf_generator.py  # [Utils] PDF 生成邏輯 (fpdf2)
    ├── markdown_utils.py # [Utils] Markdown 生成邏輯
    └── templates.py      # [View] Jinja2 HTML 模板 (卡片渲染)
🚀 安裝與執行 (Installation)
1. Clone 專案
Bash

git clone https://github.com/your-username/ai-travel-planner.git
cd ai-travel-planner
2. 安裝依賴套件
建議使用虛擬環境 (venv)。

Bash

pip install -r requirements.txt
(若無 requirements.txt，請安裝以下套件)：

Bash

pip install streamlit streamlit-folium folium google-generativeai groq huggingface_hub python-dotenv duckduckgo-search fpdf2 jinja2
3. 設定環境變數
請在專案根目錄建立一個 .env 檔案，並填入你的 API Key：

Properties

# .env
# 1. Google Gemini (必填)
GOOGLE_API_KEY=your_google_api_key

# 2. Groq (選填，若要用 Llama 3)
GROQ_API_KEY=your_groq_api_key

# 3. Hugging Face (選填，若要用 Open Source Model)
HF_TOKEN=your_hf_token

# 4. SerpApi (選填，做為 Google 搜尋的備援)
SERPAPI_KEY=your_serpapi_key
4. 準備中文字型 (⚠️ 重要)
為了讓生成的 PDF 能正確顯示中文，請下載 Noto Sans TC (思源黑體) 的 Static 版本。

前往 Google Fonts 下載。

解壓縮後，找到 static/NotoSansTC-Regular.ttf。

將其重新命名為 font.ttf。

放入專案的根目錄中。

5. 啟動程式
Bash

streamlit run main.py
🛠️ 常見問題排除 (Troubleshooting)
Q1: 搜尋時出現 Unsupported protocol version 0x304 錯誤？
A: 這是 macOS 的 SSL 函式庫與 curl_cffi 套件衝突導致。

解法 1 (推薦)：程式已內建 fallback 機制，若 DuckDuckGo 失敗會自動切換至 SerpApi (若有設定)。

解法 2 (治本)：嘗試降級 curl_cffi 版本：

Bash

pip install curl_cffi==0.5.10 duckduckgo_search
Q2: PDF 下載後中文變亂碼或方塊？
A: 請確認根目錄下是否有 font.ttf 檔案，且該檔案必須是支援繁體中文的字型 (如 Noto Sans TC)。不要使用 Variable Font 版本，請使用 Static 版本。

Q3: 票券卡片顯示原始 HTML 碼？
A: 這是 Markdown 縮排問題。本專案已使用 Jinja2 模板引擎並配合 .strip() 解決此問題，請確保你的 src/templates.py 是最新版本。

📚 技術棧 (Tech Stack)
Frontend: Streamlit

Map Visualization: Folium

LLM Integration:

Google Generative AI SDK

Groq SDK

Hugging Face Inference Client

Search Tools: DuckDuckGo Search

PDF Generation: fpdf2

Templating: Jinja2