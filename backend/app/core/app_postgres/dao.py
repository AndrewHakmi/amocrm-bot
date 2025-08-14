from backend.app.core.app_postgres.base import BaseDAO
from backend.app.models import User, Item


class UserDAO(BaseDAO):
    model = User

class ItemDAO(BaseDAO):
    model = Item