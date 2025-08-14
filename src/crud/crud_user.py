import logging
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.core.auth.jwt import get_jwt_strategy
from src.crud.crud_base import CRUDBase
from src.models import CompanyUser, CompanyUserRole

logger = logging.getLogger(__name__)


class CRUDUsers(CRUDBase):
    """CRUD операций для модели пользователей."""

    async def is_user_moderator(
        self, session: AsyncSession, user_id: UUID, company_id: int
    ) -> bool:
        """
        Проверить, является ли пользователь модератором компании.

        Args:
            session: Асинхронная сессия SQLAlchemy
            user_id: ID пользователя
            company_id: ID компании

        Returns:
            bool: True если пользователь является модератором компании
        """
        result = await session.execute(
            select(CompanyUser).where(
                and_(
                    CompanyUser.id == user_id,
                    CompanyUser.company_id == company_id,
                    CompanyUser.role == CompanyUserRole.MODERATOR,
                )
            )
        )

        return result.scalar_one_or_none() is not None

    async def get_company_employee_count(self, session: AsyncSession, company_id: int) -> int:
        """
        Возвращает общее количество сотрудников определенной компании в таблице CompanyUser.
         Компания выбирается по ID "company_id".

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            company_id (int): ID Компании

        Returns:
            int: Общее количество сотрудников компании в таблице CompanyUser.
        """
        result = await session.execute(
            select(func.count())
            .select_from(CompanyUser)
            .where(
                CompanyUser.company_id == company_id, CompanyUser.role == CompanyUserRole.EMPLOYEE
            )
        )
        return result.scalar()

    async def get_company_admins_count(self, session: AsyncSession, company_id: int) -> int:
        """
        Возвращает общее количество админов определенной компании в таблице CompanyUser.
         Компания выбирается по ID "company_id".

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            company_id (int): ID Компании

        Returns:
            int: Общее количество админов компании в таблице CompanyUser.
        """
        result = await session.execute(
            select(func.count())
            .select_from(CompanyUser)
            .where(
                CompanyUser.company_id == company_id,
                CompanyUser.role == CompanyUserRole.MODERATOR,
            )
        )
        return result.scalar()

    async def get_by_email(self, session: AsyncSession, email: str) -> CompanyUser | None:
        """Получает пользователя по email"""
        result = await session.execute(select(self.model).where(self.model.email == email))
        return result.scalars().first()

    async def get_by_id(self, session: AsyncSession, user_id: str) -> CompanyUser | None:
        """Получает пользователя по ID"""
        result = await session.execute(select(self.model).where(self.model.id == user_id))
        return result.scalars().first()

    async def create_password_reset_token(self, session: AsyncSession, email: str) -> str:
        """Создает токен для восстановления пароля используя JWT"""
        # Получаем пользователя
        user = await self.get_by_email(session, email)
        if not user:
            raise ValueError('Пользователь не найден')

        # Используем JWT стратегию для генерации токена
        jwt_strategy = get_jwt_strategy()
        token = await jwt_strategy.generate_password_reset_token(str(user.id), email)

        return token

    async def verify_reset_token(self, session: AsyncSession, token: str) -> bool:
        """Проверяет токен восстановления пароля используя JWT"""
        try:
            # Используем JWT стратегию для проверки токена
            jwt_strategy = get_jwt_strategy()
            payload = await jwt_strategy.verify_password_reset_token(token)

            # Проверяем существование пользователя
            user = await self.get_by_id(session, payload['sub'])
            return user is not None

        except (ValueError, KeyError):
            return False

    async def reset_password_with_token(
        self, session: AsyncSession, token: str, new_password: str
    ) -> bool:
        """Сбрасывает пароль с использованием JWT токена"""
        try:
            # Проверяем токен и получаем payload
            jwt_strategy = get_jwt_strategy()
            payload = await jwt_strategy.verify_password_reset_token(token)

            # Получаем пользователя
            user = await self.get_by_id(session, payload['sub'])
            if not user:
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
            logger.error(f'Ошибка при сбросе пароля: {e}')
            return False

    def _hash_password(self, password: str) -> str:
        """Хеширует пароль используя JWT стратегию"""
        jwt_strategy = get_jwt_strategy()
        return jwt_strategy.password_helper.hash(password)

    async def verify_password(self, session: AsyncSession, user_id: UUID, password: str) -> bool:
        """Проверка текущего пароля пользователя"""
        try:
            user = await self.get_or_404(session, user_id)

            # Проверяем, что у пользователя есть хешированный пароль
            if not user.hashed_password:
                logger.warning('У пользователя нет хешированного пароля')
                return False

            # Используем тот же PasswordHelper, что и в менеджерах
            from fastapi_users.password import PasswordHelper

            password_helper = PasswordHelper()

            try:
                # Проверяем пароль используя правильный метод
                is_valid, _ = password_helper.verify_and_update(password, user.hashed_password)
                logger.debug(f'Проверка пароля для пользователя {user_id}: {is_valid}')
                return is_valid

            except Exception as verify_error:
                logger.error(f'Ошибка при проверке пароля: {verify_error}')
                return False

        except Exception as e:
            logger.error(f'Ошибка при проверке пароля: {e}')
            return False

    async def change_password(
        self, session: AsyncSession, user_id: UUID, new_password: str
    ) -> bool:
        """Смена пароля пользователем"""
        try:
            logger.info(f'Начинаем смену пароля для пользователя {user_id}')
            user = await self.get_or_404(session, user_id)
            logger.debug(f'Пользователь найден: {user.id}')

            # Используем тот же PasswordHelper, что и в менеджерах
            from fastapi_users.password import PasswordHelper

            password_helper = PasswordHelper()
            hashed_password = password_helper.hash(new_password)
            logger.debug(f'Новый хеш создан: {hashed_password[:20]}...')

            user.hashed_password = hashed_password
            session.add(user)
            logger.debug('Пользователь добавлен в сессию')

            await session.commit()
            logger.info('Транзакция зафиксирована')

            return True

        except Exception as e:
            await session.rollback()
            logger.error(f'Ошибка при смене пароля: {e}')
            logger.error(f'Тип ошибки: {type(e)}')
            import traceback

            logger.error(f'Traceback: {traceback.format_exc()}')
            return False

    async def debug_password_hash(self, session: AsyncSession, user_id: UUID) -> dict:
        """Диагностика хеша пароля пользователя"""
        try:
            user = await self.get_or_404(session, user_id)

            return {
                'user_id': str(user_id),
                'has_password': bool(user.hashed_password),
                'hash_length': len(user.hashed_password) if user.hashed_password else 0,
                'hash_prefix': user.hashed_password[:10] if user.hashed_password else None,
                'is_bcrypt_format': user.hashed_password.startswith('$2b$')
                if user.hashed_password
                else False,
            }

        except Exception as e:
            return {'error': str(e)}


user_crud = CRUDUsers(CompanyUser)
