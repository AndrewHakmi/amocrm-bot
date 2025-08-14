from typing import List, Optional, Annotated
from fastapi import Depends
from datetime import datetime, timedelta, timezone
from app.services.uow.unit_of_work import AbstractUnitOfWork
from app.services.uow.sqlalchemy_uow import SQLAlchemyUnitOfWork

class SchedulingService:
    def __init__(self, uow_cls: type[AbstractUnitOfWork]): self.uow_cls = uow_cls

    async def suggest(self, *, lead_id: Optional[str], zone: Optional[str], duration_min:int) -> List[dict]:
        async with self.uow_cls() as uow:
            # TODO: фильтровать мастеров по зоне/скиллам; пока — заглушка «ближайшие 2–3 слота»
            now = datetime.now(timezone.utc)
            slots = await uow.availability.find_all(skip=0, limit=10)
            result = []
            for sl in slots:
                if getattr(sl, "is_booked", False): continue
                result.append({
                    "slot_id": str(sl.id),
                    "master_id": str(sl.master_id),
                    "start": sl.start.isoformat(),
                    "end": sl.end.isoformat(),
                })
                if len(result) >= 3: break
            return result

def get_scheduling_service(): return SchedulingService(SQLAlchemyUnitOfWork)
SchedulingServiceDep = Annotated[SchedulingService, Depends(get_scheduling_service)]