from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config.logging import logger
from src.crud import CRUDBase
from src.crud.constants import Default, TextError
from src.models import MessageFeed
from src.schemas import MessageFeedCreate


class CRUDMessageFeed(CRUDBase):
    """CRUD для операций с моделями тредов к проблемам."""

    async def create(
        self,
        session: AsyncSession,
        obj_in: MessageFeedCreate,
        problem_id: int,
        user_id: int,
        auto_commit: bool = Default.AUTO_COMMIT,
    ) -> MessageFeed:
        """
        Переопределённый метод create для создания объектов MesageFeed в БД.
        Возвращает созданный объект из БД.

        Параметры:
            session: асинхронная сессия SQLAlchemy;
            obj_in: объект схемы с данными для создания треда;
            problem_id: id проблемы, для которой будет создан тред;
            user_id: UUID пользователя, который является создателем треда;
            auto_commit: константа для автокоммитов, по умолчанию - True.
        """
        obj_data = obj_in.model_dump()
        obj_data['owner_id'] = user_id
        obj_data['problem_id'] = problem_id
        db_obj = self.model(**obj_data)
        try:
            session.add(db_obj)
            if auto_commit:
                await session.commit()
                await session.refresh(db_obj)
        except IntegrityError as e:
            await session.rollback()
            logger.error(f'{TextError.CREATE_UNIQUE_LOG} {self.model.__name__}: {e}')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=TextError.UNIQUE,
            )
        except Exception as e:
            await session.rollback()
            logger.error(f'{TextError.CREATE_SERVER_LOG} {self.model.__name__}: {e}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=TextError.CREATE_SERVER,
            )
        return db_obj


message_feed_crud = CRUDMessageFeed(MessageFeed)
