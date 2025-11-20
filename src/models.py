from pydantic import BaseModel, Field
from typing import List

# 定義單個景點的結構
class Attraction(BaseModel):
    name: str = Field(..., description="景點名稱")
    description: str = Field(..., description="簡短介紹")
    time: str = Field(..., description="建議抵達時間，例如 10:00")
    latitude: float = Field(..., description="緯度")
    longitude: float = Field(..., description="經度")

# 定義單日的結構
class DayItinerary(BaseModel):
    day: int
    theme: str = Field(..., description="當日主題，例如：古蹟巡禮")
    attractions: List[Attraction]

# 定義整個行程的結構 (這是 LLM 最終要吐給你的格式)
class TripPlan(BaseModel):
    trip_name: str
    total_days: int
    itinerary: List[DayItinerary]