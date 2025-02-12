from src.crud import CRUDBase
from src.problems.models.message_models import CommentFeed


class CRUDComment(CRUDBase):
    """CRUD для операций с моделями комментариев к тредам."""

    pass


comment_crud = CRUDComment(CommentFeed)
