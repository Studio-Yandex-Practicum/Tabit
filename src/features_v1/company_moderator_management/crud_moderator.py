from src.core.crud_base import CRUDBase
from src.models import UserTabit


class CRUDModerator(CRUDBase):
    """CRUD операций для модели пользователей."""

    pass


moderator_crud = CRUDModerator(UserTabit)
