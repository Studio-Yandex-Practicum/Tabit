from collections.abc import Sequence
from typing import Any, Optional
from uuid import UUID

import jwt
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi_users import FastAPIUsers, exceptions, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    Authenticator,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.authentication.authenticator import (
    EnabledBackendsDependency,
    name_to_strategy_variable_name,
    name_to_variable_name,
)
from fastapi_users.jwt import SecretType, decode_jwt, generate_jwt
from fastapi_users.manager import BaseUserManager, UserManagerDependency
from fastapi_users.schemas import model_dump
from makefun import with_signature
from pydantic import BaseModel

from src.api.v1.auth.managers import get_admin_manager, get_user_manager
from src.api.v1.auth.protocol import StrategyT, TransportT
from src.config import settings
from src.tabit_management.models import TabitAdminUser
from src.users.models import UserTabit


class TransportShema(BaseModel):
    """Схема для передачи JWT токена."""

    access_token: str
    refresh_token: str
    token_type: str


class TransportTabit(BearerTransport):
    """Транспорт для JWT сервиса Tabit."""

    async def get_login_response_with_refresh(
        self, access_token: str, refresh_token: str
    ) -> JSONResponse:
        """
        Подготовит ответ с токенами.
        :param access_token: строка содержащая access_token;
        :refresh_token: строка содержащая refresh_token.
        """
        bearer_response = TransportShema(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=settings.jwt_token_type,
        )
        return JSONResponse(model_dump(bearer_response))


# TODO: Нужно путь в константы определить, так, чтобы от эндпоинта собиралась.
transport_admin = TransportTabit(tokenUrl='/api/v1/admin/auth/login')
"""Транспорт JWT-токенов для администраторов сервиса Tabit."""

transport_user = TransportTabit(tokenUrl='/api/v1/auth/login')
"""Транспорт JWT-токенов для пользователей сервиса Tabit."""


class AuthenticationBackendTabit(AuthenticationBackend):
    """Сочетание способа аутентификации и стратегии сервиса Tabit."""

    transport: TransportT

    async def login_with_refresh(
        self, strategy: StrategyT[models.UP, models.ID], user: models.UP
    ) -> JSONResponse:
        """
        Передаст токены из стратегии в транспорт.
        :param strategy: стратегия JWT-токенов, по которой будут создаваться токены;
        :param user: экземпляр модели пользователей (запись из БД) для которого будут создаваться
            токены.
        """
        token_access = await strategy.write_token(user, is_access=True)
        token_refresh = await strategy.write_token(user, is_access=False)
        return await self.transport.get_login_response_with_refresh(token_access, token_refresh)


