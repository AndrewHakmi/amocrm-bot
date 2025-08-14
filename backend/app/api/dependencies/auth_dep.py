
from fastapi import Depends, HTTPException, Request
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer

from app.api.schemas.user_dto import TokenPayload
from app.config import settings
from app.core import security
from app.services.api_services.user_service import get_user_service, UserService
from jwt import InvalidTokenError, decode
from pydantic import ValidationError
from app.core.postgres.models.users import User
from starlette import status

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

TokenDep = Annotated[str, Depends(reusable_oauth2)]

async def get_current_user(token: TokenDep, user_service: UserService = Depends(get_user_service)):
    try:
        payload = decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    user = await user_service.find_by_id(token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
