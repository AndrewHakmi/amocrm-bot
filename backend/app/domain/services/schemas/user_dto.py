from uuid import UUID

from pydantic import BaseModel


class CreateUser(BaseModel):
    name: str
    email: str

class UserPublic(BaseModel):
    id: UUID
    name: str
    email: str