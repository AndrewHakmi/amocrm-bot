from pydantic import BaseModel
from typing import Optional

class BookingCreateIn(BaseModel):
    slot_id: str
    lead_id: Optional[str] = None
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    notes: Optional[str] = None

class BookingCreateOut(BaseModel):
    booking_id: str
    calendar_event_id: Optional[str] = None
    status: str

class BookingCancelIn(BaseModel):
    booking_id: str
    reason: Optional[str] = None

class BookingCancelOut(BaseModel):
    booking_id: str
    status: str