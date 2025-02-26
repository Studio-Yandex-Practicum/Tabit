from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.problems.models import AssociationUserComment


class CRUDAssociationUserComment:
    """CRUD для модели AssociationUserComment."""

    model = AssociationUserComment

    async def get(
        self, comment_id: int, user_id: UUID, session: AsyncSession
    ) -> AssociationUserComment | None:
        """
        Функция получает запись модели AssociationUserComment по указанным comment_id и user_id.
        Возвращает либо объект модели, либо None.

        Параметры:
            comment_id: id запрашиваемого комментария;
            user_id: UUID пользователя, сделавшего запрос;
            session: асинхронная сессия SQLAlchemy.
        """
        user_comment_obj = await session.execute(
            select(self.model).where(
                and_(self.model.left_id == user_id, self.model.right_id == comment_id)
            )
        )
        return user_comment_obj.scalar_one_or_none()

    async def create(self, comment_id: int, user_id: UUID, session: AsyncSession):
        """
        Функция создаёт запись о лайке комментария пользователем.

        Параметры:
            comment_id: id запрашиваемого комментария;
            user_id: UUID пользователя, сделавшего запрос;
            session: асинхронная сессия SQLAlchemy.
        """
        user_comment_obj = self.model(left_id=user_id, right_id=comment_id)
        session.add(user_comment_obj)

    async def remove(self, user_comment_obj: AssociationUserComment, session: AsyncSession):
        """
        Функция удаляет запись о лайке комментария пользователем.

        Параметры:
            user_comment_obj: объект модели AssociationUserComment;
            session: асинхронная сессия SQLAlchemy.
        """
        await session.delete(user_comment_obj)


user_comment_association_crud = CRUDAssociationUserComment()
