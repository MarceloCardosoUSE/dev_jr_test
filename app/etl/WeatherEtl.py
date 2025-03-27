from app.services.WeatherService import WeatherAPIClient
from app.models.Weather import WeatherData
from app.database import SessionLocal
from datetime import datetime

class WeatherETL:
    def __init__(self):
        self.api_client = WeatherAPIClient()
        self.db = SessionLocal()

    def extract(self, city: str, country_code: str = None):
        return self.api_client.get_weather_by_city(city, country_code)

    def transform(self, data: dict) -> dict:
        return {
            'city': data['name'],
            'country': data['sys']['country'],
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'temp_min': data['main']['temp_min'],
            'temp_max': data['main']['temp_max'],
            'pressure': data['main']['pressure'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'wind_deg': data['wind'].get('deg', 0),  
            'clouds': data['clouds']['all'],
            'weather_main': data['weather'][0]['main'],
            'weather_description': data['weather'][0]['description'],
            'sunrise': datetime.fromtimestamp(data['sys']['sunrise']),
            'sunset': datetime.fromtimestamp(data['sys']['sunset']),
            'timezone': data['timezone'],
            'forecast_date': datetime.fromtimestamp(data['dt']).date() 
        }

    def load(self, data):
        db_data = WeatherData(**data.dict())
        self.db.add(db_data)
        self.db.commit()
        self.db.refresh(db_data)
        return db_data

    def run_etl(self, city: str, country_code: str = None):
        try:
            extracted_data = self.extract(city, country_code)
            transformed_data = self.transform(extracted_data)
            loaded_data = self.load(transformed_data)
            return loaded_data
        except Exception as e:
            self.db.rollback()
            raise e
        finally:
            self.db.close()