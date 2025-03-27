from pydantic import BaseModel

class WebhookPayload(BaseModel):
    city: str
    country_code: str = None