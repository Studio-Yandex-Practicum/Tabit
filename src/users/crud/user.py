from src.core.crud_base import CRUDBase
from src.models import UserTabit


class CRUDUsers(CRUDBase):
    """CRUD операций для модели пользователей."""

    pass


user_crud = CRUDUsers(UserTabit)
