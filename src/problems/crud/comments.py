from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.constants import (
    DEFAULT_AUTO_COMMIT,
    TEXT_ERROR_SERVER_CREATE,
    TEXT_ERROR_SERVER_CREATE_LOG,
    TEXT_ERROR_UNIQUE,
    TEXT_ERROR_UNIQUE_CREATE_LOG,
)
from src.crud import CRUDBase
from src.logger import logger
from src.problems.crud import user_comment_association_crud
from src.problems.models import AssociationUserComment, CommentFeed
from src.problems.schemas import CommentCreate


class CRUDComment(CRUDBase):
    """
    Переопределённый метод create для создания объектов MesageFeed в БД.
    Возвращает созданный объект из БД.

    Параметры:
        session: асинхронная сессия SQLAlchemy;
        obj_in: объект схемы с данными для создания коммментария;
        message_feed_id: id треда, в котором будет создан комментарий;
        user_id: UUID пользователя, который является создателем треда;
        auto_commit: константа для автокоммитов, по умолчанию - True.
    """

    async def create(
        self,
        session: AsyncSession,
        obj_in: CommentCreate,
        message_feed_id: int,
        user_id: int,
        auto_commit: bool = DEFAULT_AUTO_COMMIT,
    ) -> CommentFeed:
        """
        Переопределённый метод create для создания объектов CommentFeed в БД.
        Возвращает созданный объект из БД.

        Параметры:
            session: асинхронная сессия SQLAlchemy;
            obj_in: объект схемы с данными для создания комментария;
            message_feed_id: id треда, в котором будет создан комментарий;
            user_id: UUID пользователя, который является автором комментария;
            auto_commit: константа для автокоммитов, по умолчанию - True.
        """
        obj_data = obj_in.model_dump()
        obj_data['owner_id'] = user_id
        obj_data['message_id'] = message_feed_id
        db_obj = self.model(**obj_data)
        try:
            session.add(db_obj)
            if auto_commit:
                await session.commit()
                await session.refresh(db_obj)
        except IntegrityError as e:
            await session.rollback()
            logger.error(f'{TEXT_ERROR_UNIQUE_CREATE_LOG} {self.model.__name__}: {e}')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=TEXT_ERROR_UNIQUE,
            )
        except Exception as e:
            await session.rollback()
            logger.error(f'{TEXT_ERROR_SERVER_CREATE_LOG} {self.model.__name__}: {e}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=TEXT_ERROR_SERVER_CREATE,
            )
        return db_obj

    async def like(self, comment: CommentFeed, user_id: UUID, session: AsyncSession):
        """
        Функция для лайка комментариев.
        Создаёт запись о лайке в связанной таблице и увеличивает рейтинг на 1.

        Параметры:
            comment: объект модели CommentFeed;
            user_id: UUID пользователя, сделавшего запрос;
            session: асинхронная сессия SQLAlchemy.
        """
        try:
            await user_comment_association_crud.create(comment.id, user_id, session)
            comment.rating += 1
            session.add(comment)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f'{TEXT_ERROR_SERVER_CREATE_LOG} {self.model.__name__}: {e}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=TEXT_ERROR_SERVER_CREATE,
            )

    async def unlike(
        self, user_comment_obj: AssociationUserComment, comment: CommentFeed, session: AsyncSession
    ):
        """
        Функция для снятия лайка с комментариев.
        Удалёет запись о лайке в связанной таблице и уменьшает рейтинг на 1.

        Параметры:
            user_comment_obj: объект модели AssociationUserComment;
            comment: объект модели CommentFeed;
            session: асинхронная сессия SQLAlchemy.
        """
        try:
            await user_comment_association_crud.remove(user_comment_obj, session)
            comment.rating -= 1
            session.add(comment)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f'{TEXT_ERROR_SERVER_CREATE_LOG} {self.model.__name__}: {e}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=TEXT_ERROR_SERVER_CREATE,
            )


comment_crud = CRUDComment(CommentFeed)
