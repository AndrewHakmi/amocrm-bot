from fastapi import APIRouter, Body
from app.api.schemas.slots_dto import SlotsSuggestIn, SlotsSuggestOut, Slot
from app.api.schemas.utils import ErrorResponse
from app.services.api_services.scheduling_service import SchedulingServiceDep

router = APIRouter(prefix="/slots", tags=["scheduling"])


@router.post(
    "/suggest",
    response_model=SlotsSuggestOut,
    summary="Подобрать 2–3 ближайших свободных слота",
    description=(
        "Возвращает список 2–3 слотов для записи с учётом зоны/длительности/доступности мастеров. "
        "Если слотов нет — возвращайте пустой массив; фронт/бот должен эскалировать менеджеру."
    ),
    responses={
        200: {"description": "Слоты подобраны", "model": SlotsSuggestOut},
        400: {"description": "Неверные данные", "model": ErrorResponse},
        500: {"description": "Внутренняя ошибка", "model": ErrorResponse},
    },
)
async def suggest(
    scheduling: SchedulingServiceDep,
    payload: SlotsSuggestIn = Body(
        ...,
        examples={
            "ex": {"summary": "Запрос слотов", "value": {"lead_id": "amo_lead_id_1", "zone": "Алматы-центр", "duration_min": 60}}
        },
    )
):
    items = await scheduling.suggest(lead_id=payload.lead_id, zone=payload.zone, duration_min=payload.duration_min)
    return SlotsSuggestOut(slots=[Slot(**i) for i in items])