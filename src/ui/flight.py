import streamlit as st

def render_flight_info(result, enable_flight_search):
    """
    渲染航班資訊卡片
    """
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