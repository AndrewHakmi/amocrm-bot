from pydantic import BaseModel, Field
from typing import Optional

class DeviceCreate(BaseModel):
    brand: str = Field(..., max_length=64)
    type: str = Field(..., max_length=32)
    name: str = Field(..., max_length=128)

class DevicePublic(BaseModel):
    id: str
    brand: str
    type: str
    name: str

class DeviceUpdate(BaseModel):
    brand: Optional[str] = None
    type: Optional[str] = None
    name: Optional[str] = None