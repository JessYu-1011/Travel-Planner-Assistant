import streamlit as st
import os

def render_sidebar():
    """
    渲染側邊欄，並回傳使用者的輸入資料 (Dict)
    """
    with st.sidebar:
        st.title("🌍 旅程設定")

        st.subheader("🤖 AI 模型")
        llm_provider = st.selectbox("選擇後端", 
            ["Google Gemini", "Groq (LPU)", "Hugging Face (Open Source)", 
            "Local Ollama (Llama 3.1)","Remote Ollama (Cloudflare Tunnel)"])
        
        # API Key 檢查邏輯
        if llm_provider == "Google Gemini" and not (st.secrets['GOOGLE_API_KEY'] or os.getenv("GOOGLE_API_KEY")):
            st.error("❌ 缺少 GOOGLE_API_KEY")
        elif llm_provider == "Groq (LPU)" and not (st.secrets['GROQ_API_KEY'] or os.getenv("GROQ_API_KEY")):
            st.error("❌ 缺少 GROQ_API_KEY")
        elif llm_provider == "Hugging Face (Open Source)" and not (st.secrets['HF_TOKEN'] or os.getenv("HF_TOKEN")):
            st.error("❌ 缺少 HF_TOKEN")
        elif llm_provider == "Local Ollama (Llama 3.1)":
            st.info("💡 請確保終端機已執行 `ollama serve`")
        elif llm_provider == "Remote Ollama (Cloudflare Tunnel)":
            if not (st.secrets['REMOTE_OLLAMA_HOST'] or os.getenv("REMOTE_OLLAMA_HOST")):
                st.error("❌ 缺少 REMOTE_OLLAMA 設定")
            else:
                st.success("✅ 已設定遠端連線資訊")
        
        st.divider()

        col_b1, col_b2 = st.columns(2)
        with col_b1: origin = st.text_input("🛫 出發地", "台北")
        with col_b2: destination = st.text_input("🛬 目的地", "大阪")
            
        start_date = st.date_input("📅 日期")
        days = st.slider("🗓️ 天數", 1, 30, 5)
        
        # Budget
        budget_input = st.number_input("💰 總預算 (TWD)", min_value=10000, value=30000, step=5000)
        
        # Interests
        st.write("❤️ 興趣")
        predefined_options = ["歷史古蹟", "在地美食", "動漫巡禮", "自然風景", "購物血拼", "主題樂園"]
        selected_base = st.multiselect("選擇類別", predefined_options, ["在地美食", "購物血拼"], label_visibility="collapsed")
        custom_input = st.text_input("➕ 其他興趣 (手動輸入)", placeholder="例如：攝影, 咖啡廳")
        interests = selected_base + [x.strip() for x in custom_input.split(",") if x.strip()]
        
        st.divider()
        enable_flight_search = st.checkbox("啟用機票比價", value=True)
        submit_btn = st.button("🚀 開始規劃", type="primary")

        return {
            "llm_provider": llm_provider,
            "origin": origin,
            "destination": destination,
            "start_date": start_date,
            "days": days,
            "budget": budget_input,
            "interests": interests,
            "enable_flight_search": enable_flight_search,
            "submit": submit_btn
        }