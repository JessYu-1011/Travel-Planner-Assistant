import streamlit as st
import json
import re
from dotenv import load_dotenv
from streamlit_folium import st_folium

# 引用自訂模組
from src.llm_services.llm_factory import get_llm_service
from src.map_utils import render_map
from src.templates import render_ticket_card
from src.export.pdf_generator import convert_json_to_pdf
from src.export.markdown_utils import create_itinerary_markdown

def parse_price(price_str):
    """
    從字串中提取數字 (例如: "TWD 12,000" -> 12000)
    如果找不到數字或為 "查看優惠"，回傳 0
    """
    if not price_str or not isinstance(price_str, str):
        return 0
    try:
        # 1. 移除逗號 (1,000 -> 1000)
        clean_str = price_str.replace(',', '')
        # 2. 使用 Regex 抓取第一組連續數字
        match = re.search(r'\d+', clean_str)
        if match:
            return int(match.group())
        return 0
    except:
        return 0

def user_request_prompt(destination, days, origin, start_date, budget, interests):
    return f"""
    我要去 {destination} 玩 {days} 天，從 {origin} 出發，日期 {start_date}。
    總預算約 TWD {budget}。
    興趣：{", ".join(interests)}。

    【你的能力與工具】
    1. **通用搜尋**：如果你不知道某個景點的介紹、交通方式或營業時間，請呼叫 `search_internet` 查詢，不要憑空捏造。
    2. **機票估價**：請呼叫 `search_flight_average_cost` 查行情，再呼叫 `search_flights` 產連結。
    3. **票券比價**：付費景點請呼叫 `search_activity_tickets`。
    
    【執行步驟】
    1. 先上網做功課 (search_internet / search_flight_average_cost)。
    2. 根據查到的資料規劃每日行程。
    3. 進行預算試算 (budget_analysis)，最終輸出預算幣別請用 TWD，如果上面活動金額不是 TWD 請先換算。
    4. 輸出 JSON。
    """

