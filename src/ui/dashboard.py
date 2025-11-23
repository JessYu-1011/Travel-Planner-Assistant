import streamlit as st
from src.utils.utils import parse_price

def render_budget_dashboard(result, user_budget):
    """
    渲染預算儀表板與 AI 分析文字
    """
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
    remaining_budget = user_budget - total_cost

    # === 顯示 Metrics ===
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

    # === 顯示 AI 分析 ===
    analysis_text = result.get("budget_analysis")
    if analysis_text:
        if "不足" in analysis_text or "警告" in analysis_text or "超支" in analysis_text:
            st.error(f"🤖 **AI 預算分析警告：**\n\n{analysis_text}")
        else:
            st.info(f"🤖 **AI 預算分析建議：**\n\n{analysis_text}")
            
    st.caption("⚠️ 注意：此金額僅計算「機票」與「已知票券」，不含當地餐飲與交通費用。AI 估價僅供參考。")
    st.divider()