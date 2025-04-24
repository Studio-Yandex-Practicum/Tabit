"""Модуль содержит константы и настройки для тестирования API.

Включает в себя:
- Базовые константы (TextError, Default, Length, Directory)
- Настройки тестовой БД (TEST_DATABASE_URL)
- URL-адреса API (URL)
- Тестовые данные (пароли, email, изображения и т.д.)
- Полезные нагрузки (payload) для тестовых запросов
- Ожидаемые поля в ответах API
"""

import os
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from dotenv import load_dotenv
from fastapi import status

from config.constants.core import ConstantsBase
from src.models.enum import CompanyUserRole

load_dotenv()


class AuthData:
    """Тестовые данные для аутентификации.

    Атрибуты:
        BAD_EMAIL: Кортеж невалидных email адресов для тестирования валидации.
        BAD_PASSWORD: Кортеж невалидных паролей для тестирования валидации.
        GOOD_PASSWORD: Валидный пароль для тестирования.
    """

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


class AdminPayloads:
    """Полезные нагрузки (payload) для тестирования администраторов.

    Атрибуты:
        PAYLOAD_BAD_FOR_CREATE_ADMIN: Кортеж невалидных payload для создания администратора.
            Каждый payload не содержит обязательные поля или содержит невалидные данные.
        PAYLOAD_FOR_CREATE_ADMIN: Кортеж валидных payload для создания администратора.
            Содержит различные комбинации обязательных и необязательных полей.
        PAYLOAD_FOR_PATCH_ADMIN: Кортеж валидных payload для обновления данных администратора.
            Содержит различные комбинации полей для тестирования частичного обновления.
    """

    PAYLOAD_FOR_CREATE_ADMIN: tuple[dict[str, str], ...] = (
        {
            'patronymic': 'string',
            'phone_number': 'string',
            'email': 'user1@example.com',
            'password': AuthData.GOOD_PASSWORD,
            'name': 'string',
            'surname': 'string',
        },
        {
            'phone_number': 'string',
            'email': 'user2@example.com',
            'password': AuthData.GOOD_PASSWORD,
            'name': 'string',
            'surname': 'string',
        },
        {
            'patronymic': 'string',
            'email': 'user3@example.com',
            'password': AuthData.GOOD_PASSWORD,
            'name': 'string',
            'surname': 'string',
        },
        {
            'email': 'user4@example.com',
            'password': AuthData.GOOD_PASSWORD,
            'name': 'string',
            'surname': 'string',
        },
    )
    PAYLOAD_BAD_FOR_CREATE_ADMIN: tuple[dict[str, str], ...] = (
        {
            'email': 'user1@example.com',
            'password': AuthData.GOOD_PASSWORD,
            'name': 'string',
        },
        {
            'email': 'user2@example.com',
            'password': AuthData.GOOD_PASSWORD,
            'surname': 'string',
        },
        {
            'password': AuthData.GOOD_PASSWORD,
            'name': 'string',
            'surname': 'string',
        },
        {
            'email': 'user4@example.com',
            'name': 'string',
            'surname': 'string',
        },
    )
    PAYLOAD_FOR_PATCH_ADMIN: tuple[dict[str, str], ...] = (
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


class Default(ConstantsBase.Default):
    """Класс констант значений по умолчанию используемых в пакете `tests`.

    Так же класс наследует значения из ConstantsBase.Default.
    """


class Directory(ConstantsBase.Directory):
    """Класс констант путей к директориям, используемых в пакете `tests`.

    Так же класс наследует значения из ConstantsBase.Directory.
    """


class ExpectedFields:
    """Ожидаемые поля в ответах API.

    Атрибуты:
        COMPANY_FIELDS: Множество полей, ожидаемых в ответе с информацией о компании.
        DEPARTMENT_FIELDS: Множество полей, ожидаемых в ответе с информацией об отделе.
        EMPLOYEE_FIELDS: Множество полей, ожидаемых в ответе с информацией о сотруднике.
    """

    COMPANY_FIELDS: set[str] = {
        'id',
        'name',
        'description',
        'logo',
        'license_id',
        'max_admins_count',
        'max_employees_count',
        'start_license_time',
        'end_license_time',
        'is_active',
        'slug',
        'created_at',
        'updated_at',
    }

    DEPARTMENT_FIELDS: set[str] = {'name', 'slug', 'id', 'company_id'}

    EMPLOYEE_FIELDS: set[str] = {
        'id',
        'email',
        'is_active',
        'is_superuser',
        'is_verified',
        'name',
        'surname',
        'patronymic',
        'phone_number',
        'birthday',
        'telegram_username',
        'role',
        'start_date_employment',
        'end_date_employment',
        'avatar_link',
        'company_id',
        'current_department_id',
        'previous_department_id',
        'department_transition_date',
        'employee_position',
        'created_at',
        'updated_at',
    }


class TextError(ConstantsBase.TextError):
    """Класс для хранения стандартных текстов ошибок, используемых в пакете `tests`.

    Так же класс наследует значения из ConstantsBase.TextError.
    """


class Images:
    """Тестовые изображения в формате base64.

    Атрибуты:
        BASE64_JPG: Изображение в формате JPG, закодированное в base64.
        BASE64_PNG: Изображение в формате PNG, закодированное в base64.
        INVALID: Кортеж невалидных изображений с ожидаемыми ошибками.
    """

    BASE64_PNG: str = (
        'data:image/png;base64,'
        'iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAA'
        'AJcEhZcwAADsQAAA7EAZUrDhsAAAAWSURBVBhXY/jPAEIM/5ns7eyA1H8GADMUBbmnKLI7AAAAAElFTkSuQmCC'
    )

    BASE64_JPG: str = (
        'data:image/jpg;base64,'
        'iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAA'
        'JcEhZcwAADsQAAA7EAZUrDhsAAAAZSURBVBhXY2T4DwQMDAxMBw8dYmBgZGQAAEnjBkemLjB6AAAAAElFTkSuQmCC'
    )

    INVALID: tuple[tuple[Any, Any], ...] = (
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
            f'{BASE64_PNG}b',
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


class Length(ConstantsBase.Length):
    """Класс констант, определяющих ограничения длины для различных полей,
    используемых в пакете `tests`.

    Так же класс наследует значения из ConstantsBase.Length.
    """


@dataclass(frozen=True)
class MiscConstants(ConstantsBase.MiscConstants):
    """Класс разных общесистемных констант, используемых в пакете `tests`.

    Класс реализован, как неизменяемый.

    Так же класс наследует значения из ConstantsBase.MiscConstants.
    """


class ProblemFeedsData:
    """Данные для тестирования ленты проблем `problem_feeds.py`.

    Атрибуты:
        COMMENT_CREATE_BAD: Кортеж невалидных payload для создания комментария
            с ожидаемыми кодами ошибок.
        COMMENT_CREATE_NEW: Валидный payload для создания нового комментария.
        COMMENT_UPDATE: Валидный payload для обновления комментария.
        COMMENT_UPDATE_BAD: Кортеж невалидных payload для обновления комментария
            с ожидаемыми кодами ошибок.
        MESSAGE_FEED_CREATE_BAD: Кортеж невалидных payload для создания ленты сообщений
            с ожидаемыми кодами ошибок.
        MESSAGE_FEED_CREATE_FOR_ANOTHER_COMPANY: Payload для создания ленты сообщений
            для другой компании.
        MESSAGE_FEED_CREATE_NEW: Кортеж валидных payload для создания ленты сообщений
            с флагом важности.
    """

    MESSAGE_FEED_CREATE_NEW: tuple[tuple[dict[str, Any], bool], ...] = (
        ({'text': 'feed with important field', 'important': True}, True),
        ({'text': 'feed w/o important field'}, False),
    )
    MESSAGE_FEED_CREATE_BAD: tuple[tuple[dict[str, Any], int], ...] = (
        ({}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ({'text': 'feed with extra field', 'problem_id': 5}, status.HTTP_422_UNPROCESSABLE_ENTITY),
    )
    MESSAGE_FEED_CREATE_FOR_ANOTHER_COMPANY: dict[str, str] = {'text': 'feed for another company'}
    COMMENT_CREATE_NEW: dict[str, str] = {'text': 'new comment'}
    COMMENT_CREATE_BAD: tuple[tuple[dict[str, Any], int], ...] = (
        ({}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        (
            {'text': 'comment with extra field', 'message_id': 5},
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
    )
    COMMENT_UPDATE: dict[str, str] = {'text': 'updated comment'}
    COMMENT_UPDATE_BAD: tuple[tuple[dict[str, Any], int], ...] = (
        ({}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ({'text': 'comment with extra field', 'rating': 5}, status.HTTP_422_UNPROCESSABLE_ENTITY),
    )


class TabitManagementData:
    """Данные для тестирования управления `tabit_management.py`.

    Атрибуты:
        ADMIN_CREATE_MOD_BAD: Кортеж невалидных payload для создания модератора.
            Варианты payload:
                1) Отсутствие необходимого поля
                2) Некорректный пароль
                3) Повторяющийся email
                4) Некорректная роль
                5) Некорректный company_id
                6) Некорректный current_department_id
                7) Некорректная связка company_id и current_department_id
        ADMIN_CREATE_MOD_NEW: Валидный payload для создания нового модератора.
        ADMIN_GET_MOD_INFO: Ожидаемые коды ответа для получения информации о модераторе.
        ADMIN_PATCH_MOD: Кортеж валидных payload для частичного обновления модератора
            с флагами проверки department_id.
        ADMIN_PATCH_MOD_BAD: Кортеж невалидных payload для частичного обновления модератора.
            Варианты payload:
                1) Лишнее поле
                2) Некорректный пароль
                3) Повторяющийся email
                4) Некорректный current_department_id
                5) Некорректная связка company_id и current_department_id
        ADMIN_PUT_MOD: Кортеж валидных payload для полного обновления модератора
            с флагами проверки department_id.
        ADMIN_PUT_MOD_BAD: Кортеж невалидных payload для полного обновления модератора.
            Варианты payload:
                1) Лишнее поле
                2) Отсутствие необходимого поля
                3) Некорректный пароль
                4) Повторяющийся email
                5) Некорректный current_department_id
                6) Некорректная связка company_id и current_department_id
        MOD_TEST_EMAIL: Тестовый email для модератора.
        MOD_TEST_EMAIL_BAD: Альтернативный тестовый email для модератора.
        TEST_UUID: Тестовый UUID для идентификации.
    """

    TEST_UUID: UUID = UUID('{12345678-1234-5678-1234-567812345678}')
    MOD_TEST_EMAIL: str = 'test@example.com'
    MOD_TEST_EMAIL_BAD: str = 'test_bad@example.com'
    ADMIN_GET_MOD_INFO: tuple[int, int] = (status.HTTP_200_OK, status.HTTP_404_NOT_FOUND)
    ADMIN_CREATE_MOD_NEW: dict[str, str | CompanyUserRole] = {
        'name': 'test',
        'surname': 'test',
        'role': CompanyUserRole.MODERATOR,
        'email': MOD_TEST_EMAIL,
        'password': AuthData.GOOD_PASSWORD,
    }

    ADMIN_CREATE_MOD_BAD: tuple[dict[str, str | int | CompanyUserRole], ...] = (
        {
            'name': 'test_bad',
            'surname': 'test_bad',
            'role': CompanyUserRole.MODERATOR,
            'password': AuthData.GOOD_PASSWORD,
            'company_id': 1,
            'current_department_id': 1,
        },
        {
            'name': 'test_bad',
            'surname': 'test_bad',
            'role': CompanyUserRole.MODERATOR,
            'email': MOD_TEST_EMAIL_BAD,
            'password': AuthData.BAD_PASSWORD[-1],
            'company_id': 1,
            'current_department_id': 1,
        },
        {
            'name': 'test_bad',
            'surname': 'test_bad',
            'role': CompanyUserRole.MODERATOR,
            'email': MOD_TEST_EMAIL,
            'password': AuthData.GOOD_PASSWORD,
            'company_id': 1,
            'current_department_id': 1,
        },
        {
            'name': 'test_bad',
            'surname': 'test_bad',
            'role': CompanyUserRole.EMPLOYEE,
            'email': MOD_TEST_EMAIL_BAD,
            'password': AuthData.GOOD_PASSWORD,
            'company_id': 1,
            'current_department_id': 1,
        },
        {
            'name': 'test_bad',
            'surname': 'test_bad',
            'role': CompanyUserRole.MODERATOR,
            'email': MOD_TEST_EMAIL_BAD,
            'password': AuthData.GOOD_PASSWORD,
            'company_id': 99,
            'current_department_id': 1,
        },
        {
            'name': 'test_bad',
            'surname': 'test_bad',
            'role': CompanyUserRole.MODERATOR,
            'email': MOD_TEST_EMAIL_BAD,
            'password': AuthData.GOOD_PASSWORD,
            'company_id': 1,
            'current_department_id': 99,
        },
        {
            'name': 'test_bad',
            'surname': 'test_bad',
            'role': CompanyUserRole.MODERATOR,
            'email': MOD_TEST_EMAIL_BAD,
            'password': AuthData.GOOD_PASSWORD,
            'company_id': 2,
            'current_department_id': 1,
        },
    )
    ADMIN_PATCH_MOD: tuple[tuple[dict[str, str | int], bool], ...] = (
        ({'name': 'updated_name', 'email': 'updated@example.com'}, False),
        ({'current_department_id': 2}, True),
    )

    ADMIN_PATCH_MOD_BAD: tuple[dict[str, str | int], ...] = (
        {'company_id': 2},
        {'password': AuthData.BAD_PASSWORD[-1]},
        {'email': MOD_TEST_EMAIL_BAD},
        {'current_department_id': 99},
        {'current_department_id': 2},
    )
    ADMIN_PUT_MOD: tuple[tuple[dict[str, str | int | CompanyUserRole], bool], ...] = (
        (
            {
                'name': 'updated_name',
                'surname': 'updated_surname',
                'email': 'updated@example.com',
                'password': AuthData.GOOD_PASSWORD,
                'role': CompanyUserRole.MODERATOR,
                'current_department_id': 1,
            },
            False,
        ),
        (
            {
                'name': 'updated_name',
                'surname': 'updated_surname',
                'email': 'updated@example.com',
                'password': AuthData.GOOD_PASSWORD,
                'role': CompanyUserRole.MODERATOR,
                'current_department_id': 2,
            },
            True,
        ),
    )

    ADMIN_PUT_MOD_BAD: tuple[dict[str, str | int | CompanyUserRole], ...] = (
        {
            'name': 'test_bad',
            'surname': 'test_bad',
            'role': CompanyUserRole.MODERATOR,
            'email': MOD_TEST_EMAIL,
            'password': AuthData.GOOD_PASSWORD,
            'company_id': 1,
            'current_department_id': 1,
        },
        {
            'name': 'test_bad',
            'surname': 'test_bad',
            'role': CompanyUserRole.MODERATOR,
            'password': AuthData.GOOD_PASSWORD,
            'current_department_id': 1,
        },
        {
            'name': 'test_bad',
            'surname': 'test_bad',
            'role': CompanyUserRole.MODERATOR,
            'email': MOD_TEST_EMAIL,
            'password': AuthData.BAD_PASSWORD[-1],
            'current_department_id': 1,
        },
        {
            'name': 'test_bad',
            'surname': 'test_bad',
            'role': CompanyUserRole.MODERATOR,
            'email': MOD_TEST_EMAIL_BAD,
            'password': AuthData.GOOD_PASSWORD,
            'current_department_id': 1,
        },
        {
            'name': 'test_bad',
            'surname': 'test_bad',
            'role': CompanyUserRole.MODERATOR,
            'email': MOD_TEST_EMAIL,
            'password': AuthData.GOOD_PASSWORD,
            'current_department_id': 99,
        },
        {
            'name': 'test_bad',
            'surname': 'test_bad',
            'role': CompanyUserRole.MODERATOR,
            'email': MOD_TEST_EMAIL,
            'password': AuthData.GOOD_PASSWORD,
            'current_department_id': 2,
        },
    )


class Test_Database_URL:
    """Настройки подключения к тестовой базе данных.

    Атрибуты:
        USER: Имя пользователя тестовой БД
        PASSWORD: Пароль пользователя тестовой БД
        HOST: Хост тестовой БД
        PORT: Порт тестовой БД
        DBNAME: Имя тестовой БД
    """

    USER: str = os.getenv('TEST_POSTGRES_USER', 'test_user')
    PASSWORD: str = os.getenv('TEST_POSTGRES_PASSWORD', 'test_password')
    HOST: str = os.getenv('TEST_POSTGRES_HOST', 'localhost')
    PORT: int = int(os.getenv('TEST_POSTGRES_PORT', 54333))
    DBNAME: str = os.getenv('TEST_POSTGRES_DB', 'test_db')


@dataclass(frozen=True)
class Url:
    """Все пути API, используемые в тестах.

    Класс реализован, как неизменяемый.

    Содержит эндпоинты для:
    - Аутентификации администратора и пользователя
    - Управления компаниями, лицензиями, отделами и сотрудниками
    - Встреч и обратной связи
    - Ленты проблем и комментариев
    - Управления модераторами

    Атрибуты:
        ADMIN_AUTH: Базовый URL для аутентификации администратора
        ADMIN_GET_COMPANIES: URL для получения списка компаний администратором
        ADMIN_LOGIN: URL для входа администратора
        ADMIN_LOGOUT: URL для выхода администратора
        ADMIN_ME: URL для получения информации о текущем администраторе
        ADMIN_MOD_DATA_URL: URL для работы с данными конкретного модератора
        ADMIN_MODS_URL: URL для работы со списком модераторов
        ADMIN_REFRESH: URL для обновления токена администратора
        COMMENTS_PATCH_DELETE_404_URL: URL для тестирования ошибок при работе с комментариями
        COMMENTS_PATCH_DELETE_URL: URL для изменения/удаления комментариев
        COMMENTS_URL: URL для работы с комментариями
        COMPANY_ENDPOINT: URL для работы с конкретной компанией
        COMPANIES_ENDPOINT: URL для работы со списком компаний
        CREATE_DEPARTMENT_ENDPOINT: URL для создания отдела
        CREATE_EMPLOYEE_ENDPOINT: URL для создания сотрудника
        DEPARTMENT_ENDPOINT: URL для работы с конкретным отделом
        DEPARTMENTS_ENDPOINT: URL для работы со списком отделов
        EMPLOYEE_ENDPOINT: URL для работы с конкретным сотрудником
        EMPLOYEES_ENDPOINT: URL для работы со списком сотрудников
        FEEDBACK_ENDPOINT: URL для работы с обратной связью
        LICENSES_ENDPOINT: URL для работы с лицензиями
        LIKE_URL: URL для лайка комментария
        MEETINGS_ENDPOINT: URL для работы со списком встреч
        MEETINGS_SINGLE: URL для работы с конкретной встречей
        MESSAGE_FEED_URL: URL для работы с лентой сообщений
        UNLIKE_URL: URL для снятия лайка с комментария
        USER_LOGIN: URL для входа пользователя
        USER_LOGOUT: URL для выхода пользователя
        USER_ME: URL для получения информации о текущем пользователе
        USER_REFRESH: URL для обновления токена пользователя
    """

    ADMIN_AUTH: str = '/api/v1/admin/auth/'
    ADMIN_LOGIN: str = '/api/v1/admin/auth/login'
    ADMIN_LOGOUT: str = '/api/v1/admin/auth/logout'
    ADMIN_ME: str = '/api/v1/admin/auth/me'
    ADMIN_REFRESH: str = '/api/v1/admin/auth/refresh-token'
    COMPANIES_ENDPOINT: str = '/api/v1/admin/companies/'
    COMPANY_ENDPOINT: str = '/api/v1/{company_slug}/'
    CREATE_DEPARTMENT_ENDPOINT: str = '/api/v1/{company_slug}/departments'
    CREATE_EMPLOYEE_ENDPOINT: str = '/api/v1/{company_slug}/employees'
    DEPARTMENT_ENDPOINT: str = '/api/v1/{company_slug}/departments/{department_slug}'
    DEPARTMENTS_ENDPOINT: str = '/api/v1/{company_slug}/departments'
    EMPLOYEE_ENDPOINT: str = '/api/v1/{company_slug}/employees/{employee_id}'
    EMPLOYEES_ENDPOINT: str = '/api/v1/{company_slug}/employees'
    FEEDBACK_ENDPOINT: str = '/api/v1/{company_slug}/feedback/'
    LICENSES_ENDPOINT: str = '/api/v1/admin/licenses/'
    MEETINGS_ENDPOINT: str = '/api/v1/{company_slug}/problems/{problem_id}/meetings/'
    MEETINGS_SINGLE: str = '/api/v1/{company_slug}/problems/{problem_id}/meetings/{meeting_id}'
    USER_LOGIN: str = '/api/v1/auth/login'
    USER_LOGOUT: str = '/api/v1/auth/logout'
    USER_ME: str = '/api/v1/auth/me'
    USER_REFRESH: str = '/api/v1/auth/refresh-token'

    # URLs для problem_feeds.py
    COMMENTS_PATCH_DELETE_404_URL: str = (
        '/api/v1/{company_slug}/{problem_id}/{message_feed_id}/comments/{comment_id}'
    )
    COMMENTS_PATCH_DELETE_URL: str = (
        '/api/v1/{company_slug}/problems/1/{message_feed_id}/comments/{comment_id}'
    )
    COMMENTS_URL: str = '/api/v1/{company_slug}/problems/{problem_id}/{message_feed_id}/comments'
    LIKE_URL: str = '/api/v1/{company_slug}/problems/1/{message_feed_id}/comments/1/like'
    MESSAGE_FEED_URL: str = '/api/v1/{company_slug}/problems/{problem_id}/thread'
    UNLIKE_URL: str = '/api/v1/{company_slug}/problems/1/{message_feed_id}/comments/1/unlike'

    # URLs для tabit_management.py
    ADMIN_GET_COMPANIES: str = '/api/v1/admin/'
    ADMIN_MOD_DATA_URL: str = '/api/v1/admin/staff/{user_id}'
    ADMIN_MODS_URL: str = '/api/v1/admin/staff'


class UserPayloads:
    """Полезные нагрузки (payload) для тестирования пользователей.

    Атрибуты:
        MODERATOR_TELEGRAM: Тестовый Telegram username для модератора
        PAYLOAD_FOR_PATCH_USER: Кортеж валидных payload для обновления данных пользователя
        PAYLOAD_FOR_PATCH_USER_EXTRA: Payload с дополнительными полями для тестирования валидации
        USER_TELEGRAM: Тестовый Telegram username для пользователя
    """

    MODERATOR_TELEGRAM: str = 'avadakedavra'
    PAYLOAD_FOR_PATCH_USER: tuple[dict[str, str], ...] = (
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
    PAYLOAD_FOR_PATCH_USER_EXTRA: dict[str, int | str | bool | CompanyUserRole] = {
        'id': 1776,
        'email': 'illuminati@world.gov',
        'is_active': False,
        'is_superuser': True,
        'is_verified': False,
        'role': CompanyUserRole.MODERATOR,
        'start_date_employment': '1776-05-01',
        'end_date_employment': '1776-05-01',
        'company_id': 1776,
        'current_department_id': 1776,
        'previous_department_id': 1776,
        'department_transition_date': '1776-05-01',
        'employee_position': 'Минервал',
        'created_at': '1776-05-01 00:00:01.000 +0100',
        'updated_at': '1776-05-01 00:00:01.000 +0100',
    }
    USER_TELEGRAM: str = 'expectopatronum'
