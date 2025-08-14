from fastapi import APIRouter, Body
from app.api.schemas.intake_dto import IntakeIn, IntakeOut
from app.api.schemas.utils import ErrorResponse
from app.services.api_services.pricing_service import PricingServiceDep
from app.services.api_services.amocrm_service import AmoServiceDep

router = APIRouter(prefix="/intake", tags=["intake"])

@router.post(
    "",
    response_model=IntakeOut,
    summary="Приём анкеты из Typebot/n8n",
    description=(
        "Принимает данные лида (устройство, модель, симптом, контакты), "
        "создаёт/обновляет контакт и лид в amoCRM, добавляет заметку, "
        "и возвращает предварительную оценку стоимости и признак `onsite_possible`."
    ),
    responses={
        200: {"description": "Анкета принята, оценка рассчитана", "model": IntakeOut},
        400: {"description": "Неверные данные", "model": ErrorResponse},
        500: {"description": "Внутренняя ошибка", "model": ErrorResponse},
    },
)
async def intake(
    pricing: PricingServiceDep,
    amo: AmoServiceDep,
    payload: IntakeIn = Body(
        ...,
        examples={
            "iphone_battery": {
                "summary": "iPhone 12 — батарея",
                "value": {
                    "deviceType": "iPhone",
                    "model": "iPhone 12",
                    "symptom": "battery",
                    "description": "Быстро разряжается",
                    "photos": [],
                    "address": "ул. Абая 10",
                    "lat": 43.238949,
                    "lng": 76.889709,
                    "preferredTimes": ["сегодня вечер", "завтра утро"],
                    "phone": "+77001234567",
                    "name": "Иван",
                    "channel": "typebot"
                }
            }
        },
    )):
    contact_id = await amo.upsert_contact(phone=payload.phone, name=payload.name)
    lead_id = await amo.upsert_lead(contact_id=contact_id, title=f"{payload.deviceType} {payload.model} — {payload.symptom}", price=None)
    p = await pricing.estimate(device_type=payload.deviceType, model=payload.model, symptom=payload.symptom, zone=None)
    await amo.add_note(lead_id=lead_id, text=f"Intake via {payload.channel}: {payload.description or '-'}", attachments=payload.photos or [])
    return IntakeOut(lead_id=lead_id, onsite_possible=p["onsite_possible"],
                     price_min=p["min"], price_max=p["max"], currency=p["currency"])
