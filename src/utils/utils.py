import re

def parse_price(price_str):
    """
    Extract the price number in the structure
    """
    if not price_str or not isinstance(price_str, str):
        return 0
    try:
        clean_str = price_str.replace(',', '')
        # Find the first contiguous set of numbers
        match = re.search(r'\d+', clean_str)
        if match:
            return int(match.group())
        return 0
    except:
        return 0