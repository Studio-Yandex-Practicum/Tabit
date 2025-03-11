from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config.logging import logger
from src.core.crud_base import CRUDBase
from src.features_v1.tabit_admin_management.constants import (
    DEFAULT_LIMIT,
    DEFAULT_SKIP,
    ERROR_INTERNAL_SERVER,
)
from src.models import Company


class CRUDAdminCompany(CRUDBase):
    """CRUD операций для модели компании от лица админа."""

    async def get_multi(
        self,
        session: AsyncSession,
        skip: int = DEFAULT_SKIP,
        limit: int = DEFAULT_LIMIT,
        filters: Optional[dict[str, Any]] = None,
        order_by: list[str] | None = None,
    ) -> list[Company]:
        """
        Переопределённый метод get_multi от CRUDBase. Возвращает список объектов Company.
        В случае возникновения ошибок, выбрасывает исключения.

        Параметры:
            session: Асинхронная сессия SQLAlchemy.
            skip: Число записей для пропуска.
            limit: Максимальное число записей.
            filters: Словарь {имя_поля: значение} для фильтрации.
            order_by: Список полей для сортировки; '-' в начале для убывания.
        """
        try:
            return await super().get_multi(session, skip, limit, filters, order_by)
        except SQLAlchemyError as error:
            logger.error(f'Эндпоинт get_all_info, ошибка бд: {error}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=ERROR_INTERNAL_SERVER
            )
        except Exception as error:
            logger.error(f'Эндпоинт get_all_info, ошибка: {error}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=ERROR_INTERNAL_SERVER
            )


admin_company_crud = CRUDAdminCompany(Company)
