from fpdf import FPDF
import os
import logging

# 2. 強制關閉 fontTools 的 INFO 訊息
# 這樣它就不會一直洗版 "subsetting not needed" 了
logging.getLogger("fontTools.subset").setLevel(logging.WARNING)
font_path = "fonts/NotoSansTC-Black.ttf"

class PDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        # 使用內建字型顯示頁碼，避免中文 footer 出錯
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

def convert_json_to_pdf(trip_data):
    """
    使用 fpdf2 將行程 JSON 轉為 PDF (修復版)
    """
    pdf = PDF()
    pdf.add_page()
    
    # --- 1. 字型載入與檢查 ---
    use_unicode = False
    
    if os.path.exists(font_path):
        # 檢查檔案大小，Variable Font 通常很大 (>8MB)，容易導致 fpdf2 崩潰
        file_size_mb = os.path.getsize(font_path) / (1024 * 1024)
        if file_size_mb > 10:
            print(f"⚠️ 警告：字型檔過大 ({file_size_mb:.1f}MB)，可能是 Variable Font，建議改用 Static 版 (Regular.ttf)。")

        try:
            pdf.add_font("NotoSans", style="", fname=font_path)
            pdf.set_font("NotoSans", size=12)
            use_unicode = True
        except Exception as e:
            print(f"❌ 字型載入失敗: {e}，將使用預設英文字型。")
            pdf.set_font("helvetica", size=12)
    else:
        print(f"❌ 找不到 {font_path}，將使用預設英文字型。")
        pdf.set_font("helvetica", size=12)

    # --- 2. 寫入標題 ---
    trip_name = trip_data.get('trip_name', '旅遊行程表')
    pdf.set_font_size(24)
    # 使用 epw (Effective Page Width) 確保不超出邊界
    pdf.cell(pdf.epw, 20, trip_name, new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(5)

    # --- 3. 寫入機票 ---
    flight = trip_data.get('flight')
    if flight:
        pdf.set_font_size(16)
        pdf.set_fill_color(255, 235, 205) # 淺橘色背景
        pdf.cell(pdf.epw, 10, "✈️ 航班資訊", new_x="LMARGIN", new_y="NEXT", fill=True)
        
        pdf.set_font_size(12)
        airline = flight.get('airline') or "未定"
        price = flight.get('price') or "未定"
        
        # 強制重置 X 軸，避免跑版
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(pdf.epw, 8, f"航空公司: {airline}\n參考價格: {price}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

    # --- 4. 寫入每日行程 ---
    itinerary = trip_data.get('daily_itinerary', [])
    for day in itinerary:
        day_num = day.get('day', '?')
        theme = day.get('theme', '行程')
        
        # Day Header
        pdf.set_font_size(14)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(pdf.epw, 10, f"📅 Day {day_num}: {theme}", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_text_color(0, 0, 0)
        
        for spot in day.get('attractions', []):
            time = spot.get('time', '')
            name = spot.get('name', '')
            desc = spot.get('description', '')
            
            # 景點標題
            pdf.set_font_size(11)
            # 強制重置 X
            pdf.set_x(pdf.l_margin)
            pdf.cell(pdf.epw, 8, f"[{time}] {name}", new_x="LMARGIN", new_y="NEXT")
            
            # 景點描述 (最容易報錯的地方)
            if desc:
                pdf.set_font_size(10)
                pdf.set_text_color(80, 80, 80)
                # 縮排效果：透過 set_x 移動起始點，但寬度要扣掉縮排量
                indent = 10
                pdf.set_x(pdf.l_margin + indent)
                effective_width = pdf.epw - indent
                
                try:
                    pdf.multi_cell(effective_width, 6, desc, new_x="LMARGIN", new_y="NEXT")
                except Exception as e:
                    print(f"⚠️ 描述渲染失敗: {e}")
                    # 如果渲染失敗，嘗試用簡單模式印出（避免崩潰）
                    pdf.set_x(pdf.l_margin)
                    pdf.cell(pdf.epw, 6, "(描述內容無法顯示)", new_x="LMARGIN", new_y="NEXT")
                
                pdf.set_text_color(0, 0, 0)
                pdf.ln(2)
        
        pdf.ln(5)

    # --- 5. 寫入票券 ---
    activities = trip_data.get('activities', [])
    if activities:
        pdf.add_page()
        pdf.set_font_size(16)
        pdf.set_fill_color(224, 255, 255)
        pdf.cell(pdf.epw, 10, "🎫 推薦票券 (AI 比價)", new_x="LMARGIN", new_y="NEXT", fill=True)
        pdf.ln(5)
        
        pdf.set_font_size(11)
        for act in activities:
            platform = act.get('platform', 'OTA').upper()
            title = act.get('title') or act.get('name') or '票券'
            price = act.get('price', '查看優惠')
            
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(pdf.epw, 8, f"• [{platform}] {title} - {price}", new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())