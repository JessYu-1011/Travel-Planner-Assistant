import streamlit as st
import json
import re
from dotenv import load_dotenv

from src.llm_services.llm_factory import get_llm_service
from src.tools.prompt import get_user_request_prompt
# UI parts
from src.ui.sidebar import render_sidebar
from src.ui.header import render_header
from src.ui.dashboard import render_budget_dashboard
from src.ui.flight import render_flight_info
from src.ui.itinerary import render_itinerary
from src.ui.map_view import render_map_view

def run_app():
    load_dotenv()

    # page setting
    st.set_page_config(
        page_title="AI 全能旅遊規劃師",
        page_icon="✈️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS 
    st.markdown("""
    <style>
        .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
        .streamlit-expanderHeader { font-weight: 600; font-size: 1.1em; }
    </style>
    """, unsafe_allow_html=True)

    if "trip_result" not in st.session_state:
        st.session_state["trip_result"] = None

    # render sidebar
    inputs = render_sidebar()

    # control submission
    if inputs["submit"]:
        if not inputs["destination"]:
            st.warning("請輸入目的地！")
        else:
            try:
                llm_service = get_llm_service(inputs["llm_provider"])
                with st.spinner(f"AI 正在根據您的 {inputs['budget']} 元預算進行規劃..."):
                    user_request = get_user_request_prompt(
                        inputs["destination"], 
                        inputs["days"], 
                        inputs["origin"], 
                        inputs["start_date"], 
                        inputs["budget"], 
                        inputs["interests"]
                    )
                    raw_response = llm_service.generate_trip(
                        user_request, 
                        enable_flights=inputs["enable_flight_search"]
                    )
                    
                    # parse json
                    try:
                        match = re.search(r"\{.*\}", raw_response, re.DOTALL)
                        if match:
                            st.session_state["trip_result"] = json.loads(match.group(0))
                        else:
                            raise ValueError("找不到 JSON")
                    except Exception as e:
                        st.error("JSON 解析失敗")
                        st.text(raw_response)
            except Exception as e:
                st.error(f"錯誤: {e}")

    # render the result
    result = st.session_state["trip_result"]

    if result:
        render_header(result)
        
        render_budget_dashboard(result, inputs["budget"])
        
        render_flight_info(result, inputs["enable_flight_search"])

        # 2 Col layout for itinerary and map
        col_left, col_right = st.columns([1, 1.2])

        with col_left:
            render_itinerary(result)
        
        with col_right:
            render_map_view(result)
            
    else:
        st.info("👈 請在左側設定您的預算與偏好，開始 AI 規劃！")

if __name__ == "__main__":
    run_app()