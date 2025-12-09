from jinja2 import Template

# HTML templates for ticket cards
TICKET_CARD_TEMPLATE = """
<a href="{{ link }}" target="_blank" style="text-decoration: none; color: inherit; display: block; margin-bottom: 10px;">
<div style="display: flex; background: white; border-radius: 10px; border: 1px solid #eee; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
<div style="width: 100px; min-height: 100px; background-image: url('{{ img_url }}'); background-size: cover; background-position: center; flex-shrink: 0;"></div>
<div style="padding: 10px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between;">
<div style="font-weight: bold; color: #333; margin-bottom: 4px;">{{ title }}</div>
<div style="display: flex; justify-content: space-between; align-items: center;">
<span style="background-color: {{ badge_color }}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.75em;">{{ platform_name }}</span>
<div style="color: #e91e63; font-weight: bold;">{{ price }} &gt;</div>
</div></div></div></a>
"""

def render_ticket_card(link, img_url, title, badge_color, platform_name, price):
    """
    渲染票券卡片 HTML。
    """
    template = Template(TICKET_CARD_TEMPLATE)
    html_code = template.render(
        link=link,
        img_url=img_url,
        title=title,
        badge_color=badge_color,
        platform_name=platform_name,
        price=price
    )
    
    # 關鍵：移除所有前後空白與換行，變成一行字串
    # 這能 100% 防止 Streamlit 把它當成 code block
    return html_code.strip().replace("\n", "")