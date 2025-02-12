from src.crud import CRUDBase
from src.problems.models.message_models import MessageFeed


class CRUDMessageFeed(CRUDBase):
    """CRUD для операций с моделями тредов к проблемам."""

    pass


message_feed_crud = CRUDMessageFeed(MessageFeed)
