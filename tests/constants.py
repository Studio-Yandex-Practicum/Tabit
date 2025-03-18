import os
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv

from src.constants import TextError
from src.users.models.enum import RoleUserTabit

load_dotenv()


@dataclass
class TEST_DATABASE_URL:
    TEST_USER: str = os.getenv('TEST_POSTGRES_USER', 'test_user')
    TEST_PASSWORD: str = os.getenv('TEST_POSTGRES_PASSWORD', 'test_password')
    TEST_HOST: str = os.getenv('TEST_POSTGRES_HOST', 'localhost')
    TEST_PORT: int = int(os.getenv('TEST_POSTGRES_PORT', 5433))
    TEST_DBNAME: str = os.getenv('TEST_POSTGRES_DB', 'test_db')


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
    USER_ME: str = '/api/v1/auth/me'
    USER_REFRESH: str = '/api/v1/auth/refresh-token'
    COMPANIES_ENDPOINT: str = '/api/v1/admin/companies/'
    LICENSES_ENDPOINT: str = '/api/v1/admin/licenses/'
    MEETINGS_ENDPOINT: str = '/api/v1/{company_slug}/problems/{problem_id}/meetings'
    MEETINGS_SINGLE: str = '/api/v1/{company_slug}/problems/{problem_id}/meetings/{meeting_id}'


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
PAYLOAD_FOR_PATCH_USER: tuple[dict, ...] = (
    {
        'name': 'Модест',
        'surname': 'Староконь',
        'patronymic': 'Илларионович',
        'phone_number': '8 495 694-83-90',
        'birthday': '1999-05-14',
    },
    {
        'phone_number': '8 495 694-83-90',
        'surname': 'Староконь',
    },
    {
        'patronymic': 'Илларионович',
    },
)
PAYLOAD_FOR_PATCH_USER_EXTRA: dict = {
    'id': 1776,
    'email': 'illuminati@world.gov',
    'is_active': False,
    'is_superuser': True,
    'is_verified': False,
    'role': RoleUserTabit.ADMIN,
    'start_date_employment': '1776-05-01',
    'end_date_employment': '1776-05-01',
    'company_id': 1776,
    'current_department_id': 1776,
    'last_department_id': 1776,
    'department_transition_date': '1776-05-01',
    'employee_position': 'Минервал',
    'created_at': '1776-05-01 00:00:01.000 +0100',
    'updated_at': '1776-05-01 00:00:01.000 +0100',
}
MODERATOR_TELEGRAM: str = 'avadakedavra'
USER_TELEGRAM: str = 'expectopatronum'

IMAGE_BASE64_PNG: str = (
    'data:image/png;base64,'
    'iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAA'
    'AJcEhZcwAADsQAAA7EAZUrDhsAAAAWSURBVBhXY/jPAEIM/5ns7eyA1H8GADMUBbmnKLI7AAAAAElFTkSuQmCC'
)

IMAGE_BASE64_JPG: str = (
    'data:image/jpg;base64,'
    'iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAA'
    'JcEhZcwAADsQAAA7EAZUrDhsAAAAZSURBVBhXY2T4DwQMDAxMBw8dYmBgZGQAAEnjBkemLjB6AAAAAElFTkSuQmCC'
)

INVALID_IMAGE: tuple[tuple[Any, Any], ...] = (
    (
        1,
        [
            {
                'type': 'string_type',
                'loc': ['body', 'logo'],
                'msg': 'Input should be a valid string',
                'input': 1,
            }
        ],
    ),
    ('string', TextError.BASE64_TYPE),
    (
        f'{IMAGE_BASE64_PNG}b',
        TextError.BASE64_FATAL.format(
            image='logo',
            error_class='Error',
            error_text=(
                'Invalid base64-encoded string: number of data characters (173) '
                'cannot be 1 more than a multiple of 4'
            ),
        ),
    ),
)