class JWTStrategyTabit(JWTStrategy):
    """JWT-стратегия сервиса Tabit."""

    def __init__(
        self,
        secret: SecretType,
        lifetime_seconds: int | None,
        lifetime_seconds_refresh: int | None,
        token_audience: list[str] = settings.jwt_token_audience,
        algorithm: str = settings.jwt_token_algorithm,
        public_key: SecretType | None = None,
    ):
        """
        :param secret: Постоянный секрет, который используется для кодирования токена;
        :param lifetime_seconds: Время жизни access-токена указывается в секундах;
        :param lifetime_seconds_refresh: Время жизни refresh-токена указывается в секундах;
        :param token_audience: Список допустимых аудиторий для токена JWT;
        :param algorithm: Алгоритм шифрования JWT;
        :param public_key: Если для алгоритма шифрования JWT требуется пара ключей вместо простого
            secret, ключ для расшифровки JWT может быть предоставлен здесь. Параметр secret всегда
            будет использоваться для шифрования JWT.
        """
        super().__init__(
            secret=secret,
            lifetime_seconds=lifetime_seconds,
            token_audience=token_audience,
            algorithm=algorithm,
            public_key=public_key,
        )
        self.lifetime_seconds_refresh = lifetime_seconds_refresh

    async def read_token(
        self,
        token: str | None,
        user_manager: BaseUserManager[models.UP, models.ID],
        distinguishing_feature: str | None = settings.jwt_distinguishing_feature_access_token,
    ) -> models.UP | None:
        """
        Проверит является ли переданный токен access-token или refresh-token и валиден ли он.
        Вернет экземпляр модели пользователя (запись из БД), которому был выдан этот токен.
        :param token: переданный токен;
        :param user_manager: менеджер управления пользователями;
        :param distinguishing_feature:
            - None - по умолчанию  - стандартный функционал библиотеки;
            - str - будет проверять в полезной нагрузке токена наличие ключа этой строки, при
            создании этот ключ разный для access или refresh токенов.
        """
        if token is None:
            return None
        try:
            data = decode_jwt(
                token, self.decode_key, self.token_audience, algorithms=[self.algorithm]
            )
            if distinguishing_feature and data.get(distinguishing_feature) is None:
                return None
            user_id = data.get('sub')
            if user_id is None:
                return None
        except jwt.PyJWTError:
            return None
        try:
            parsed_id = user_manager.parse_id(user_id)
            return await user_manager.get(parsed_id)
        except (exceptions.UserNotExists, exceptions.InvalidID):
            return None

    async def write_token(self, user: models.UP, is_access: bool | None = None) -> str:
        """
        Подготовит данные для создания access-token или refresh-token и, после его создания,
        вернет его.
        :param user: экземпляр модели пользователя (запись из БД);
        :param is_access: параметр-флаг, в зависимости от значения, "подмешает" в полезную
            нагрузку токена дополнительные данные, для идентификации роли токена:
            - None - по умолчанию - стандартный функционал библиотеки;
            - True - создаст access-token;
            - False - создаст refresh-token.
        """
        data = {
            'sub': str(user.id),
            'aud': self.token_audience,
        }
        lifetime_seconds = self.lifetime_seconds
        if is_access is not None:
            distinguishing_feature = (
                settings.jwt_distinguishing_feature_access_token
                if is_access
                else settings.jwt_distinguishing_feature_refresh_token
            )
            data[distinguishing_feature] = distinguishing_feature
            lifetime_seconds = self.lifetime_seconds_refresh
        return generate_jwt(data, self.encode_key, lifetime_seconds, algorithm=self.algorithm)


def get_jwt_strategy() -> JWTStrategy:
    """Вернет класс с настройками JWT-стратегии."""
    return JWTStrategyTabit(
        secret=settings.jwt_secret.get_secret_value(),
        lifetime_seconds=settings.jwt_lifetime_seconds,
        lifetime_seconds_refresh=settings.jwt_lifetime_seconds_refresh,
    )


jwt_auth_backend_admin = AuthenticationBackendTabit(
    name='jwt_admin',
    transport=transport_admin,
    get_strategy=get_jwt_strategy,
)
"""Экземпляр сочетания способа аутентификации и стратегии сервиса Tabit."""


jwt_auth_backend_user = AuthenticationBackendTabit(
    name='jwt_user',
    transport=transport_user,
    get_strategy=get_jwt_strategy,
)
"""Экземпляр сочетания способа аутентификации и стратегии сервиса Tabit."""


