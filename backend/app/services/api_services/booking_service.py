from typing import Optional, Annotated
from fastapi import Depends, HTTPException
from app.services.uow.unit_of_work import AbstractUnitOfWork
from app.services.uow.sqlalchemy_uow import SQLAlchemyUnitOfWork

class BookingService:
    def __init__(self, uow_cls: type[AbstractUnitOfWork]): self.uow_cls = uow_cls

    async def create(self, *, slot_id:str, lead_id:Optional[str], address:Optional[str], lat:Optional[float], lng:Optional[float], notes:Optional[str]) -> dict:
        async with self.uow_cls() as uow:
            slot = await uow.availability.find_one_or_none({"id": slot_id})
            if not slot or getattr(slot, "is_booked", False):
                raise HTTPException(409, "Slot not available")
            # помечаем занятым и создаём booking
            await uow.availability.update({"id": slot_id}, {"is_booked": True})
            booking = await uow.bookings.add({
                "master_id": str(slot.master_id),
                "lead_link_id": lead_id,
                "status": "CONFIRMED",
                "start": slot.start,
                "end": slot.end,
                "address": address, "lat": lat, "lng": lng,
                "notes": notes
            })
            return {"booking_id": str(booking.id), "calendar_event_id": None, "status": "CONFIRMED"}

    async def cancel(self, *, booking_id:str, reason:Optional[str]) -> dict:
        async with self.uow_cls() as uow:
            b = await uow.bookings.find_one_or_none({"id": booking_id})
            if not b: raise HTTPException(404, "Booking not found")
            await uow.bookings.update({"id": booking_id}, {"status": "CANCELLED"})
            await uow.availability.update({"master_id": b.master_id, "start": b.start, "end": b.end}, {"is_booked": False})
            return {"booking_id": booking_id, "status": "CANCELLED"}

def get_booking_service(): return BookingService(SQLAlchemyUnitOfWork)
BookingServiceDep = Annotated[BookingService, Depends(get_booking_service)]