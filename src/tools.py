# src/tools.py
from ddgs import DDGS
import urllib.parse
import time
import random
import urllib.parse

def search_internet(query: str):
    """
    使用 DuckDuckGo 搜尋網際網路上的最新資訊。
    當你不知道某個景點的細節、天氣、或是需要最新資訊時使用。
    """
    # 隨機延遲，避免被鎖 IP
    time.sleep(random.uniform(1, 2))
    print(f"🌐 [Tool] 通用搜尋: {query}")
    
    try:
        # 搜尋前 3 筆結果 (region='tw-tzh' 針對台灣繁體優化)
        results = list(DDGS().text(query, region="tw-tzh", max_results=3))
        
        if not results:
            return "抱歉，網路上查無相關資訊。"
            
        # 整理結果給 LLM 看
        summary = f"關於 '{query}' 的搜尋結果：\n"
        for res in results:
            title = res.get('title', '無標題')
            snippet = res.get('body', '無摘要')
            link = res.get('href', '#')
            summary += f"- [{title}]({link}): {snippet}\n"
            
        return summary

    except Exception as e:
        print(f"❌ 搜尋失敗: {e}")
        return f"搜尋工具暫時無法使用: {str(e)}"

# 1. 機票查詢 (改為：智慧連結生成模式)
def search_flights(origin: str, destination: str, departure_date: str):
    """
    產生機票比價連結 (Skyscanner & Google Flights)，不呼叫 API，完全免費。
    Args:
        origin: 出發地 (TPE)
        destination: 目的地 (KIX)
        departure_date: 日期 (YYYY-MM-DD)
    """
    print(f"✈️ [Tool] 生成機票連結: {origin} -> {destination} ({departure_date})")
    
    # --- A. 產生 Skyscanner 連結 ---
    # 格式: https://www.skyscanner.com.tw/transport/flights/tpe/kix/241225
    # 去除日期中的 dash (2024-12-25 -> 241225)
    try:
        y, m, d = departure_date.split('-')
        short_date = f"{y[2:]}{m}{d}" # 變成 250101
    except:
        short_date = "" # 防呆
        
    skyscanner_link = f"https://www.skyscanner.com.tw/transport/flights/{origin.lower()}/{destination.lower()}/{short_date}"

    # --- B. 產生 Google Flights 連結 ---
    # 格式: https://www.google.com/travel/flights?q=Flights%20to%20KIX%20from%20TPE%20on%202024-12-25
    query = f"Flights from {origin} to {destination} on {departure_date}"
    google_link = f"https://www.google.com/travel/flights?q={urllib.parse.quote(query)}"

    # 回傳資料
    # 因為沒有真的查價，我們回傳一個「引導性」的文字
    return {
        "type": "flight",
        "airline": "多個航班比價",
        "price": "點擊查看即時票價", # UI 顯示用
        "link": skyscanner_link,     # 預設給 Skyscanner
        "link_google": google_link   # 備用
    }

