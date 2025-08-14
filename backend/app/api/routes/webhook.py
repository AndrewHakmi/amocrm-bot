from fastapi import APIRouter, Request

from app.api.schemas.user_dto import Message
from app.api.schemas.utils import ErrorResponse

router = APIRouter(prefix="/webhook", tags=["webhooks"])

@router.post(
    "/amocrm",
    response_model=Message,
    status_code=200,
    summary="Вебхук от amoCRM",
    description=(
        "Принимает события от amoCRM (смена статусов, завершение, no-show). "
        "По событию триггерит пост-сервисные операции: оплата/счёт, запрос отзыва, теги."
    ),
    responses={
        200: {"description": "Обработано", "model": Message},
        400: {"description": "Неверный формат", "model": ErrorResponse},
        500: {"description": "Внутренняя ошибка", "model": ErrorResponse},
    },
)
async def amocrm_hook(req: Request):
    body = await req.json()
    # TODO: обработка
    return {"message": "ok"}

@router.post(
    "/calendar",
    response_model=Message,
    summary="Вебхук календаря мастеров",
    description="Синхронизация изменений событий календаря (создание/отмена/перенос).",
    responses={
        200: {"description": "Обработано", "model": Message},
        400: {"description": "Неверный формат", "model": ErrorResponse},
        500: {"description": "Внутренняя ошибка", "model": ErrorResponse},
    },
)
async def calendar_hook(req: Request):
    body = await req.json()
    # TODO: обработка
    return {"message": "ok"}