from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from app.database import SessionLocal
from app.models.Weather import WeatherData as DBWeatherData
from app.schemas.Weather import WeatherData, WeatherDataDeleteResponse, WeatherDataFilter
from app.services.WeatherService import WeatherAPIClient

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post('/weather/{city}', response_model=WeatherData)
def create_weather_data(
    city: str, 
    country_code: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    client = WeatherAPIClient()
    try:
        weather_data = client.get_weather_by_city(city, country_code)
        db_weather = DBWeatherData(**weather_data.dict())
        db.add(db_weather)
        db.commit()
        db.refresh(db_weather)
        return db_weather
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/weather/{city}', response_model=List[WeatherData])
def get_weather_history(
    city: str,
    date: Optional[date] = Query(None, description="Filter by date in YYYY-MM-DD format"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(DBWeatherData).filter(DBWeatherData.city.ilike(f"%{city}%"))
    
    if date:
        query = query.filter(DBWeatherData.forecast_date == date)
    
    return query.order_by(DBWeatherData.recorded_at.desc()).offset(skip).limit(limit).all()

@app.delete("/weather/{weather_id}", response_model=WeatherDataDeleteResponse)
def delete_weather_record(
    weather_id: int,
    db: Session = Depends(get_db)
):
    result = db.query(DBWeatherData).filter(DBWeatherData.id == weather_id).delete()
    db.commit()
    if not result:
        raise HTTPException(status_code=404, detail="Weather record not found")
    return {"message": "Weather record deleted", "deleted_count": result}

@app.delete("/weather/", response_model=WeatherDataDeleteResponse)
def bulk_delete_weather_records(
    filter: WeatherDataFilter,
    db: Session = Depends(get_db)
):
    query = db.query(DBWeatherData)
    filters = []
    if filter.city:
        filters.append(DBWeatherData.city.ilike(f"%{filter.city}%"))
    if filter.start_date:
        filters.append(DBWeatherData.forecast_date >= filter.start_date)
    if filter.end_date:
        filters.append(DBWeatherData.forecast_date <= filter.end_date)
    
    if not filters:
        raise HTTPException(status_code=400, detail="At least one filter must be provided")
    
    result = query.filter(and_(*filters)).delete()
    db.commit()
    return {"message": "Weather records deleted", "deleted_count": result}

@app.post("/webhook/weather")
async def weather_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        payload = await request.json()
        if not payload.get('city'):
            raise HTTPException(status_code=400, detail="City parameter is required")
        
        client = WeatherAPIClient()
        weather_data = client.get_weather_by_city(payload['city'], payload.get('country_code'))
        
        # Save to database
        db_weather = DBWeatherData(**weather_data.dict())
        db.add(db_weather)
        db.commit()
        db.refresh(db_weather)
        
        return {
            "status": "success",
            "data": {
                "city": db_weather.city,
                "temperature": db_weather.temperature,
                "recorded_at": db_weather.recorded_at
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))