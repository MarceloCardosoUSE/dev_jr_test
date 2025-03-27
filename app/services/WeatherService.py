import requests
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv
from app.schemas.Weather import WeatherDataCreate
from typing import Optional
from fastapi import HTTPException

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

class WeatherAPIClient:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')

        if not self.api_key:
            raise ValueError("OpenWeatherMap API key not found in .env file")

        self.base_url = 'https://api.openweathermap.org/data/2.5/weather'

    def get_weather_by_city(self, city: str, country_code: Optional[str] = None) -> WeatherDataCreate:
        try:
            params = {
                'q': f"{city},{country_code}" if country_code else city,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
                
            response.raise_for_status()
            data = response.json()
            
            return self._transform_data(data)
            
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=502,
                detail=f"Weather service unavailable: {str(e)}"
            )

    def _transform_data(self, data: dict) -> WeatherDataCreate:
        try:
            return WeatherDataCreate(
                city=data['name'],
                country=data['sys']['country'],
                temperature=data['main']['temp'],
                feels_like=data['main']['feels_like'],
                temp_min=data['main']['temp_min'],
                temp_max=data['main']['temp_max'],
                pressure=data['main']['pressure'],
                humidity=data['main']['humidity'],
                wind_speed=data['wind']['speed'],
                wind_deg=data['wind'].get('deg', 0),
                clouds=data['clouds']['all'],
                weather_main=data['weather'][0]['main'],
                weather_description=data['weather'][0]['description'],
                sunrise=datetime.fromtimestamp(data['sys']['sunrise']),
                sunset=datetime.fromtimestamp(data['sys']['sunset']),
                timezone=data['timezone'],
                forecast_date=datetime.fromtimestamp(data['dt'])
            )
        except KeyError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Invalid data structure from weather service: Missing {str(e)}"
            )