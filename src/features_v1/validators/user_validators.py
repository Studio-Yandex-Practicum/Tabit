from fastapi import Depends, HTTPException, status
from fastapi_users.exceptions import InvalidPasswordException
from fastapi_users.manager import BaseUserManager
from sqlalchemy import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth.managers import get_user_manager
from src.crud import moderator_crud, user_crud
from src.features_v1.constants import TextError
from src.schemas import UserCreateSchema


class BaseUserValidator:
    """
    Базовый класс для валидации, связанной с пользователями.

    Назначение:
        Инкапсулирует общие методы проверки, такие как:
        - проверка существования пользователя по email;
        - валидация пароля пользователя;
        - проверка telegram_username;
        - получение пользователя по UUID.

    Преимущества:
        - Повышает читаемость и повторное использование кода.
        - Избегает дублирования логики валидации в разных функциях/хендлерах.
        - Упрощает тестирование и расширение функциональности валидаторов.
        - Централизует зависимости (например, `session`, `user_manager`) и делает их явными.

    Используется:
        В функциях валидации, зависящих от `user_manager` или `session`, для чистого и
        предсказуемого взаимодействия с внешними ресурсами (БД, менеджерами).
    """

    def __init__(
        self, session: AsyncSession | None = None, user_manager: BaseUserManager | None = None
    ):
        self.session = session
        self.user_manager = user_manager

    async def check_user_exists_by_email(self, email: str) -> bool:
        if not self.user_manager:
            raise ValueError('user_manager is required')
        user = await self.user_manager.user_db.get_by_email(email)
        return user is not None

    async def check_user_password_valid(self, password: str, user_data: UserCreateSchema) -> None:
        if not self.user_manager:
            raise ValueError('user_manager is required')
        await self.user_manager.validate_password(password, user_data)

    async def check_telegram_username_exists(self, username: str) -> bool:
        if not self.session:
            raise ValueError('session is required')
        return await moderator_crud.get_by_telegram_username(username, self.session) is not None

    async def get_user_by_uuid(self, uuid: UUID):
        if not self.session:
            raise ValueError('session is required')
        return await user_crud.get(self.session, uuid)


async def validate_user_not_exists(
    user_data: UserCreateSchema,
    user_manager: BaseUserManager = Depends(get_user_manager),
) -> None:
    """
    Проверяет, что пользователь с таким email не существует.
    Args:
        user_data (UserCreateSchema): данные пользователя.
        user_manager (BaseUserManager): менеджер для пользователя.
    Raises:
        HTTPException: Если пользователь с таким email уже существует,
                        возвращает ошибку 400 (BAD REQUEST).
    """
    validator = BaseUserValidator(user_manager=user_manager)
    if user_data.email and await validator.check_user_exists_by_email(user_data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=TextError.EXISTS_EMAIL)


async def validate_password(
    user_data: UserCreateSchema,
    user_manager: BaseUserManager = Depends(get_user_manager),
) -> None:
    """
    Проверяет, что пароль соответствует требованиям.
    Args:
        user_data (UserCreateSchema): данные пользователя.
        user_manager (BaseUserManager): менеджер для пользователя.
    Raises:
        HTTPException: Если пароль не соответствует требованиям,
                        возвращает ошибку 400 (BAD REQUEST).
    """
    validator = BaseUserValidator(user_manager=user_manager)
    if user_data.password:
        try:
            await validator.check_user_password_valid(user_data.password, user_data)
        except InvalidPasswordException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=TextError.INVALID_PASSWORD
            )


async def check_telegram_username_for_duplicates(username: str, session: AsyncSession) -> None:
    """
    Функция проверяет, что в БД не существует пользователя с переданным telegram_username.
    В случае, если пользователь существует, то выбрасывается ошибка HTTP 400.
    Параметры:
        username: telegram_username, переданный в запросе к API;
        session: асинхронная сессия SQLAlchemy;
    """
    validator = BaseUserValidator(session=session)
    if username and await validator.check_telegram_username_exists(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=TextError.INVALID_TELEGRAM_USERNAME
        )


async def validate_field_members(
    session: AsyncSession,
    uuid_members: list[UUID] | None,
    company_id: int | None = None,
) -> None:
    """
    Проверит переданный список uuid пользователей на корректность uuid
    и принадлежность пользователей к переданной компании.

    Параметры
        session: Асинхронная сессия SQLAlchemy;
        uuid_members: список uuid пользователей;
        company_id: число - id компании из которой пользователи.
    """
    if not uuid_members:
        return
    validator = BaseUserValidator(session=session)
    for uuid in uuid_members:
        user = await validator.get_user_by_uuid(uuid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=TextError.UUID_INVALID.format(uuid),
            )
        if company_id is not None and company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=TextError.USER_NOT_FROM_COMPANY.format(uuid),
            )
