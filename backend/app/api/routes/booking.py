from fastapi import APIRouter, Body
from app.api.schemas.bookings_dto import BookingCreateIn, BookingCreateOut, BookingCancelIn, BookingCancelOut
from app.api.schemas.utils import ErrorResponse
from app.services.api_services.booking_service import BookingServiceDep

router = APIRouter(prefix="/bookings", tags=["booking"])

@router.post(
    "",
    response_model=BookingCreateOut,
    status_code=201,
    summary="Создать бронирование по выбранному слоту",
    description=(
        "Атомарно создаёт бронирование и помечает слот занятым. "
        "При ошибке календаря/интеграции — должен откатить изменения."
    ),
    responses={
        201: {"description": "Бронирование создано", "model": BookingCreateOut},
        400: {"description": "Неверные данные", "model": ErrorResponse},
        404: {"description": "Слот не найден", "model": ErrorResponse},
        409: {"description": "Слот занят", "model": ErrorResponse},
        500: {"description": "Внутренняя ошибка", "model": ErrorResponse},
    },
)
async def create(
    booking: BookingServiceDep,
    payload: BookingCreateIn = Body(
        ...,
        examples={
            "ex": {
                "summary": "Пример бронирования",
                "value": {"slot_id": "uuid-slot", "lead_id": "amo_lead_id_1", "address": "ул. Абая 10"}
            }
        },
    ),

):
    res = await booking.create(slot_id=payload.slot_id, lead_id=payload.lead_id,
                               address=payload.address, lat=payload.lat, lng=payload.lng, notes=payload.notes)
    return BookingCreateOut(**res)

@router.post(
    "/cancel",
    response_model=BookingCancelOut,
    summary="Отменить бронирование",
    description="Меняет статус бронирования на `CANCELLED` и освобождает слот.",
    responses={
        200: {"description": "Бронирование отменено", "model": BookingCancelOut},
        404: {"description": "Бронирование не найдено", "model": ErrorResponse},
        500: {"description": "Внутренняя ошибка", "model": ErrorResponse},
    },
)
async def cancel(
        booking: BookingServiceDep,
    payload: BookingCancelIn = Body(
        ...,
        examples={"ex": {"summary": "Пример отмены", "value": {"booking_id": "uuid-booking", "reason": "Клиент перенёс"}}},
    )

):
    res = await booking.cancel(booking_id=payload.booking_id, reason=payload.reason)
    return BookingCancelOut(**res)