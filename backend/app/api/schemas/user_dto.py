from datetime import datetime
from typing import Optional
from uuid import UUID

from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel, field_validator, Field, ConfigDict


class UserRegister(BaseModel):
    email: str = Field(max_length=128)
    password: str


    @field_validator('email')
    def validate_email_rfc(cls, v):
        try:
            result = validate_email(v, check_deliverability=False)
            blocked_domains = {'test.com', 'example.com'}
            domain = v.split('@')[-1]
            if domain in blocked_domains:
                raise ValueError('Введите реальную почту')
            return result.normalized
        except EmailNotValidError as e:
            raise ValueError(str(e))

class UserCreate(UserRegister):
    is_superuser: bool = False

class UserPublic(BaseModel):
    id: UUID
    email: str = Field(max_length=128)
    is_superuser: bool = False

    model_config = ConfigDict(from_attributes=True)


class UsersPublic(BaseModel):
    users: list[UserPublic]


class Message(BaseModel):
    message: str = Field(max_length=100)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str | None = None

class NewPassword(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


class UpdatePassword(BaseModel):
    password: str
    email: str

    @field_validator('password')
    def validate_password_complexity(cls, v):
        if len(v) < 8:
            raise ValueError('Пароль должен быть не менее 8 символов в длину')
        if not any(c.isdigit() for c in v):
            raise ValueError('Пароль должен содержать по крайней мере одну цифру')
        return v
