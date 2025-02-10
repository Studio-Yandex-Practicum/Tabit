from src.crud import CRUDBase
from src.users.models import UserTabit


class CRUDUsers(CRUDBase):
    """CRUD операций для модели пользователей."""
    pass


user_crud = CRUDUsers(UserTabit)
