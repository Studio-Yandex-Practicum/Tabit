from src.crud import CRUDBase
from src.tabit_management.models import TabitAdminUser


class CRUDAdminUser(CRUDBase):
    """CRUD операций для моделей администраторов сервиса Табит."""

    pass


admin_crud = CRUDAdminUser(TabitAdminUser)
