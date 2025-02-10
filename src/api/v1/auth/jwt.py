from abc import abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import UUID

import jwt
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, Authenticator
from fastapi import Response
from fastapi.responses import JSONResponse
from fastapi_users import exceptions, models
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.authentication.strategy import Strategy
from fastapi_users.authentication.transport import Transport
from fastapi_users.jwt import SecretType, decode_jwt, generate_jwt, _get_secret_value
from fastapi_users.schemas import model_dump
from pydantic import BaseModel
from fastapi_users.manager import BaseUserManager
from fastapi import Depends, HTTPException, status

from src.config import settings
from src.api.v1.auth.protocol import StrategyT, TransportT
from src.tabit_management.models import TabitAdminUser
from src.users.models import UserTabit
from src.api.v1.auth.managers import get_admin_manager, get_user_manager

TOKEN_TYPE: str = 'bearer'
ALGORITHM: str = 'HS256'
TOKEN_AUDIENCE: list[str] = ['fastapi-users:auth']


class TransportShema(BaseModel):
    """Схема для передачи JWT токена."""

    access_token: str
    refresh_token: str
    token_type: str


class TransportTabit(BearerTransport):
    """Транспорт для JWT сервиса Tabit."""

    async def get_login_response_with_refresh(
        self, access_token: str, refresh_token: str
    ) -> Response:
        """Подготовит ответ с токенами."""
        bearer_response = TransportShema(
            access_token=access_token, refresh_token=refresh_token, token_type=TOKEN_TYPE
        )
        return JSONResponse(model_dump(bearer_response))


# TODO: Нужно путь в константы определить, так, чтобы от эндпоинта собиралась.
transport = TransportTabit(tokenUrl='/api/v1/admin/auth/login')


DISTINGUISHING_FEATURE_ACCESS = 'access'
DISTINGUISHING_FEATURE_REFRESH = 'refresh'


class AuthenticationBackendTabit(AuthenticationBackend):
    """Сочетание способа аутентификации и стратегии сервиса Tabit."""

    transport: TransportT

    async def login_with_refresh(
        self, strategy: StrategyT[models.UP, models.ID], user: models.UP
    ) -> Response:
        """Передаст токены из стратегии в транспорт."""
        token_access = await strategy.write_token(user, is_access=True)
        token_refresh = await strategy.write_token(user, is_access=False)
        return await self.transport.get_login_response_with_refresh(token_access, token_refresh)

    async def read_refresh_token(self, strategy: StrategyT[models.UP, models.ID]):
        pass


class JWTStrategyTabit(JWTStrategy):
    """JWT-стратегия сервиса Tabit."""

    def __init__(
        self,
        secret: SecretType,
        lifetime_seconds: int | None,
        lifetime_seconds_refresh: int | None,
        token_audience: list[str] = TOKEN_AUDIENCE,
        algorithm: str = ALGORITHM,
        public_key: SecretType | None = None,
    ):
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
        distinguishing_feature: str | None = DISTINGUISHING_FEATURE_ACCESS,
    ) -> models.UP | None:
        """Проверит является ли переданный токен access-token или refresh-token и валиден ли он."""
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
        param is_access: По умолчанию None - стандартный функционал библиотеки,
            True - создаст access-token, False - refresh-token
        """
        data = {
            'sub': str(user.id),
            'aud': self.token_audience,
        }
        lifetime_seconds = self.lifetime_seconds
        if is_access is not None:
            distinguishing_feature = (
                DISTINGUISHING_FEATURE_ACCESS if is_access else DISTINGUISHING_FEATURE_REFRESH
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


jwt_auth_backend = AuthenticationBackendTabit(
    name='jwt_2',
    transport=transport,
    get_strategy=get_jwt_strategy,
)


from collections.abc import Sequence
from fastapi_users.authentication.authenticator import name_to_variable_name, name_to_strategy_variable_name, EnabledBackendsDependency
from makefun import with_signature


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
        get_enabled_backends: Optional[
            EnabledBackendsDependency[models.UP, models.ID]
        ] = None,
    ):
        """
        Return a dependency callable to retrieve currently authenticated user and token.

        :param optional: If `True`, `None` is returned if there is no authenticated user
        or if it doesn't pass the other requirements.
        Otherwise, throw `401 Unauthorized`. Defaults to `False`.
        Otherwise, an exception is raised. Defaults to `False`.
        :param active: If `True`, throw `401 Unauthorized` if
        the authenticated user is inactive. Defaults to `False`.
        :param verified: If `True`, throw `401 Unauthorized` if
        the authenticated user is not verified. Defaults to `False`.
        :param superuser: If `True`, throw `403 Forbidden` if
        the authenticated user is not a superuser. Defaults to `False`.
        :param get_enabled_backends: Optional dependency callable returning
        a list of enabled authentication backends.
        Useful if you want to dynamically enable some authentication backends
        based on external logic, like a configuration in database.
        By default, all specified authentication backends are enabled.
        Please not however that every backends will appear in the OpenAPI documentation,
        as FastAPI resolves it statically.
        """
        signature = self._get_dependency_signature(get_enabled_backends)

        @with_signature(signature)
        async def current_user_token_refresh_dependency(*args: Any, **kwargs: Any):
            return await self._updating_tokens(
                *args,
                optional=optional,
                active=active,
                verified=verified,
                superuser=superuser,
                **kwargs,
            )

        return current_user_token_refresh_dependency

    async def _updating_tokens(
        self,
        *args,
        user_manager: BaseUserManager[models.UP, models.ID],
        optional: bool = False,
        active: bool = False,
        verified: bool = False,
        superuser: bool = False,
        **kwargs,
    ) -> tuple[Optional[models.UP], Optional[str]]:
        user: Optional[models.UP] = None
        token: Optional[str] = None
        enabled_backends: Sequence[AuthenticationBackend[models.UP, models.ID]] = (
            kwargs.get("enabled_backends", self.backends)
        )
        for backend in self.backends:
            if backend in enabled_backends:
                token = kwargs[name_to_variable_name(backend.name)]
                strategy: StrategyT[models.UP, models.ID] = kwargs[
                    name_to_strategy_variable_name(backend.name)
                ]
                if token is not None:
                    user = await strategy.read_token(
                        token, user_manager, DISTINGUISHING_FEATURE_REFRESH
                    )
                    if user:
                        break
        status_code = status.HTTP_401_UNAUTHORIZED
        if user:
            status_code = status.HTTP_403_FORBIDDEN
            if active and not user.is_active:
                status_code = status.HTTP_401_UNAUTHORIZED
                user = None
            elif (
                verified and not user.is_verified or superuser and not user.is_superuser
            ):
                user = None
        if not user and not optional:
            raise HTTPException(status_code=status_code)
        return user, token

from fastapi_users.manager import UserManagerDependency


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


tabit_admin = FastAPIUsersTabit[TabitAdminUser, UUID](get_admin_manager, [jwt_auth_backend])
tabit_users = FastAPIUsersTabit[UserTabit, UUID](get_user_manager, [jwt_auth_backend])
