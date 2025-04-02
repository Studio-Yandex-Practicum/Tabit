from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import CRUDBase
from src.users.models import TagUser
from src.users.models.models import AssociationUserTags
from src.users.schemas.tag import TagUserCreateSchema, TagUserResponseSchema, TagUserUpdateSchema


class CRUDTags(CRUDBase):
    """CRUD операций для модели пользователей."""

    async def get_tags_by_company(
        self, session: AsyncSession, company_id: int
    ) -> list[TagUserResponseSchema]:
        """
        Получает все теги, принадлежащие конкретной компании.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            company_id: Уникальный идентификатор компании

        Returns:
            TagUserResponseSchema: Полученые тэги.
        """
        query = select(TagUser).where(TagUser.company_id == company_id)
        result = await session.execute(query)
        return result.scalars().all()

    async def create(
        self, session: AsyncSession, obj_in: TagUserCreateSchema, company_id: int
    ) -> TagUserResponseSchema:
        """
        Создаёт тэг и связывает его с пользователем.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            tag_data: Данные нового тэга.
            company_id: Уникальный идентификатор компании.

        Returns:
            TagUserResponseSchema: Созданный тэг.

        Raises:
            HTTPException: Если произошла ошибка при создании тэга.
        """
        tag = TagUser(name=obj_in.name, company_id=company_id)
        session.add(tag)
        await session.flush()
        association = AssociationUserTags(left_id=obj_in.user_id, right_id=tag.id)
        session.add(association)
        await session.commit()
        await session.refresh(tag)
        return TagUserResponseSchema.model_validate(tag)

    async def update(
        self, session: AsyncSession, tag: TagUser, obj_in: TagUserUpdateSchema
    ) -> TagUserResponseSchema:
        """
        Обновляет имя тэга, если он принадлежит указанной компании.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            tag_id: Уникальный идентификатор тэга.
            obj_in: Данные для обновления.
            company_id: Уникальный идентификатор компании.

        Returns:
            TagUserResponseSchema: Обновленный тэг.

        Raises:
            HTTPException: Если тэг не найден или не принадлежит компании.
        """
        return await super().update(session, tag, obj_in)

    async def delete_tag(self, session: AsyncSession, tag_id: int, company_id: int) -> None:
        """
        Удаляет тэг из базы данных по её ID.
        Перед удалением проверяет существование тэга.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            company_id: Уникальный идентификатор компании.
            tag_id: Уникальный идентификатор тэга.

        Returns:
            None
        """
        db_obj = await self.get_or_404(session, tag_id)
        await self.remove(session, db_obj)


tag_crud = CRUDTags(TagUser)
