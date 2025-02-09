from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy

from src.config import settings

# TODO: Нужно путь в константы определить, так, чтобы от эндпоинта собиралась.
bearer_transport = BearerTransport(tokenUrl='/api/v1/admin/auth/login')


def get_jwt_strategy() -> JWTStrategy:
    """Вернет класс с настройками jwt-стратегии."""
    return JWTStrategy(
        secret=settings.jwt_secret.get_secret_value(),
        lifetime_seconds=settings.jwt_lifetime_seconds,
    )


jwt_auth_backend = AuthenticationBackend(
    name='jwt',
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
