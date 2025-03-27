from datetime import datetime, date
from pydantic import BaseModel

class WeatherDataBase(BaseModel):
    city: str
    country: str

class WeatherDataCreate(WeatherDataBase):
    temperature: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    humidity: int
    wind_speed: float
    wind_deg: int
    clouds: int
    weather_main: str
    weather_description: str
    sunrise: datetime
    sunset: datetime
    timezone: int
    forecast_date: datetime

class WeatherData(WeatherDataCreate):
    id: int
    recorded_at: datetime

    class Config:
        from_attributes = True

class WeatherDataFilter(BaseModel):
    city: str | None = None
    start_date: date | None = None
    end_date: date | None = None

class WeatherDataDeleteResponse(BaseModel):
    message: str
    deleted_count: int