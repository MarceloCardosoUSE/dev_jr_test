from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database import Base, engine

class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, nullable=False, index=True)
    country = Column(String, nullable=False)
    temperature = Column(Float, nullable=False)
    feels_like = Column(Float, nullable=False)
    temp_min = Column(Float, nullable=False)
    temp_max = Column(Float, nullable=False)
    pressure = Column(Integer, nullable=False)
    humidity = Column(Integer, nullable=False)
    wind_speed = Column(Float, nullable=False)
    wind_deg = Column(Integer, nullable=False)
    clouds = Column(Integer, nullable=False)
    weather_main = Column(String, nullable=False)
    weather_description = Column(String, nullable=False)
    sunrise = Column(DateTime, nullable=False)
    sunset = Column(DateTime, nullable=False)
    timezone = Column(Integer, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    forecast_date = Column(DateTime, nullable=False)

    def __repr__(self):
        return (f"<WeatherData(city={self.city}, country={self.country}, temperature={self.temperature}, "
                f"weather_main={self.weather_main}, recorded_at={self.recorded_at})>")

Base.metadata.create_all(bind=engine)
