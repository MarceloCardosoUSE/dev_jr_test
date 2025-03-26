from sqlalchemy import Column, Integer, String, DateTime, UUID
from datetime import datetime
from database import Base
import uuid

class Forecasts(Base):
    __tablename__ = "forecasts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    city_name = Column(String, index=True)
    temp = Column(Integer)
    description = Column(String)
    date = Column(DateTime, default=datetime.now)