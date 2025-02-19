from typing import Any, Optional
from uuid import UUID

from fastapi import HTTPException, status
from fastapi_users.exceptions import InvalidPasswordException, UserAlreadyExists, UserNotExists
from fastapi_users.manager import BaseUserManager
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.constants import DEFAULT_LIMIT, DEFAULT_SKIP
from src.crud import CRUDBase, UserCreateMixin
from src.logger import logger
from src.tabit_management.constants import (
    ERROR_INTERNAL_SERVER,
    ERROR_INVALID_PASSWORD,
    ERROR_INVALID_TELEGRAM_USERNAME,
    ERROR_USER_ALREADY_EXISTS,
    ERROR_USER_NOT_EXISTS,
)
from src.tabit_management.schemas.admin_company import (
    CompanyAdminCreateSchema,
    CompanyAdminUpdateSchema,
)
from src.users.models import UserTabit


class CRUDAdminUser(UserCreateMixin, CRUDBase):
    """CRUD операций для моделей администраторов сервиса Табит."""

    async def check_telegram_username_for_duplicates(
        self, username: str, session: AsyncSession
    ) -> None:
        """
        Функция проверяет, что в БД не существует пользователя с переданным telegram_username.
        В случае, если пользователь существует, то выбрасывается ошибка HTTP 400.

        Параметры:
            username: telegram_username, переданный в запросе к API;
            session: асинхронная сессия SQLAlchemy;
        """
        if username:
            if await self.get_by_telegram_username(username, session):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_INVALID_TELEGRAM_USERNAME
                )

    async def get_multi(
        self,
        session: AsyncSession,
        skip: int = DEFAULT_SKIP,
        limit: int = DEFAULT_LIMIT,
        filters: Optional[dict[str, Any]] = None,
        order_by: list[str] | None = None,
    ) -> list[UserTabit]:
        """
        Переопределённый метод get_multi от CRUDBase. Возвращает список объектов UserTabit.
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
            logger.error(f'Эндпоинт gget_all_staff, ошибка бд: {error}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=ERROR_INTERNAL_SERVER
            )
        except Exception as error:
            logger.error(f'Эндпоинт get_all_staff, ошибка: {error}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=ERROR_INTERNAL_SERVER
            )

    async def get_by_telegram_username(
        self, username: str, session: AsyncSession
    ) -> UserTabit | None:
        """
        Функция, возвращающая объект пользователя UserTabit по переданному telegram_username,
        или же возвращающая значение None, если пользователь не обнаружен.

        Параметры:
            username: переданное значение telegram_username, по которому будет происходить поиск;
            session: асинхронная сессия SQLAlchemy;
        """
        user = await session.execute(
            select(self.model).where(self.model.telegram_username == username)
        )
        return user.scalars().first()

    async def get_or_404(self, user_id: UUID, user_manager: BaseUserManager) -> UserTabit:
        """
        Переопределённый метод get_or_404 от CRUDBase. Возвращает найденный объект UserTabit.
        В случае, если объект не был найден, выбрасывается исключение HTTP 404.

        Параметры:
            user_id - UUID пользователя;
            user_manager - менеджер пользователей
        """
        try:
            admin_user = await user_manager.get(user_id)
        except UserNotExists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_USER_NOT_EXISTS
            )
        return admin_user

    async def create(
        self,
        session: AsyncSession,
        create_data: CompanyAdminCreateSchema,
        user_manager: BaseUserManager,
    ) -> UserTabit:
        """
        Переопределённый метод create от CRUDBase. Возвращает созданный объект UserTabit.
        В случае возникновения ошибок, выбрасывает исключения.

        Параметры:
            session: асинхронная сессия SQLAlchemy;
            create_data: Валидированные данные схемы CompanyAdminCreateSchema,
            для создания админа компании;
            user_manager - менеджер пользователей.
        """
        await self.check_telegram_username_for_duplicates(create_data.telegram_username, session)
        try:
            created_admin_user = await user_manager.create(create_data)
        except UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_USER_ALREADY_EXISTS
            )
        except InvalidPasswordException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_INVALID_PASSWORD
            )
        return created_admin_user

    async def update(
        self,
        user_id: UUID,
        update_data: CompanyAdminUpdateSchema,
        session: AsyncSession,
        user_manager: BaseUserManager,
    ) -> UserTabit:
        """
        Переопределённый метод update от CRUDBase. Функция обновляет данные админа от компании.

        Получает объект пользователя по UUID, обновляет его данные в БД и возвращает его.
        Параметры:
            user_id - UUID пользователя;
            update_date: объект схемы с данными для обновления;
            session: асинхронная сессия SQLAlchemy;
            user_manager: менеджер пользователей.
        """
        await self.check_telegram_username_for_duplicates(update_data.telegram_username, session)
        try:
            admin_user = await user_manager.get(user_id)
            admin_user = await user_manager.update(update_data, admin_user)
        except UserNotExists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_USER_NOT_EXISTS
            )
        except UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_USER_ALREADY_EXISTS
            )
        except InvalidPasswordException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_INVALID_PASSWORD
            )
        return admin_user

    async def remove(self, user_id: UUID, user_manager: BaseUserManager) -> None:
        """
        Переопределённый метод remove от CRUDBase. Функция удалёет из БД запись об
        объекте UserTabit с переданным UUID.
        Если пользователь с указанным UUID не найден, то выбрасывается исключение HTTP 404.

        Параметры:
            user_id - UUID пользователя;
            user_manager: менеджер пользователей.
        """
        try:
            admin_user = await user_manager.get(user_id)
            await user_manager.delete(admin_user)
        except UserNotExists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_USER_NOT_EXISTS
            )


admin_user_crud = CRUDAdminUser(UserTabit)