# 2. 查詢 Klook/KKday 票券 (加入防鎖機制)
def search_activity_tickets(keyword: str, platform: str = "klook"):
    """
    搜尋票券，並嘗試抓取圖片與正確連結。
    包含 Rate Limit 重試機制。
    """
    # --- 隨機延遲，模擬人類操作 (避免 Ratelimit) ---
    delay = random.uniform(2, 4)
    time.sleep(delay) 
    
    print(f"🎫 [Tool] 搜尋票券: {keyword} ({platform}) - 延遲 {delay:.1f}s")

    # 定義平台資訊
    if platform == "klook":
        site_url = "klook.com"
        search_base = "https://www.klook.com/zh-TW/search?text="
        logo_url = "https://cdn6.agoda.net/images/mv8/logo/klook_logo_multi_language.png"
    else:
        site_url = "kkday.com"
        search_base = "https://www.kkday.com/zh-tw/product/productlist?keyword="
        logo_url = "https://cdn.kkday.com/m-s/static/img/logo/kkday_logo_2.svg"

    # 產生保底連結 (Fallback)
    safe_keyword = urllib.parse.quote(keyword)
    fallback_link = f"{search_base}{safe_keyword}"

    # 預設回傳值
    title = f"{keyword} - {platform.upper()} 優惠"
    link = fallback_link
    image = logo_url
    price = "查看優惠"

    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            # ⚠️ 修改重點：在初始化時不使用 Context Manager (with DDGS() as ddgs)，改用直接呼叫
            # 這樣有時候能避開某些 Session 鎖死的問題
            
            ddgs = DDGS()
            
            # A. 搜尋文字
            query = f"site:{site_url} {keyword} 票"
            
            # 嘗試抓取結果
            # backend="api" 通常比預設的 "lite" 或 "html" 更穩定，但也更容易被擋
            # 如果這裡報錯，它會自動跳到 except 並觸發重試
            text_results = list(ddgs.text(query, region="wt-wt", max_results=1))
            
            if text_results:
                top = text_results[0]
                title = top.get('title', title)
                # 確保連結長度足夠，避免抓到怪怪的短連結
                if len(top.get('href', '')) > 15: 
                    link = top.get('href')

            # B. 搜尋圖片 (這是最容易報錯的地方，我們把它獨立包起來)
            try:
                time.sleep(random.uniform(1, 2)) # 稍微休息
                img_query = f"{keyword} scenery {site_url}"
                img_results = list(ddgs.images(img_query, max_results=1))
                if img_results:
                    image = img_results[0].get('image', logo_url)
            except Exception as img_e:
                print(f"⚠️ [DDG Image Error] 圖片搜尋失敗 (不影響主流程): {img_e}")
                # 圖片失敗沒關係，我們繼續用 Logo

            # 如果成功執行到這裡，就跳出重試迴圈
            break 

        except Exception as e:
            print(f"⚠️ [DDG Warning] 嘗試 {attempt+1}/{max_retries+1} 失敗: {e}")
            
            # 如果是 SSL 協定錯誤 (0x304)，通常重試也沒用，直接跳出
            if "0x304" in str(e) or "Protocol" in str(e):
                print("❌ [Fatal] SSL 協定不支援，停止重試，使用 Fallback 連結。")
                break
                
            if "Ratelimit" in str(e) and attempt < max_retries:
                wait_time = 3 * (attempt + 1)
                print(f"⏳ 觸發頻率限制，冷卻 {wait_time} 秒後重試...")
                time.sleep(wait_time)
            else:
                break

    return {
        "type": "ticket",
        "platform": platform,
        "title": title,
        "link": link,
        "image": image,
        "price": price
    }

# --- 工具 3: 搜尋網路上的平均旅遊花費 (爬蟲) ---
def search_internet_average_cost(destination: str, days: int):
    """
    搜尋網路上 (PTT/Dcard/Blog) 關於該地點的平均旅遊花費。
    Args:
        destination: 地點 (如 大阪)
        days: 天數 (如 5)
    Returns:
        str: 搜尋到的相關摘要文字，讓 LLM 去分析金額。
    """
    print(f"🔍 [Tool] 正在搜尋 '{destination}' {days} 天的網路預算討論...")
    
    # 搜尋關鍵字優化
    query = f"{destination} {days}天 自由行 花費 ptt dcard 2024 2025"
    
    try:
        results = list(DDGS().text(query, region="tw-tzh", max_results=3))
        
        if not results:
            return "查無相關預算討論資料。"
            
        # 組合摘要給 LLM 看
        summary = "網路搜尋結果：\n"
        for res in results:
            summary += f"- {res['title']}: {res['body']}\n"
            
        return summary

    except Exception as e:
        print(f"❌ 預算搜尋失敗: {e}")
        return "預算搜尋工具暫時無法使用。"

def search_flight_average_cost(origin: str, destination: str):
    """
    搜尋網路上關於該航線的平均機票價格行情 (爬蟲 PTT/Dcard/Blog)。
    用來代替即時查價 API，進行預算估算。
    Args:
        origin: 出發地 (如 台北/TPE)
        destination: 目的地 (如 大阪/KIX)
    """
    # 隨機延遲，模擬人類
    time.sleep(random.uniform(2, 5))
    
    # 關鍵字優化：加入年份確保資料夠新
    query = f"{origin} 到 {destination} 機票價格 ptt dcard 2024 2025 便宜"
    print(f"✈️ [Tool] 搜尋機票行情: {query}")
    
    try:
        # 搜尋前 5 筆結果
        results = list(DDGS().text(query, region="tw-tzh", max_results=5))
        
        if not results:
            return "查無相關機票價格討論。"
            
        # 組合摘要給 LLM 看
        summary = f"關於 {origin} 飛 {destination} 的機票價格搜尋結果：\n"
        for res in results:
            title = res.get('title', '')
            body = res.get('body', '')
            summary += f"- {title}: {body}\n"
            
        return summary

    except Exception as e:
        print(f"❌ 機票行情搜尋失敗: {e}")
        return "機票行情工具暫時無法使用。"