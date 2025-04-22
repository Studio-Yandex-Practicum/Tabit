from uuid import UUID

from fastapi import HTTPException, status
from fastapi_users.exceptions import InvalidPasswordException, UserAlreadyExists, UserNotExists
from fastapi_users.manager import BaseUserManager
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import CRUDBase, UserCreateMixin
from src.crud.constants import (
    ERROR_INVALID_PASSWORD,
    ERROR_USER_ALREADY_EXISTS,
    ERROR_USER_NOT_EXISTS,
)
from src.models import CompanyUser
from src.schemas import (
    CompanyAdminCreateSchema,
    CompanyAdminPatchSchema,
    CompanyAdminPutSchema,
)


class CRUDModeratorUser(UserCreateMixin, CRUDBase):
    """CRUD операций для моделей администраторов сервиса Табит."""

    async def get_by_telegram_username(
        self, username: str, session: AsyncSession
    ) -> CompanyUser | None:
        """
        Функция, возвращающая объект пользователя CompanyUser по переданному telegram_username,
        или же возвращающая значение None, если пользователь не обнаружен.

        Параметры:
            username: переданное значение telegram_username, по которому будет происходить поиск;
            session: асинхронная сессия SQLAlchemy;
        """
        user = await session.execute(
            select(self.model).where(self.model.telegram_username == username)
        )
        return user.scalars().first()

    async def create(
        self,
        create_data: CompanyAdminCreateSchema,
        user_manager: BaseUserManager,
    ) -> CompanyUser:
        """
        Переопределённый метод create от CRUDBase. Возвращает созданный объект UserTabit.
        В случае возникновения ошибок, выбрасывает исключения.

        Параметры:
            create_data: Валидированные данные схемы CompanyAdminCreateSchema,
            для создания админа компании;
            user_manager - менеджер пользователей.
        """
        try:
            created_admin_user = await user_manager.create(create_data)
        except UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ERROR_USER_ALREADY_EXISTS
            )
        except InvalidPasswordException:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ERROR_INVALID_PASSWORD
            )
        return created_admin_user

    async def update(
        self,
        user_id: UUID,
        update_data: CompanyAdminPatchSchema | CompanyAdminPutSchema,
        user_manager: BaseUserManager,
    ) -> CompanyUser:
        """
        Переопределённый метод update от CRUDBase. Функция обновляет данные админа от компании.

        Получает объект пользователя по UUID, обновляет его данные в БД и возвращает его.
        Параметры:
            user_id - UUID пользователя;
            update_date: объект схемы с данными для обновления;
            user_manager: менеджер пользователей.
        """
        try:
            admin_user = await user_manager.get(user_id)
            if (
                update_data.current_department_id is not None
                and admin_user.current_department_id != update_data.current_department_id
            ):
                update_data.previous_department_id = admin_user.current_department_id
            else:
                update_data.previous_department_id = admin_user.previous_department_id
            admin_user = await user_manager.update(update_data, admin_user)
        except UserNotExists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_USER_NOT_EXISTS
            )
        except UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ERROR_USER_ALREADY_EXISTS
            )
        except InvalidPasswordException:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ERROR_INVALID_PASSWORD
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


moderator_crud = CRUDModeratorUser(CompanyUser)
