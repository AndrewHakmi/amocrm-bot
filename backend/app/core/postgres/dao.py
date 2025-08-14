from app.core.postgres.base import BaseDAO
from app.core.postgres.models.users import User


class UserDAO(BaseDAO):
    model = User


