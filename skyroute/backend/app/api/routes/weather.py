from fastapi import APIRouter
from app.services.weather_service import WeatherService

router = APIRouter(prefix="/weather", tags=["weather"])
weather_service = WeatherService()


@router.get("/current", summary="获取当前天气")
async def get_current_weather(lat: float = 39.9, lon: float = 116.4):
    """获取指定坐标的当前气象数据"""
    return await weather_service.get_current_weather(lat, lon)


@router.get("/flight-conditions", summary="获取飞行气象条件评估")
async def get_flight_conditions(lat: float = 39.9, lon: float = 116.4):
    """评估当前气象条件是否适合飞行"""
    weather = await weather_service.get_current_weather(lat, lon)
    return {
        "weather": weather,
        "is_flyable": weather["flight_risk"] != "high",
        "recommendations": _get_recommendations(weather),
    }


def _get_recommendations(weather: dict) -> list:
    """根据天气数据生成飞行建议"""
    recs = []
    if weather["wind_speed"] > 10:
        recs.append("风速较大，建议降低飞行高度")
    if weather["visibility"] < 5:
        recs.append("能见度较低，建议推迟飞行")
    if weather["cloud_cover"] > 80:
        recs.append("云层较厚，注意信号遮挡")
    if not recs:
        recs.append("气象条件良好，适合飞行")
    return recs
