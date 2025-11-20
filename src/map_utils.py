# src/map_utils.py
import folium

def render_map(trip_data: dict):
    # 安全檢查
    itinerary = trip_data.get('daily_itinerary', [])
    if not itinerary:
        return folium.Map(location=[23.69, 120.96], zoom_start=7)

    # 找中心點
    start_lat, start_lng = 25.03, 121.56
    try:
        first_spot = itinerary[0]['attractions'][0]
        if first_spot.get('latitude'):
            start_lat = first_spot['latitude']
            start_lng = first_spot['longitude']
    except: pass

    m = folium.Map(location=[start_lat, start_lng], zoom_start=13)
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'cadetblue']

    for i, day in enumerate(itinerary):
        day_color = colors[i % len(colors)]
        route_points = []
        
        for spot in day.get('attractions', []):
            lat, lng = spot.get('latitude'), spot.get('longitude')
            if lat and lng:
                route_points.append([lat, lng])
                folium.Marker(
                    [lat, lng],
                    popup=f"Day {day.get('day')}: {spot.get('name')}",
                    icon=folium.Icon(color=day_color)
                ).add_to(m)
        
        if len(route_points) > 1:
            folium.PolyLine(route_points, color=day_color, weight=4, opacity=0.7).add_to(m)

    return m