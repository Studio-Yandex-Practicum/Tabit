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
    COMPANIES_ENDPOINT: str = '/api/v1/admin/companies/'
    LICENSES_ENDPOINT: str = '/api/v1/admin/licenses/'


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
PAYLOAD_FOR_CREATE_ADMIN: tuple[dict, ...] = (
    {
        'patronymic': 'string',
        'phone_number': 'string',
        'email': 'user1@example.com',
        'password': GOOD_PASSWORD,
        'name': 'string',
        'surname': 'string',
    },
    {
        'phone_number': 'string',
        'email': 'user2@example.com',
        'password': GOOD_PASSWORD,
        'name': 'string',
        'surname': 'string',
    },
    {
        'patronymic': 'string',
        'email': 'user3@example.com',
        'password': GOOD_PASSWORD,
        'name': 'string',
        'surname': 'string',
    },
    {
        'email': 'user4@example.com',
        'password': GOOD_PASSWORD,
        'name': 'string',
        'surname': 'string',
    },
)
PAYLOAD_BAD_FOR_CREATE_ADMIN: tuple[dict, ...] = (
    {
        'email': 'user1@example.com',
        'password': GOOD_PASSWORD,
        'name': 'string',
    },
    {
        'email': 'user2@example.com',
        'password': GOOD_PASSWORD,
        'surname': 'string',
    },
    {
        'password': GOOD_PASSWORD,
        'name': 'string',
        'surname': 'string',
    },
    {
        'email': 'user4@example.com',
        'name': 'string',
        'surname': 'string',
    },
)
PAYLOAD_FOR_PATCH_ADMIN: tuple[dict, ...] = (
    {
        'patronymic': 'Императрица',
        'phone_number': '8 800 700-06-11',
        'name': 'Киширика',
        'surname': 'Киширису',
    },
    {
        'phone_number': '8 800 700-06-11',
        'surname': 'Киширису',
    },
    {
        'patronymic': 'Императрица',
    },
)