class AuthenticatorTabit(Authenticator):
    """
    Предоставляет вызываемые объекты зависимостей для получения аутентифицированного пользователя.
    """

    def current_user_refresh_token(
        self,
        optional: bool = False,
        active: bool = False,
        verified: bool = False,
        superuser: bool = False,
        get_enabled_backends: Optional[EnabledBackendsDependency[models.UP, models.ID]] = None,
    ):
        """
        Возвращает зависимость, вызываемую для получения текущего аутентифицированного
        пользователя и токена. Используется для проверки refresh-token.

        :param optional: Если значение "True", то значение "None" возвращается, если нет
        пользователя, прошедшего проверку подлинности или если оно не соответствует другим
        требованиям.
        В противном случае выдается сообщение "401 Unauthorized". По умолчанию используется
        значение "False".
        В противном случае генерируется исключение. По умолчанию используется значение `False`.
        :param active: Если указано значение "True", выдайте сообщение "401 Неавторизованный", если
        аутентифицированный пользователь неактивен. По умолчанию используется значение `False`.
        :param verified: Если значение "True", введите "401 Unauthorized", если
        аутентифицированный пользователь не подтвержден.
        По умолчанию используется значение `False`.
        :param superuser: Если значение "True", введите "403 запрещено", если
        прошедший проверку пользователь не является суперпользователем. По умолчанию используется
        значение `False`.
        :param get_enabled_backends: Необязательная зависимость, которую можно вызвать, возвращает
        список включенных серверных компонентов проверки подлинности.
        Полезно, если вы хотите динамически включить некоторые серверы аутентификации
        на основе внешней логики, например, конфигурации в базе данных.
        По умолчанию все указанные серверы аутентификации включены.
        Однако, пожалуйста, обратите внимание, что все серверные части будут отображаться в
        документации OpenAPI, поскольку FastAPI разрешает их статически.
        """
        signature = self._get_dependency_signature(get_enabled_backends)

        @with_signature(signature)
        async def current_user_token_refresh_dependency(*args: Any, **kwargs: Any):
            return await self._for_updating_tokens(
                *args,
                optional=optional,
                active=active,
                verified=verified,
                superuser=superuser,
                **kwargs,
            )

        return current_user_token_refresh_dependency

    async def _for_updating_tokens(
        self,
        *args,
        user_manager: BaseUserManager[models.UP, models.ID],
        optional: bool = False,
        active: bool = False,
        verified: bool = False,
        superuser: bool = False,
        **kwargs,
    ) -> tuple[Optional[models.UP], Optional[str]]:
        """
        Только для проверки refresh-token.

        За образец был взят метод _authenticate.
        Измен способ получения пользователя по токену.
        """
        user: Optional[models.UP] = None
        token: Optional[str] = None
        enabled_backends: Sequence[AuthenticationBackend[models.UP, models.ID]] = kwargs.get(
            'enabled_backends', self.backends
        )
        for backend in self.backends:
            if backend in enabled_backends:
                token = kwargs[name_to_variable_name(backend.name)]
                strategy: StrategyT[models.UP, models.ID] = kwargs[
                    name_to_strategy_variable_name(backend.name)
                ]
                if token is not None:
                    user = await strategy.read_token(
                        token,
                        user_manager,
                        settings.jwt_distinguishing_feature_refresh_token,
                    )
                    if user:
                        break
        status_code = status.HTTP_401_UNAUTHORIZED
        if user:
            status_code = status.HTTP_403_FORBIDDEN
            if active and not user.is_active:
                status_code = status.HTTP_401_UNAUTHORIZED
                user = None
            elif verified and not user.is_verified or superuser and not user.is_superuser:
                user = None
        if not user and not optional:
            raise HTTPException(status_code=status_code)
        return user, token


class FastAPIUsersTabit(FastAPIUsers[models.UP, models.ID]):
    """Основной объект, который связывает воедино компонент для аутентификации пользователей."""

    authenticator: AuthenticatorTabit

    def __init__(
        self,
        get_user_manager: UserManagerDependency[models.UP, models.ID],
        auth_backends: Sequence[AuthenticationBackend[models.UP, models.ID]],
    ):
        self.authenticator = AuthenticatorTabit(auth_backends, get_user_manager)
        self.get_user_manager = get_user_manager
        self.current_user = self.authenticator.current_user
        self.current_user_token = self.authenticator.current_user_token
        self.current_user_refresh_token = self.authenticator.current_user_refresh_token


tabit_admin = FastAPIUsersTabit[TabitAdminUser, UUID](get_admin_manager, [jwt_auth_backend_admin])
"""
Основной объект, который связывает воедино компонент для аутентификации пользователей для
администраторов сервиса Tabit.
"""

tabit_user = FastAPIUsersTabit[UserTabit, UUID](get_user_manager, [jwt_auth_backend_user])
"""
Основной объект, который связывает воедино компонент для аутентификации пользователей для
пользователей сервиса Tabit.
"""
