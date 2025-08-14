from pydantic import BaseModel
from typing import Optional

class PriceEstimateIn(BaseModel):
    deviceType: str
    model: str
    symptom: str
    zone: Optional[str] = None

class PriceEstimateOut(BaseModel):
    onsite_possible: bool
    price_min: Optional[float]
    price_max: Optional[float]
    currency: str = "KZT"
    eta_min: Optional[int] = None
    eta_max: Optional[int] = None
    warranty_months: Optional[int] = None