import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Body

from starlette import status
from starlette.requests import Request

from app.api.dependencies.auth_dep import CurrentUser, get_current_active_superuser
from app.api.schemas.catalog_dto import DevicePublic, DeviceCreate, DeviceUpdate
from app.api.schemas.utils import ErrorResponse

from app.core.security import get_password_hash
from app.services.api_services.user_service import UserServiceDep
from app.api.schemas.user_dto import UserPublic, UserCreate, UpdatePassword, \
    Message,  UsersPublic
from app.core.limiter import limiter
from app.services.exceptions.user_err import EmailAlreadyExistsError, PhoneAlreadyExistsError, UserNotFoundError
from app.services.exceptions.catalog_err import DeviceAlreadyExistsError, DeviceNotFoundError
router = APIRouter(prefix="/users", tags=["users"])



@router.post(
    "/",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")
async def create_user(
    *,
    request: Request,
    user_in: UserCreate,
    current_user: CurrentUser,
    user_service: UserServiceDep
) -> Any:
    """
    Create a new user. Only accessible by superusers.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=401,
            detail="Не достаточно прав"
        )
    try:
        user = await user_service.create_user(user_in)
    except EmailAlreadyExistsError:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует.")
    except PhoneAlreadyExistsError:
        raise HTTPException(status_code=400, detail="Пользователь с таким телефоном уже существует.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")
    return user


@router.patch("/me/password", response_model=Message, status_code=status.HTTP_200_OK,
    summary="Изменить пароль текущего пользователя",
    description=(
        "Обновляет пароль **текущего авторизованного пользователя**. "
        "Ожидает новый пароль в теле запроса. Пароль хешируется на сервере."
    ))
async def update_password_me(
    new_password: str,
    user_service: UserServiceDep,
    current_user: CurrentUser
) -> Any:
    try:
        hashed_password = get_password_hash(new_password)
        update_data = {"password": hashed_password, "email": current_user.email}
        await user_service.update_me(current_user.id, UpdatePassword.model_validate(update_data))
        return Message(message="Пароль успешно обновлён")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении пароля: {str(e)}")


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    return current_user

@router.delete("/me", response_model=Message)
async def delete_user_me(user_service: UserServiceDep, current_user: CurrentUser) -> Any:
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Cупер пользователи не могут удалять сами себя"
        )
    try:
        await user_service.delete_by_id(current_user.id)
        return Message(message="Вы успешно удалили свой аккаунт")
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")




@router.get("/all", response_model=UsersPublic, dependencies=[Depends(get_current_active_superuser)])
async def get_all_users(
    user_service: UserServiceDep,
    skip: int = 0,
    limit: int = 100
):
    try:
        users = await user_service.get_all(skip=skip, limit=limit)
        users_public = [UserPublic.model_validate(user) for user in users]

        return UsersPublic(users=users_public)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@router.get("/{user_id}", response_model=UserPublic)
async def read_user_by_id(
    user_id: uuid.UUID,
    user_service: UserServiceDep,
    current_user: CurrentUser
) -> Any:
    try:
        user = await user_service.find_by_id(user_id)
        if user == current_user or current_user.is_superuser:
            return user
        raise HTTPException(
            status_code=403,
            detail="Недостаточно прав для просмотра этого пользователя",
        )
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")



@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
async def delete_user(
    user_id: uuid.UUID,
    user_service: UserServiceDep,
    current_user: CurrentUser
) -> Message:
    if user_id == current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Суперпользователь не может удалить сам себя"
        )
    try:
        await user_service.delete_by_id(user_id)
        return Message(message=f"Пользователь с id {user_id} удалён")
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении: {str(e)}")




@router.get("/admin/get-devices", response_model=list[DevicePublic], dependencies=[Depends(get_current_active_superuser)],
    status_code=status.HTTP_201_CREATED,
    summary="Создать устройство",
    description="Создаёт запись устройства. Уникальность (brand, type, name) контролируется сервисом.",
    responses={
        201: {"description": "Создано", "model": DevicePublic},
        401: {"description": "Неавторизован", "model": ErrorResponse},
        409: {"description": "Дубликат (brand, type, name)", "model": ErrorResponse},
    })
async def list_devices(
    user_service: UserServiceDep,
    skip: int = 0,
    limit: int = 100
) -> Any:
    items = await user_service.list_devices(skip=skip, limit=limit)
    return [DevicePublic(id=str(i.id), brand=i.brand, type=i.type, name=i.name) for i in items]

@router.post("admin/create-device", response_model=DevicePublic,  dependencies=[Depends(get_current_active_superuser)])
async def create_device(
        user_service: UserServiceDep,
        payload: DeviceCreate = Body(
            ...,
            examples={
                "ex": {"summary": "Пример", "value": {"brand": "Apple", "type": "phone", "name": "iPhone"}}
            },
        )
) -> Any:
    try:
        d = await user_service.create_device(payload)
        return DevicePublic(id=str(d.id), brand=d.brand, type=d.type, name=d.name)
    except DeviceAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Device with the same (brand, type, name) already exists")



@router.patch("admin/devices/update/{device_id}", response_model=DevicePublic, dependencies=[Depends(get_current_active_superuser)],
    summary="Обновить устройство",
    description="Обновляет часть полей устройства. Проверяет коллизию уникальности.",
    responses={
        200: {"description": "Обновлено", "model": DevicePublic},
        401: {"description": "Неавторизован", "model": ErrorResponse},
        404: {"description": "Не найдено", "model": ErrorResponse},
        409: {"description": "Дубликат", "model": ErrorResponse},
    })
async def update_device(
    device_id: str,
    payload: DeviceUpdate,
    user_service: UserServiceDep,
) -> Any:
    try:
        d = await user_service.update_device(device_id, payload)
        return DevicePublic(id=str(d.id), brand=d.brand, type=d.type, name=d.name)
    except DeviceNotFoundError:
        raise HTTPException(status_code=404, detail="Device not found")
    except DeviceAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Device with the same (brand, type, name) already exists")

@router.delete("admin/devices/delete/{device_id}", dependencies=[Depends(get_current_active_superuser)], summary="Удалить устройство",
    description="Удаляет запись устройства. Если связана с моделями — учитывайте внешние ключи/каскады.",
    responses={
        200: {"description": "Удалено", "model": Message},
        401: {"description": "Неавторизован", "model": ErrorResponse},
        404: {"description": "Не найдено", "model": ErrorResponse},
    })
async def delete_device(
    device_id: str,
    user_service: UserServiceDep,
):
    try:
        await user_service.delete_device(device_id)
        return {"message": "Device deleted"}
    except DeviceNotFoundError:
        raise HTTPException(status_code=404, detail="Device not found")