from src.crud import CRUDBase, UserCreateMixin
from src.users.models import UserTabit


class CRUDAdminUser(UserCreateMixin, CRUDBase):
    """CRUD операций для моделей администраторов сервиса Табит."""

    pass


admin_user_crud = CRUDAdminUser(UserTabit)
