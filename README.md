✈️ AI 智慧旅遊規劃助手 - 系統架構與技術說明
1. 系統架構概觀 (System Architecture)
本專案採用 「微服務導向 (Service-Oriented)」 的模組化架構，將前端介面、業務邏輯、AI 推理與外部工具清楚分離。系統運作流程如下：

前端 (Frontend)：使用者在網頁介面輸入需求（地點、天數、興趣）。

AI 核心 (LLM Core)：Gemini 模型接收需求，分析意圖，判斷是否需要查詢外部資料。

工具層 (Tools Layer)：

若需要機票 -> 呼叫 SerpApi (Google Flights)。

若需要門票/圖片 -> 呼叫 DuckDuckGo Search。

資料整合 (Integration)：AI 將外部數據與行程邏輯整合，生成結構化的 JSON 資料。

渲染層 (Rendering)：前端解析 JSON，動態生成「互動地圖」、「比價卡片」與「行程表」。

2. 專案目錄結構與職責
你的程式碼結構設計符合軟體工程的 Separation of Concerns (關注點分離) 原則：

Plaintext

project_root/
├── .env                  # [設定] 存放 API Key，確保資安 (不需上傳 GitHub)
├── main.py               # [前端] 程式進入點，負責 UI 佈局與狀態管理
├── src/
│   ├── gemini_service.py # [邏輯] 封裝與 Google Gemini 的對話與 Prompt 工程
│   ├── tools.py          # [工具] 實作網路爬蟲與 API 串接 (DDG, SerpApi)
│   └── map_utils.py      # [視覺化] 負責將座標資料轉換為 Folium 地圖物件
└── requirements.txt      # [依賴] 專案所需的 Python 套件清單
3. 關鍵套件與技術選型解析 (Tech Stack)
以下是專案中使用的每一個核心套件及其被選用的理由：

A. 核心框架與介面
streamlit

用途： 快速建構 Web App 前端介面。

選用理由： 對於 Python 開發者最友善，不需要寫 HTML/CSS/JavaScript 就能做出響應式網頁。它內建的 st.session_state 讓狀態管理變得非常簡單。

B. AI 模型與邏輯
google-generativeai

用途： 呼叫 Google Gemini API (使用 gemini-1.5-flash 模型)。

選用理由：

Function Calling (工具呼叫)： 原生支援讓 AI 決定何時呼叫 Python 函式，這是實現 "AI Agent" 的關鍵。

長文本能力： 1.5-flash 擁有百萬級 token window，適合處理大量旅遊資訊。

成本效益： 比起 GPT-4o，Gemini 1.5 Flash 速度快且價格極低（甚至有免費層級）。

C. 外部數據獲取 (Tools)
duckduckgo-search

用途： 搜尋 Klook/KKday 的票券連結、標題，以及抓取景點圖片。

選用理由： 完全免費且不需要 API Key。相比 Google Search API 昂貴且有限制，DuckDuckGo 是學生專案抓取公開資訊的最佳選擇，且支援圖片搜尋。

serpapi (google-search-results)

用途： 專門用於抓取 Google Flights 的機票價格。

選用理由： Google Flights 的網頁結構極其複雜且有反爬蟲機制，直接寫爬蟲幾乎不可能。SerpApi 提供了穩定的 JSON 介面來獲取這些數據。

D. 地圖與視覺化
folium

用途： 基於 Leaflet.js 的 Python 地圖庫，用來繪製底圖、標記點 (Markers) 和路線 (Polylines)。

streamlit-folium

用途： 橋接器。因為 Streamlit 原生不支援 Folium 的互動功能，這個套件讓地圖可以嵌入在 Streamlit 網頁中。

E. 系統與設定
python-dotenv

用途： 讀取 .env 檔案中的環境變數。

選用理由： 資安最佳實踐。避免將 GOOGLE_API_KEY 等敏感資訊直接寫死在程式碼中 (Hard-code)，防止上傳 GitHub 時外洩。