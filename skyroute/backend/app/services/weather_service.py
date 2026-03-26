"""
天气服务 - 获取并缓存气象数据
"""
import httpx
import json
from datetime import datetime
from typing import Dict, Any, Optional

from app.core.config import settings


class WeatherService:
    """天气数据服务（OpenWeatherMap API集成）"""

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self._cache: Dict[str, Any] = {}
        self._cache_time: Optional[datetime] = None

    async def get_current_weather(
        self, lat: float = 39.9, lon: float = 116.4
    ) -> Dict[str, Any]:
        """获取指定坐标的当前天气数据"""
        now = datetime.utcnow()
        if (
            self._cache_time
            and (now - self._cache_time).seconds < settings.WEATHER_UPDATE_INTERVAL
            and f"{lat:.2f},{lon:.2f}" in self._cache
        ):
            return self._cache[f"{lat:.2f},{lon:.2f}"]

        if not self.api_key:
            return self._mock_weather(lat, lon)

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self.BASE_URL}/weather",
                    params={"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric"},
                )
                resp.raise_for_status()
                data = resp.json()

                result = self._parse_weather(data)
                self._cache[f"{lat:.2f},{lon:.2f}"] = result
                self._cache_time = now
                return result
        except Exception:
            return self._mock_weather(lat, lon)

    def _parse_weather(self, data: Dict) -> Dict[str, Any]:
        """解析OpenWeatherMap响应"""
        wind = data.get("wind", {})
        main = data.get("main", {})
        clouds = data.get("clouds", {})
        return {
            "temperature": main.get("temp", 20),
            "humidity": main.get("humidity", 60),
            "pressure": main.get("pressure", 1013),
            "wind_speed": wind.get("speed", 5),
            "wind_direction": wind.get("deg", 180),
            "visibility": data.get("visibility", 10000) / 1000,
            "cloud_cover": clouds.get("all", 20),
            "weather_code": data.get("weather", [{}])[0].get("id", 800),
            "description": data.get("weather", [{}])[0].get("description", "clear sky"),
            "flight_risk": self._assess_flight_risk(wind.get("speed", 5), data.get("visibility", 10000)),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _assess_flight_risk(self, wind_speed: float, visibility: float) -> str:
        """评估飞行风险等级"""
        if wind_speed > 15 or visibility < 1000:
            return "high"
        elif wind_speed > 8 or visibility < 3000:
            return "medium"
        return "low"

    def _mock_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """无API密钥时的模拟天气数据"""
        import math, time
        hour = (time.time() % 86400) / 3600
        temp = 18 + 8 * math.sin((hour - 6) * math.pi / 12)
        wind_speed = 3 + 2 * math.sin(hour * 0.5)
        return {
            "temperature": round(temp, 1),
            "humidity": 55,
            "pressure": 1013,
            "wind_speed": round(wind_speed, 1),
            "wind_direction": 225,
            "visibility": 10.0,
            "cloud_cover": 20,
            "weather_code": 800,
            "description": "clear sky (模拟数据)",
            "flight_risk": "low",
            "timestamp": datetime.utcnow().isoformat(),
        }