def run_app():
    load_dotenv()

    st.set_page_config(
        page_title="AI 全能旅遊規劃師",
        page_icon="✈️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown("""
    <style>
        .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
        .streamlit-expanderHeader { font-weight: 600; font-size: 1.1em; }
        /* 預算儀表板樣式 */
        .budget-card {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)

    if "trip_result" not in st.session_state:
        st.session_state["trip_result"] = None

    # --- 側邊欄 ---
    with st.sidebar:
        st.title("🌍 旅程設定")
        
        st.subheader("🤖 AI 模型")
        llm_provider = st.selectbox("選擇後端", ["Google Gemini", "Groq (LPU)", "Hugging Face (Open Source)"])
        
        st.divider()

        col_b1, col_b2 = st.columns(2)
        with col_b1: origin = st.text_input("🛫 出發地", "TPE")
        with col_b2: destination = st.text_input("🛬 目的地", "Osaka")
            
        start_date = st.date_input("📅 日期")
        days = st.slider("🗓️ 天數", 1, 10, 5)
        
        # 預算設定
        budget_input = st.number_input("💰 總預算 (TWD)", min_value=10000, value=30000, step=5000)
        
        # 興趣選擇 (混合輸入模式)
        st.write("❤️ 興趣")
        predefined_options = ["歷史古蹟", "在地美食", "動漫巡禮", "自然風景", "購物血拼", "主題樂園"]
        selected_base = st.multiselect("選擇類別", predefined_options, ["在地美食", "購物血拼"], label_visibility="collapsed")
        custom_input = st.text_input("➕ 其他興趣 (手動輸入)", placeholder="例如：攝影, 咖啡廳")
        interests = selected_base + [x.strip() for x in custom_input.split(",") if x.strip()]
        
        st.divider()
        enable_flight_search = st.checkbox("啟用機票比價", value=True)
        submit_btn = st.button("🚀 開始規劃", type="primary")

    # --- 控制邏輯 ---
    if submit_btn:
        if not destination:
            st.warning("請輸入目的地！")
        else:
            try:
                llm_service = get_llm_service(llm_provider)
                with st.spinner(f"AI 正在根據您的 {budget_input} 元預算進行規劃..."):
                    user_request = user_request_prompt(destination, days, origin, start_date, budget_input, interests)
                    raw_response = llm_service.generate_trip(user_request, enable_flights=enable_flight_search)
                    
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

    # --- 結果顯示 ---
    result = st.session_state["trip_result"]

    if result:
        # === 新增：預算計算邏輯 ===
        total_cost = 0
        
        # 1. 機票價格
        flight_price = 0
        if result.get('flight'):
            flight_price = parse_price(result['flight'].get('price', '0'))
            total_cost += flight_price

        # 2. 票券價格
        activities_cost = 0
        for act in result.get('activities', []):
            p = parse_price(act.get('price', '0'))
            activities_cost += p
            total_cost += p

        # 3. 計算剩餘預算
        remaining_budget = budget_input - total_cost
        
        # === 標題與下載 ===
        col_title, col_btn = st.columns([2, 1])
        with col_title:
            st.title(f"✈️ {result.get('trip_name', '專屬旅程')}")
        with col_btn:
            md_text = create_itinerary_markdown(result)
            b1, b2 = st.columns(2)
            with b1:
                st.download_button("📝 Markdown", md_text, "plan.md", "text/markdown")
            with b2:
                try:
                    pdf_bytes = convert_json_to_pdf(result)
                    st.download_button("📄 PDF", pdf_bytes, "plan.pdf", "application/pdf")
                except:
                    st.warning("PDF 失敗")

        # === 新增：預算儀表板顯示 ===
        st.markdown("### 💰 預算預測概覽")
        col_m1, col_m2, col_m3 = st.columns(3)
        
        with col_m1:
            st.metric(
                label="預估總花費 (機票+門票)", 
                value=f"TWD {total_cost:,}",
                delta=f"剩餘 TWD {remaining_budget:,}" if remaining_budget >= 0 else f"超支 TWD {abs(remaining_budget):,}",
                delta_color="normal" if remaining_budget >= 0 else "inverse"
            )
        with col_m2:
            st.metric(label="🛫 機票預算", value=f"TWD {flight_price:,}")
        with col_m3:
            st.metric(label="🎫 門票/活動預算", value=f"TWD {activities_cost:,}")
        
        st.caption("⚠️ 注意：此金額僅計算「機票」與「已知票券」，不含當地餐飲與交通費用。AI 估價僅供參考。")
        st.divider()

        # === 原有機票顯示 ===
        flight = result.get("flight")
        if enable_flight_search and flight:
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 3, 1])
                with c1: st.markdown("### 🛫 航班")
                with c2:
                    st.markdown(f"**{flight.get('airline', 'N/A')}**")
                    st.caption(f"價格: {flight.get('price', 'N/A')}")
                with c3:
                    if flight.get('link'): st.link_button("訂票", flight['link'])

        # === 行程與票券 ===
        col_left, col_right = st.columns([1, 1.2])

        with col_left:
            activities = result.get("activities", [])
            if activities:
                with st.expander("🎫 票券比價 (AI 估價)", expanded=True):
                    for act in activities:
                        platform = act.get('platform', 'other').lower()
                        if 'klook' in platform:
                            badge = "#FF5722"; p_name = "KLOOK"; logo = "https://cdn6.agoda.net/images/mv8/logo/klook_logo_multi_language.png"
                        else:
                            badge = "#26A69A"; p_name = "KKday"; logo = "https://cdn.kkday.com/m-s/static/img/logo/kkday_logo_2.svg"

                        img = act.get('image') or logo
                        title = act.get('title') or act.get('name') or '優惠票券'
                        link = act.get('link') or act.get('ticket_link') or '#'
                        price = act.get('price', '查看優惠')

                        card_html = render_ticket_card(link, img, title, badge, p_name, price)
                        st.markdown(card_html, unsafe_allow_html=True)

            daily_itinerary = result.get("daily_itinerary", [])
            if daily_itinerary:
                st.subheader("📅 每日行程")
                for day in daily_itinerary:
                    with st.expander(f"Day {day.get('day')}: {day.get('theme', '行程')}", expanded=False):
                        for spot in day.get('attractions', []):
                            st.markdown(f"**{spot.get('time')} {spot.get('name')}**")
                            st.caption(spot.get('description'))

        with col_right:
            st.subheader("🗺️ 地圖")
            try:
                map_obj = render_map(result)
                st_folium(map_obj, height=700, width=None)
            except:
                st.error("地圖載入失敗")
    else:
        st.info("👈 請在左側設定您的預算與偏好，開始 AI 規劃！")