from src.crud.crud_base import CRUDBase
from src.models import CompanyUser


class CRUDUsers(CRUDBase):
    """CRUD операций для модели пользователей."""

    pass


user_crud = CRUDUsers(CompanyUser)
