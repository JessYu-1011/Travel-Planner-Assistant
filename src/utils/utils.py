import re

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