from src.crud import CRUDBase, UserCreateMixin
from src.models import TabitAdminUser


class CRUDAdminUser(UserCreateMixin, CRUDBase):
    """CRUD операций для моделей администраторов сервиса Табит."""

    pass


admin_user_crud = CRUDAdminUser(TabitAdminUser)
