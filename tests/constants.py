from dataclasses import dataclass


@dataclass
class URL:
    """Все пути используемые в тестах."""

    ADMIN_AUTH: str = '/api/v1/admin/auth/'
    ADMIN_LOGIN: str = '/api/v1/admin/auth/login'
    ADMIN_LOGOUT: str = '/api/v1/admin/auth/logout'
    ADMIN_ME: str = '/api/v1/admin/auth/me'
    ADMIN_REFRESH: str = '/api/v1/admin/auth/refresh-token'
    USER_LOGIN: str = '/api/v1/auth/login'
    USER_LOGOUT: str = '/api/v1/auth/logout'
    USER_REFRESH: str = '/api/v1/auth/refresh-token'


GOOD_PASSWORD: str = 'string123STRING'
BAD_PASSWORD: tuple[str, ...] = (
    'string123STRING',
    'STRING123STRING',
    'stringSTRING',
    'string123string',
    '!string123STRING',
    's123S',
)
BAD_EMAIL: tuple[str, ...] = (
    'user@example.',
    'user@.com',
    '@example.com',
    'user@exa mple.com',
    'user@ex@ample.com',
)
