from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.constants import (
    TEXT_ERROR_SERVER_CREATE,
    TEXT_ERROR_SERVER_CREATE_LOG,
    TEXT_ERROR_SERVER_DELETE,
    TEXT_ERROR_SERVER_DELETE_LOG,
    TEXT_ERROR_UNIQUE,
    TEXT_ERROR_UNIQUE_CREATE_LOG,
)
from src.logger import logger
from src.problems.models import AssociationUserComment


class CRUDAssociationUserComment:
    model = AssociationUserComment

    async def get(
        self, comment_id: int, user_id: UUID, session: AsyncSession
    ) -> AssociationUserComment | None:
        user_comment_association = await session.execute(
            select(self.model).where(
                and_(self.model.left_id == user_id, self.model.right_id == comment_id)
            )
        )
        return user_comment_association.scalar_one_or_none()

    async def create(self, comment_id: int, user_id: UUID, session: AsyncSession):
        user_comment_association = self.model(left_id=user_id, right_id=comment_id)
        try:
            session.add(user_comment_association)
            await session.commit()
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

    async def remove(self, comment_id: int, user_id: UUID, session: AsyncSession):
        user_comment_association = self.get(comment_id, user_id, session)
        try:
            await session.delete(user_comment_association)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f'{TEXT_ERROR_SERVER_DELETE_LOG} {self.model.__name__}: {e}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=TEXT_ERROR_SERVER_DELETE,
            )


user_comment_association_crud = CRUDAssociationUserComment()
