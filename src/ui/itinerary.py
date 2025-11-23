import streamlit as st
from src.templates import render_ticket_card

def render_itinerary(result):
    """
    渲染每日行程與票券比價 (通常放在左欄)
    """
    # === 票券比價區 ===
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

    # === 每日行程區 ===
    daily_itinerary = result.get("daily_itinerary", [])
    if daily_itinerary:
        st.subheader("📅 每日行程")
        for day in daily_itinerary:
            day_num = day.get('day', '?')
            theme = day.get('theme', '行程')
            
            with st.expander(f"Day {day_num}: {theme}", expanded=False):
                # 兼容 Gemini 物件格式與其他模型的字串格式
                attractions = day.get('attractions') or day.get('activities', [])

                for idx, spot in enumerate(attractions):
                    if isinstance(spot, dict):
                        time = spot.get('time', '彈性時間')
                        name = spot.get('name', '行程')
                        desc = spot.get('description', '')
                        st.markdown(f"**🕒 {time} - {name}**")
                        if desc: st.caption(desc)
                    elif isinstance(spot, str):
                        st.markdown(f"**📍 行程 {idx+1}:** {spot}")