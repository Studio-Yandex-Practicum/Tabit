from uuid import UUID

from fastapi import HTTPException, status
from fastapi_users.exceptions import InvalidPasswordException, UserAlreadyExists, UserNotExists
from fastapi_users.manager import BaseUserManager
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import CRUDBase, UserCreateMixin
from src.crud.constants import TextErrorConstants
from src.models import CompanyUser
from src.schemas import (
    CompanyAdminCreateSchema,
    CompanyAdminPatchSchema,
    CompanyAdminPutSchema,
)


class CRUDModeratorUser(UserCreateMixin, CRUDBase):
    """CRUD операций для моделей модераторов компаний."""

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

    async def get_by_email(self, session: AsyncSession, email: str) -> CompanyUser | None:
        """Получает модератора по email"""
        result = await session.execute(select(self.model).where(self.model.email == email))
        return result.scalars().first()

    async def get_by_id(self, session: AsyncSession, user_id: str) -> CompanyUser | None:
        """Получает модератора по ID"""
        result = await session.execute(select(self.model).where(self.model.id == user_id))
        return result.scalars().first()

    async def create_password_reset_token(self, session: AsyncSession, email: str) -> str:
        """Создает токен для восстановления пароля используя JWT"""
        # Получаем модератора
        user = await self.get_by_email(session, email)
        if not user:
            raise ValueError('Модератор не найден')

        # Проверяем, что это действительно модератор
        from src.models import CompanyUserRole

        if user.role != CompanyUserRole.MODERATOR:
            raise ValueError('Пользователь не является модератором')

        # Используем JWT стратегию для генерации токена
        from src.core.auth.jwt import get_jwt_strategy

        jwt_strategy = get_jwt_strategy()
        token = await jwt_strategy.generate_password_reset_token(str(user.id), email)

        return token

    async def verify_reset_token(self, session: AsyncSession, token: str) -> bool:
        """Проверяет токен восстановления пароля используя JWT"""
        try:
            # Используем JWT стратегию для проверки токена
            from src.core.auth.jwt import get_jwt_strategy

            jwt_strategy = get_jwt_strategy()
            payload = await jwt_strategy.verify_password_reset_token(token)

            # Проверяем существование модератора
            user = await self.get_by_id(session, payload['sub'])
            if not user:
                return False

            # Проверяем, что это действительно модератор
            from src.models import CompanyUserRole

            return user.role == CompanyUserRole.MODERATOR

        except (ValueError, KeyError):
            return False

    async def reset_password_with_token(
        self, session: AsyncSession, token: str, new_password: str
    ) -> bool:
        """Сбрасывает пароль с использованием JWT токена"""
        try:
            # Проверяем токен и получаем payload
            from src.core.auth.jwt import get_jwt_strategy

            jwt_strategy = get_jwt_strategy()
            payload = await jwt_strategy.verify_password_reset_token(token)

            # Получаем модератора
            user = await self.get_by_id(session, payload['sub'])
            if not user:
                return False

            # Проверяем, что это действительно модератор
            from src.models import CompanyUserRole

            if user.role != CompanyUserRole.MODERATOR:
                return False

            # Обновляем пароль используя JWT стратегию
            hashed_password = jwt_strategy.password_helper.hash(new_password)
            user.hashed_password = hashed_password

            await session.commit()
            return True

        except ValueError:
            return False

    async def reset_password_by_admin(
        self, session: AsyncSession, user_id: UUID, new_password: str
    ) -> bool:
        """Принудительный сброс пароля администратором"""
        try:
            user = await self.get_or_404(session, user_id)

            # Проверяем, что это действительно модератор
            from src.models import CompanyUserRole

            if user.role != CompanyUserRole.MODERATOR:
                return False

            # Хешируем новый пароль
            from fastapi_users.password import PasswordHelper

            password_helper = PasswordHelper()
            hashed_password = password_helper.hash(new_password)

            # Обновляем пароль
            user.hashed_password = hashed_password
            session.add(user)
            await session.commit()

            return True

        except Exception as e:
            await session.rollback()
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f'Ошибка при сбросе пароля модератора: {e}')
            return False

    async def verify_password(self, session: AsyncSession, user_id: UUID, password: str) -> bool:
        """Проверка текущего пароля модератора"""
        try:
            user = await self.get_or_404(session, user_id)

            # Проверяем, что это действительно модератор
            from src.models import CompanyUserRole

            if user.role != CompanyUserRole.MODERATOR:
                return False

            # Проверяем, что у модератора есть хешированный пароль
            if not user.hashed_password:
                import logging

                logger = logging.getLogger(__name__)
                logger.warning('У модератора нет хешированного пароля')
                return False

            # Используем тот же PasswordHelper, что и в менеджерах
            from fastapi_users.password import PasswordHelper

            password_helper = PasswordHelper()

            try:
                # Проверяем пароль используя правильный метод
                is_valid, _ = password_helper.verify_and_update(password, user.hashed_password)
                import logging

                logger = logging.getLogger(__name__)
                logger.debug(f'Проверка пароля для модератора {user_id}: {is_valid}')
                return is_valid

            except Exception as verify_error:
                import logging

                logger = logging.getLogger(__name__)
                logger.error(f'Ошибка при проверке пароля модератора: {verify_error}')
                return False

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f'Ошибка при проверке пароля модератора: {e}')
            return False

    async def change_password(
        self, session: AsyncSession, user_id: UUID, new_password: str
    ) -> bool:
        """Смена пароля модератором"""
        try:
            import logging

            logger = logging.getLogger(__name__)
            logger.info(f'Начинаем смену пароля для модератора {user_id}')
            user = await self.get_or_404(session, user_id)
            logger.debug(f'Модератор найден: {user.id}')

            # Проверяем, что это действительно модератор
            from src.models import CompanyUserRole

            if user.role != CompanyUserRole.MODERATOR:
                logger.warning(f'Пользователь {user_id} не является модератором')
                return False

            # Используем тот же PasswordHelper, что и в менеджерах
            from fastapi_users.password import PasswordHelper

            password_helper = PasswordHelper()
            hashed_password = password_helper.hash(new_password)
            logger.debug(f'Новый хеш создан: {hashed_password[:20]}...')

            user.hashed_password = hashed_password
            session.add(user)
            logger.debug('Модератор добавлен в сессию')

            await session.commit()
            logger.info('Транзакция зафиксирована')

            return True

        except Exception as e:
            await session.rollback()
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f'Ошибка при смене пароля модератора: {e}')
            logger.error(f'Тип ошибки: {type(e)}')
            import traceback

            logger.error(f'Traceback: {traceback.format_exc()}')
            return False

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
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=TextErrorConstants.USER_ALREADY_EXISTS,
            )
        except InvalidPasswordException:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=TextErrorConstants.INVALID_PASSWORD,
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
                status_code=status.HTTP_404_NOT_FOUND, detail=TextErrorConstants.USER_NOT_EXISTS
            )
        except UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=TextErrorConstants.USER_ALREADY_EXISTS,
            )
        except InvalidPasswordException:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=TextErrorConstants.INVALID_PASSWORD,
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
                status_code=status.HTTP_404_NOT_FOUND, detail=TextErrorConstants.USER_NOT_EXISTS
            )


moderator_crud = CRUDModeratorUser(CompanyUser)
