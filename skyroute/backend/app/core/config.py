from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_ENV: str = "development"
    SECRET_KEY: str = "dev-secret-key-change-in-prod"
    
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/skyroute"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    OPENWEATHER_API_KEY: str = ""
    CESIUM_ION_TOKEN: str = ""
    
    CORS_ORIGINS: str = "http://localhost:5173"
    
    VOXEL_SIZE: int = 10
    CONFLICT_SEPARATION_HORIZONTAL: float = 50.0
    CONFLICT_SEPARATION_VERTICAL: float = 30.0
    WEATHER_UPDATE_INTERVAL: int = 300
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
