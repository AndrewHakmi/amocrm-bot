from pydantic import BaseModel, Field, conlist
from typing import Optional, List

class IntakeIn(BaseModel):
    deviceType: str
    model: str
    symptom: str
    description: Optional[str] = None
    photos: Optional[List[str]] = None
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    preferredTimes: Optional[List[str]] = None
    phone: Optional[str] = None
    name: Optional[str] = None
    channel: str = "typebot"

class IntakeOut(BaseModel):
    lead_id: Optional[str] = None
    onsite_possible: bool
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    currency: str = "KZT"