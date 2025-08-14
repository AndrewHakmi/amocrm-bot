from pydantic import BaseModel
from typing import List, Optional

class SlotsSuggestIn(BaseModel):
    lead_id: Optional[str] = None
    zone: Optional[str] = None
    duration_min: int = 60

class Slot(BaseModel):
    slot_id: str
    master_id: str
    start: str
    end: str

class SlotsSuggestOut(BaseModel):
    slots: List[Slot]