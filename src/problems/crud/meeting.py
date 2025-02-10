from src.crud import CRUDBase
from src.problems.models import Meeting


class CRUDMeeting(CRUDBase):
    """CRUD операции для модели встречи."""

    pass


meeting_crud = CRUDMeeting(Meeting)
