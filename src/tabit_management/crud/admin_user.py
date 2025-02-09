from src.crud import CRUDBase, UserCreateMixin
from src.tabit_management.models import TabitAdminUser


class CRUDAdminUser(UserCreateMixin, CRUDBase):
    """CRUD операций для моделей администраторов сервиса Табит."""

    pass


admin_crud = CRUDAdminUser(TabitAdminUser)
