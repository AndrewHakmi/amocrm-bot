from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr


router = APIRouter(prefix="/utils", tags=["utils"])



@router.get("/health-check/",  summary="Проверка живости сервиса",
    description="Возвращает `ok`, если процесс жив и обрабатывает запросы.")
async def health_check() -> bool:
    return True
