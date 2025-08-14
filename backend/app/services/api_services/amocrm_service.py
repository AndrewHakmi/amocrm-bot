from typing import Optional, Annotated
from fastapi import Depends
from app.services.uow.unit_of_work import AbstractUnitOfWork
from app.services.uow.sqlalchemy_uow import SQLAlchemyUnitOfWork

class AmoCRMService:
    def __init__(self, uow_cls: type[AbstractUnitOfWork]): self.uow_cls = uow_cls

    async def upsert_contact(self, *, phone: Optional[str], name: Optional[str]) -> Optional[str]:
        # TODO: amo API; пока — вернём фиктивный id
        return "amo_contact_id_1"

    async def upsert_lead(self, *, contact_id: Optional[str], title: str, price: Optional[float]) -> Optional[str]:
        # TODO: amo API
        return "amo_lead_id_1"

    async def add_note(self, *, lead_id:str, text:str, attachments:list[str]|None=None) -> None:
        # TODO: amo API
        return None

def get_amocrm_service(): return AmoCRMService(SQLAlchemyUnitOfWork)
AmoServiceDep = Annotated[AmoCRMService, Depends(get_amocrm_service)]