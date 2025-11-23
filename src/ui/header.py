import streamlit as st
from src.export.pdf_generator import convert_json_to_pdf
from src.export.markdown_utils import create_itinerary_markdown

def render_header(result):
    """
    渲染結果頁面的標題與下載按鈕
    """
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