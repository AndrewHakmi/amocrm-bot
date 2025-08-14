from fastapi import APIRouter, Body
from app.api.schemas.price_dto import PriceEstimateIn, PriceEstimateOut
from app.api.schemas.utils import ErrorResponse
from app.services.api_services.pricing_service import PricingServiceDep

router = APIRouter(prefix="/price", tags=["pricing"])

@router.post(
    "/estimate",
    response_model=PriceEstimateOut,
    summary="Оценка стоимости по триплету (device → model → issue)",
    description=(
        "Возвращает диапазон цен, ETA, гарантию и `onsite_possible`. "
        "Алгоритм: `model+issue` → `device+issue` → `issue` (fallback). "
        "Можно указать `zone` для надбавки (если настроена)."
    ),
    responses={
        200: {"description": "Оценка посчитана", "model": PriceEstimateOut},
        400: {"description": "Неверные данные", "model": ErrorResponse},
        404: {"description": "Правило цены не найдено", "model": ErrorResponse},
        500: {"description": "Внутренняя ошибка", "model": ErrorResponse},
    },
)
async def estimate(
    pricing: PricingServiceDep,
    payload: PriceEstimateIn = Body(
        ...,
        examples={
            "ex1": {
                "summary": "Пример",
                "value": {"deviceType": "iPhone", "model": "iPhone 12", "symptom": "battery", "zone": "Алматы-центр"}
            }
        },
    )
):
    p = await pricing.estimate(device_type=payload.deviceType, model=payload.model, symptom=payload.symptom, zone=payload.zone)
    return PriceEstimateOut(
        onsite_possible=p["onsite_possible"], price_min=p["min"], price_max=p["max"],
        currency=p["currency"], eta_min=p.get("eta_min"), eta_max=p.get("eta_max"),
        warranty_months=p.get("warranty_months")
    )