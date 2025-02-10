from abc import abstractmethod
from typing import Generic, Protocol

from fastapi import Response
from fastapi_users import models
from fastapi_users.authentication.transport import Transport
from fastapi_users.manager import BaseUserManager


class StrategyT(Protocol, Generic[models.UP, models.ID]):
    """Протокол для аннотирования стратегии."""

    async def read_token(
        self,
        token: str | None,
        user_manager: BaseUserManager[models.UP, models.ID],
        distinguishing_feature: str | None,
    ) -> models.UP | None: ...  # pragma: no cover

    async def write_token(
        self, user: models.UP, is_access: bool | None
    ) -> str: ...  # pragma: no cover

    async def destroy_token(
        self, token: str, user: models.UP
    ) -> None: ...  # pragma: no cover


class TransportT(Transport):
    """Протокол для аннотирования транспорта."""

    @abstractmethod
    async def get_login_response_with_refresh(
        self, token_access: str, token_refresh: str
    ) -> Response: ...  # pragma: no cover
