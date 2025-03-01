from dataclasses import dataclass


@dataclass
class URL:
    """Все пути используемые в тестах."""

    ADMIN_AUTH: str = '/api/v1/admin/auth/'
    ADMIN_LOGIN = '/api/v1/admin/auth/login'
    ADMIN_LOGOUT = '/api/v1/admin/auth/logout'
    USER_LOGIN = '/api/v1/auth/login'
    MESSAGE_FEED_URL = '/api/v1/Zorg/problems/1/thread'
    COMMENTS_URL = '/api/v1/Zorg/problems/1/1/comments'
    LIKE_URL = '/api/v1/Zorg/problems/1/1/comments/1/like'
    UNLIKE_URL = '/api/v1/Zorg/problems/1/1/comments/1/unlike'


TEXT_BAD_JSON: str = 'Ответ не соответствует ожиданию.'
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
