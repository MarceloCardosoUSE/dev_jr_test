from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Path, Query
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, text
from database import get_db, init_db
from models import Forecasts
from pydantic import BaseModel

app = FastAPI()

class CityPost(BaseModel):
    cidade: str

@app.on_event("startup")
async def startup():
    await init_db()

@app.get('/')
def index():
    return {"message": "Hello World"}

@app.post("/previsao/")
async def post_forecasts(
    payload: CityPost, 
    db: AsyncSession = Depends(get_db)
):
    existing_forecasts = await db.execute(
        select(Forecasts.date)
        .where(Forecasts.city_name == payload.cidade))
    existing_dates = existing_forecasts.scalars().all()

    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        'q': payload.cidade,
        'appid': '7aa4816d9c08eafc1b0c5c4589fbd974',
        'units': 'metric',
        'lang': 'pt_br'
    }
    response = await httpx.AsyncClient().get(url, params = params)

    received_data = response.json()

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=received_data.get("message", "An unknown error occurred").title())
    
    new_entries = []
    for entry in received_data.get("list", []):
        date = datetime.fromtimestamp(entry["dt"])
        if date in existing_dates:
            continue
        new_weather = Forecasts(
            city_name=payload.cidade,
            temp=int(entry["main"]["temp"]),
            description=entry["weather"][0]["description"].title(),
            date=date
        )
        db.add(new_weather)
        new_entries.append(new_weather)

    await db.commit()

    return {"message": f"Inserted {len(new_entries)} records for {payload.cidade}", "data": new_entries}
    
@app.get("/previsao/")
async def get_forecasts(
    cidade: str = Query(None, description="Filter by city name"),
    data: str = Query(None, description="Filter by date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
):
    query = select(Forecasts).order_by(Forecasts.city_name, Forecasts.date)

    if cidade:
        query = query.where(Forecasts.city_name == cidade)
    
    if data:
        try:
            date_obj = datetime.strptime(data, "%Y-%m-%d").date()
            query = query.where(func.DATE(Forecasts.date) == date_obj)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    result = await db.execute(query)
    forecasts = result.scalars().all()

    return {"total": len(forecasts), "forecasts": forecasts}

@app.delete("/previsao/{id}")
async def delete_forecast(
    id: str = Path(..., description="The ID of the forecast to delete"),
    db: AsyncSession = Depends(get_db),
):
    forecast = await db.get(Forecasts, id)

    if not forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")

    await db.delete(forecast)
    await db.commit()

    return {"message": f"Forecast with ID {id} has been deleted"}