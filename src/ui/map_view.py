import streamlit as st
from streamlit_folium import st_folium
from src.map_utils import render_map

def render_map_view(result):
    """
    渲染地圖 (通常放在右欄)
    """
    st.subheader("🗺️ 地圖")
    try:
        map_obj = render_map(result)
        st_folium(map_obj, height=700, width=None)
    except:
        st.error("地圖載入失敗")