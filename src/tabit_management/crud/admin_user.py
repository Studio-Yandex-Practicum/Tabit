from src.crud import CRUDBase
from src.tabit_management.models import TabitAdminUser


class CRUDAdminUser(CRUDBase):
    """CRUD операций для моделей администраторов сервиса Табит."""


admin_user_crud = CRUDAdminUser(TabitAdminUser)
