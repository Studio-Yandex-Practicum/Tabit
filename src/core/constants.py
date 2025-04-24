import string
from dataclasses import dataclass
from pathlib import Path
from re import compile

BASE_DIR = Path(__file__).resolve().parent.parent

# TODO: создать класс Length, декорировать dataclass. Все длины упаковать в этот класс, из названий
# констант удалить слово LENGTH
MIN_LENGTH_NAME: int = 2
MIN_DESCRIPTION_NAME: int = 2
MIN_LENGTH_PASSWORD: int = 8
MIN_LENGTH_TELEGRAM_USERNAME: int = 5
LENGTH_NAME_USER: int = 100
LENGTH_NAME_LICENSE: int = 100
LENGTH_NAME_COMPANY: int = 255
LENGTH_DESCRIPTION_COMPANY: int = 255
LENGTH_NAME_DEPARTMENT: int = 255
LENGTH_NAME_PROBLEM: int = 255
LENGTH_NAME_MEETING_PLACE: int = 255
LENGTH_SMALL_NAME: int = 30
LENGTH_TELEGRAM_USERNAME: int = 100
LENGTH_FILE_LINK: int = 2048
LENGTH_SLUG: int = 25

# Проверяет наличие символов в обоих регистрах, числел и минимальную длину 8 символов
PATTERN_PASSWORD: str = rf'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{{{MIN_LENGTH_PASSWORD},}}$'
# Проверяет наличие символов в обоих регистрах, чисел, спецсимволов и минимальную длину 8 символов
# PATTERN_PASSWORD: str = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'

ZERO: int = 0

TEXT_ERROR_INVALID_PASSWORD: str = (
    'Пароль должен содержать символы латинского алфавита в обоих регистрах, числа и иметь '
    f'минимальную длину в {MIN_LENGTH_PASSWORD} символов.'
)

# crud
DEFAULT_SKIP: int = 0  # Значение по умолчанию для пропуска записей
DEFAULT_LIMIT: int = 100  # Ограничение количества записей
DEFAULT_AUTO_COMMIT: bool = True  # для crud

TEXT_ERROR_NOT_FOUND: str = 'Объект не найден'
TEXT_ERROR_UNIQUE: str = 'Ошибка уникальности. Такой объект уже существует.'
TEXT_ERROR_UNIQUE_CREATE_LOG: str = 'Ошибка уникальности при создании'
TEXT_ERROR_UNIQUE_UPDATE_LOG: str = 'Ошибка уникальности при обновлении'
TEXT_ERROR_SERVER_CREATE: str = 'Ошибка сервера при создании объекта.'
TEXT_ERROR_SERVER_CREATE_LOG: str = 'Ошибка при создании'
TEXT_ERROR_SERVER_UPDATE: str = 'Ошибка сервера при обновлении объекта.'
TEXT_ERROR_SERVER_UPDATE_LOG: str = 'Ошибка при обновлении'
TEXT_ERROR_SERVER_DELETE: str = 'Ошибка сервера при удалении объекта.'
TEXT_ERROR_SERVER_DELETE_LOG: str = 'Ошибка при удалении'

TEXT_ERROR_EXISTS_EMAIL: str = 'Пользователь с такой электронной почтой уже существует.'
TEXT_ERROR_INVALID_PASSWORD: str = 'Не корректный пароль'

# Константы для моделей компании, департамента и сотрудника отдела.
ERROR_INVALID_PASSWORD: str = 'Пароль не соответвует требованиям.'
ERROR_USER_ALREADY_EXISTS: str = 'Пользователь с данным email уже существует.'
ERROR_USER_NOT_EXISTS: str = 'Пользователь с таким UUID не существует.'

TITLE_NAME_COMPANY: str = 'Название компании'
TITLE_LOGO_COMPANY: str = 'Логотип'
TITLE_LICENSE_ID_COMPANY: str = 'Ссылка на тип лицензии'
TITLE_START_LICENSE_TIME_COMPANY: str = 'Дата начала действия лицензии'
TITLE_SLUG_COMPANY: str = 'Slug компании'

TITLE_NAME_DEPARTMENT: str = 'Название отдела'
TITLE_SLUG_DEPARTMENT: str = 'Slug отдела'

TEST_ERROR_INVALID_CHARACTERS_NAME = 'Имя содержит недопустимые символы!'
TEST_ERROR_INVALID_CHARACTERS_SURNAME = 'Фамилия содержит недопустимые символы!'
TEST_ERROR_LICENSE_FIELDS: str = (
    'Поля начала действия лицензии и тип лицензии заполняются одновременно.'
)
TEST_ERROR_UNIQUE_NAME_SURNAME = 'Имя и фамилия не могут совпадать!'
SHORT_SYMBOLS = string.ascii_letters
GENERATED_SLUG_SUFFIX_RANGE = 3
ATTEMPTS = 100
SLUG_NOT_GENERATED = (
    f'Сделано {ATTEMPTS} попыток, но сгенерировать slug не удалось. Попробуйте снова.'
)
# Фильтрация и сортировка для лицензии
FILTER_NAME_DESCRIPTION = 'Фильтр по названию компании'
SORTING_DESCRIPTION = (
    "Сортировка по полю (name, created_at, updated_at). '-' означает сортировку в обратном порядке"
)


# Модуль констант для энпоинтов приложения.
@dataclass
class Summary:
    """Содержит текст резюме конечных точек."""

    TABIT_ADMIN_AUTH_LIST: str = 'Список администраторов'
    TABIT_ADMIN_AUTH_GET_BY_ID: str = 'Карточка конкретного администратора сервиса'
    TABIT_ADMIN_AUTH_PATCH_BY_ID: str = 'Изменить данные конкретного администратора сервиса'
    TABIT_ADMIN_AUTH_DELETE_BY_ID: str = 'Удалить конкретного администратора сервиса'
    TABIT_ADMIN_AUTH_GET_ME: str = 'Доступ к своим данным администратора сервиса'
    TABIT_ADMIN_AUTH_PATCH_ME: str = 'Для редактирования своих данных администратору сервиса'
    TABIT_ADMIN_AUTH_REFRESH_TOKEN: str = 'Обновить токен'
    TABIT_ADMIN_AUTH_CREATE: str = 'Создать администратора сервиса'
    TABIT_ADMIN_AUTH_LOGIN: str = 'Авторизация'
    TABIT_ADMIN_AUTH_LOGOUT: str = 'Выход из система'

    TABIT_MANAGEMENT_COMPANY_LIST: str = 'Список всех компаний'
    TABIT_MANAGEMENT_COMPANY_CREATE: str = 'Создать новую компанию'
    TABIT_MANAGEMENT_COMPANY_UPDATE: str = 'Обновить данные компании'
    TABIT_MANAGEMENT_COMPANY_DELETE: str = 'Удалить компанию'

    TABIT_COMPANY: str = 'Получить данные о компании'
    TABIT_COMPANY_DEPARTMENTS_LIST: str = 'Получить список всех отделов компании'
    TABIT_COMPANY_DEPARTMENTS_CREATE: str = 'Создать новый отдел компании'
    TABIT_COMPANY_DEPARTMENT: str = 'Получить данные об отделе компании'
    TABIT_COMPANY_DEPARTMENTS_UPDATE: str = 'Обновить данные об отделе компании'
    TABIT_COMPANY_DEPARTMENTS_DELETE: str = 'Удалить отдел компании'
    TABIT_COMPANY_DEPARTMENTS_IMPORT: str = 'Импортировать список отделов компании'

    TABIT_COMPANY_EMPLOYEES_LIST: str = 'Получить список всех сотрудников компании'
    TABIT_COMPANY_EMPLOYEE: str = 'Получить информацию о сотруднике компании'
    TABIT_COMPANY_EMPLOYEES_CREATE: str = 'Добавить сотрудника в отдел компании'
    TABIT_COMPANY_EMPLOYEES_UPDATE: str = 'Изменить данные сотрудника компании'
    TABIT_COMPANY_EMPLOYEES_DELETE: str = 'Удалить сотрудника компании'
    TABIT_COMPANY_EMPLOYEES_IMPORT: str = 'Импортировать список сотрудников компании'

    COMPANY_USER_AUTH_LOGIN: str = 'Авторизация'
    COMPANY_USER_AUTH_LOGOUT: str = 'Выход из система'
    COMPANY_USER_AUTH_REFRESH_TOKEN: str = 'Обновить токен'

    USER_AUTH_GET_ME: str = 'Доступ к своим данным пользователя сервиса'
    USER_AUTH_PATCH_ME: str = 'Для редактирования своих данных пользователя сервиса'

    PROBLEM_LIST: str = 'Получить список всех проблем для пользователя'
    PROBLEM_CREATE: str = 'Создать новую проблему'
    PROBLEM: str = 'Получить информацию о проблеме'
    PROBLEM_UPDATE: str = 'Обновить информацию о проблеме'
    PROBLEM_DELETE: str = 'Удалить проблему'
    PROBLEM_CONFIRM: str = 'Подтвердить активное участие в решения проблемы'

    MEETING_LIST: str = 'Получить список всех встреч для пользователя'
    MEETING_CREATE: str = 'Создать новую встречу'
    MEETING: str = 'Получить информацию о встречи'
    MEETING_UPDATE: str = 'Обновить информацию о встречи'
    MEETING_DELETE: str = 'Удалить встречу'

    TASK_LIST: str = 'Получить список всех задач для пользователя'
    TASK_CREATE: str = 'Создать новую задачу'
    TASK: str = 'Получить информацию о задаче'
    TASK_UPDATE: str = 'Обновить информацию о задаче'
    TASK_DELETE: str = 'Удалить задачу'


@dataclass
class Description:
    """Содержит текст описаний для конечных точек."""

    TABIT_ADMIN_AUTH_LIST: str = (
        'Возвращает список администраторов. Доступно только суперпользователю.'
    )
    TABIT_ADMIN_AUTH_GET_BY_ID: str = (
        'Отобразит карточку администратора сервиса по его `id`. Доступно только суперпользователю.'
    )
    TABIT_ADMIN_AUTH_PATCH_BY_ID: str = (
        'Изменить данные карточки администратора сервиса по его `id`. Доступно только '
        'суперпользователю.'
    )
    TABIT_ADMIN_AUTH_DELETE_BY_ID: str = (
        'Удалить администратора сервиса по его `id`. Доступно только суперпользователю. '
        'Удалить суперпользователя нельзя.'
    )
    TABIT_ADMIN_AUTH_GET_ME: str = (
        'Для доступа к своей учетной записи администраторов сервиса. '
        'Доступно только хозяину учетной записи.'
    )
    TABIT_ADMIN_AUTH_PATCH_ME: str = (
        'Позволит обновить данные о себе администратору сервиса. '
        'Доступно только хозяину учетной записи.'
    )
    TABIT_ADMIN_AUTH_REFRESH_TOKEN: str = (
        'Для обновления в токенов необходимо в заголовке '
        'Authorization передать refresh-token, вместо access-token. '
        'В ответ вернет два новых токена. Доступно только администраторам сервиса.'
    )
    TABIT_ADMIN_AUTH_CREATE: str = (
        'Создает нового администратора сервиса. Доступно только суперпользователю.'
    )
    TABIT_ADMIN_AUTH_LOGIN: str = 'Авторизация администраторов сервиса.'
    TABIT_ADMIN_AUTH_LOGOUT: str = 'Выход из системы администраторов сервиса.'

    TABIT_MANAGEMENT_COMPANY_LIST: str = (
        'Возвращает список всех компаний. Доступно только администраторам сервиса.'
    )
    TABIT_MANAGEMENT_COMPANY_CREATE: str = (
        'Создает новую компанию. Доступно только администраторам сервиса.'
        'Поля "license_id" и "start_license_time" либо оба указываются, либо не одного.'
    )
    TABIT_MANAGEMENT_COMPANY_UPDATE: str = (
        'Обновляет данные компании по её `slug`. Доступно только администраторам сервиса.'
    )
    TABIT_MANAGEMENT_COMPANY_DELETE: str = (
        'Удаляет компанию по её `slug`. Доступно только администраторам сервиса.'
        'Поля "license_id" и "start_license_time" либо оба указываются, либо не одного.'
    )

    COMPANY_USER_AUTH_LOGIN: str = 'Авторизация пользователя сервиса.'
    COMPANY_USER_AUTH_LOGOUT: str = 'Авторизация пользователя сервиса.'
    COMPANY_USER_AUTH_REFRESH_TOKEN: str = (
        'Для обновления в токенов необходимо в заголовке Authorization передать refresh-token, '
        'вместо access-token. В ответ вернет два новых токена. Доступно только пользователя '
        'сервиса. У администраторов сервиса своя конечная точка.'
    )

    USER_AUTH_GET_ME: str = (
        'Для доступа к своей учетной записи пользователей сервиса. '
        'Доступно только хозяину учетной записи.'
    )
    USER_AUTH_PATCH_ME: str = (
        'Позволит обновить данные о себе пользователей сервиса. '
        'Доступно только хозяину учетной записи.'
    )

    PROBLEM_LIST: str = (
        'Получить список всех проблем для конкретного пользователя.'
        'Список будет содержать проблемы его компании.'
        'Доступно пользователям от компании.'
    )
    PROBLEM_CREATE: str = (
        'Создаст новую проблему.'
        'Поддерживает получение списка участников для решения проблемы.'
        'Доступно пользователям от компании.'
    )
    PROBLEM: str = (
        'Получить информацию о проблеме по её идентификационному номеру.'
        'Доступно пользователям от компании.'
    )
    PROBLEM_UPDATE: str = (
        'Обновить информацию о проблеме.'
        'Поддерживает получение списка участников для решения проблемы.'
        'Доступно пользователям от компании, который является автором проблемы.'
    )
    PROBLEM_DELETE: str = (
        'Удаляет проблему.Доступно пользователям от компании, который является автором проблемы.'
    )
    PROBLEM_CONFIRM: str = (
        'Подтвердить активное участие в решения проблемы.'
        'Доступно пользователям от компании, которые являются участником решения проблемы.'
    )

    MEETING_LIST: str = (
        'Получить список всех встреч для конкретного пользователя, по конкретной проблеме.'
        'Список будет содержать проблемы его компании.'
        'Доступно пользователям от компании.'
    )
    MEETING_CREATE: str = (
        'Создаст новую встречу.'
        'Доступно пользователям от компании, которые являются участниками решения проблемы.'
    )
    MEETING: str = (
        'Получить информацию о встрече по её идентификационному номеру.'
        'Доступно пользователям от компании.'
    )
    MEETING_UPDATE: str = (
        'Обновить информацию о встрече.'
        'Поддерживает получение списка участников встречи.'
        'Доступно пользователям от компании, который является автором встречи.'
    )
    MEETING_DELETE: str = (
        'Удаляет встречу.Доступно пользователям от компании, который является автором встречи.'
    )

    TASK_LIST: str = (
        'Получить список всех задач для конкретного пользователя, по конкретной проблеме.'
        'Список будет содержать проблемы его компании.'
        'Доступно пользователям от компании.'
    )
    TASK_CREATE: str = (
        'Создаст новую проблему.'
        'Поддерживает получение списка исполнителей задачи.'
        'Доступно пользователям от компании, которые являются участниками решения проблемы.'
    )
    TASK: str = (
        'Получить информацию о задачи по её идентификационному номеру.'
        'Доступно пользователям от компании.'
    )
    TASK_UPDATE: str = (
        'Обновить информацию о проблеме.'
        'Поддерживает получение списка исполнителей задачи.'
        'Доступно пользователям от компании, который является автором задачи.'
    )
    TASK_DELETE: str = (
        'Удаляет задачу.Доступно пользователям от компании, который является автором задачи.'
    )


# crud
DEFAULT_SKIP: int = 0  # Значение по умолчанию для пропуска записей
DEFAULT_LIMIT: int = 100  # Ограничение количества записей
DEFAULT_AUTO_COMMIT: bool = True  # для crud

BASE64_STARTSWITH: str = 'data:image'

MAX_NUMBER_PROBLEM: int = 3

OPENAPI_EXTRA_ADMIN_AUTH = {'security': [{'jwt_auth_backend_admin': []}]}


@dataclass
class TextError:
    """Содержит текст сообщений об ошибке."""

    BASE64_TYPE: str = f'Переданный файл не является строкой начинающийся на с {BASE64_STARTSWITH}'
    BASE64_FATAL: str = 'Ошибка при сохранение картинки {image}: {error_class}: {error_text}'
    INVALID_PASSWORD: str = (
        'Пароль должен содержать символы латинского алфавита в обоих регистрах, числа и иметь '
        f'минимальную длину в {MIN_LENGTH_PASSWORD} символов.'
    )
    NOT_FOUND: str = 'Не найден объект {obj} по данному id: {id}'
    NOT_FOUND_BY_SLUG: str = 'Не найден объект {obj} по данному slug: {slug}'
    UNIQUE: str = 'Ошибка уникальности. Такой объект уже существует.'
    UNIQUE_CREATE_LOG: str = 'Ошибка уникальности при создании'
    UNIQUE_UPDATE_LOG: str = 'Ошибка уникальности при обновлении'
    SERVER_CREATE: str = 'Ошибка сервера при создании объекта.'
    SERVER_CREATE_LOG: str = 'Ошибка при создании'
    SERVER_UPDATE: str = 'Ошибка сервера при обновлении объекта.'
    SERVER_UPDATE_LOG: str = 'Ошибка при обновлении'
    SERVER_DELETE: str = 'Ошибка сервера при удалении объекта.'
    SERVER_DELETE_LOG: str = 'Ошибка при удалении'
    EXISTS_EMAIL: str = 'Пользователь с такой электронной почтой уже существует.'
    FORBIDDEN_ROLE_MODERATOR: str = 'Доступно только модераторам компаний'
    LOGIN = 'Неверные учетные данные для входа в систему'
    IS_SUPERUSER: str = 'Объект - суперпользователь'
    DEPARTMENT_EXIST_ERROR_MESSAGE: str = 'Объект с таким именем уже существует.'
    FORBIDDEN_FROM_COMPANY: str = 'Доступно только пользователю, из компании: {}.'
    FORBIDDEN_OWNER: str = 'Доступно только пользователю, создавшему объект.'
    FORBIDDEN_NOT_MEMBER: str = 'Только участники проблемы могут создавать встречи.'
    CLOSE_PROBLEM: str = (
        'Завершенные проблемы нельзя изменять, удалять, '
        'а также создавать/изменять для них встречи или задачи. '
        'Так же нельзя добавляться как участник к данной проблеме.'
    )
    MEETING_WAS_HELD: str = 'Проведенные встречи нельзя изменять или удалять.'
    TASK_COMPLETED: str = 'Завершенные задачи нельзя изменять или удалять'
    LAST_DATE: str = 'Вы указали прошедшую дату.'
    UUID_INVALID: str = 'UUID в поле members не корректен или пользователя с таким UUID нет: {}'
    USER_NOT_FROM_COMPANY: str = (
        'UUID в поле members принадлежит пользователю от другой компании: {}'
    )
    NOT_IS_MEMBERS: str = (
        'Вы не можете принять участие в решение проблемы, так как вы не являетесь её участником.'
    )


@dataclass
class TextScripts:
    """Текстовые переменные файла scripts.py."""

    DESCRIPTION: str = """
        Запустит проект с помощью uvicorn.

        флаги --reload, --host, --port опциональные и могут указываться одновременно.\n
        фдаг --create-superuser - создаст первого суперпользователя согласно данным в .env без
        последующего запуска проекта.
        """
    LOGGER: str = 'Starting uvicorn server...'
    RELOAD: str = 'Запустит uvicorn с флагом --reload'
    HOST: str = 'Указать хост при запуске.'
    PORT: str = 'Указать порт при запуске.'
    CREATE: str = 'Создать суперпользователя'


@dataclass
class Directory:
    """Названия директорий проекта, используемые в коде."""

    MEDIA: str = 'media'
    LOGO: str = 'logo'
    AVATAR: str = 'avatar'
    WAIF: str = 'waif'


DEFAULT_NUMBER_DEY_LICENSE: int = 1
DEFAULT_LICENSE_TERM: dict[str, int] = {'days': 1}

TITLE_NAME_LICENSE: str = 'Название лицензии'
TITLE_LICENSE_TERM: str = 'Срок действия лицензии в днях'
TITLE_MAX_MODERATORS_COUNT: str = 'Максимальное количество модераторов'
TITLE_MAX_EMPLOYEES_COUNT: str = 'Максимальное количество сотрудников'
TITLE_NAME_MODERATOR: str = 'Имя модератора сервиса'
TITLE_SURNAME_MODERATOR: str = 'Фамилия модератора сервиса'
TITLE_PATRONYMIC_MODERATOR: str = 'Отчество модератора сервиса'
TITLE_PHONE_NUMBER_MODERATOR: str = 'Контактный телефон модератора сервиса'
TITLE_EMAIL: str = 'Электронная почта пользователя'
TITLE_PASSWORD: str = 'Пароль пользователя'
TITLE_IS_SUPERUSER_ADMIN: str = (
    'Бул поле, для указания, является ли пользователь суперпользователем'
)
LICENSE_TERM_REGEX = compile(r'^P.*Y$|^P.*D$')

ERROR_FIELD_INTERVAL: str = (
    'Поле не может быть пустым. '
    'Может быть целым числом, или строкой, обозначающее целое число, '
    'или строкой формата "P1D", "P1Y", "P1Y1D".'
)
ERROR_FIELD_START_OR_END_SPACE = 'Поле не может начинаться или заканчиваться пробелом.'
ERROR_USER_ALREADY_EXISTS = 'Пользователь с данным email уже существует.'
ERROR_INVALID_PASSWORD = 'Пароль не соответвует требованиям.'
ERROR_USER_NOT_EXISTS = 'Пользователь с таким UUID не существует.'
ERROR_UPDATE_METHOD = 'Пользователь с указанными email и/или phone_number уже существует.'
RESET_PASSWORD_SUCCESS = 'Пароль был успешено установлен.'
ERROR_FIELD_START_OR_END_SPACE: str = 'Поле не может начинаться или заканчиваться пробелом.'
ERROR_INTERNAL_SERVER = 'Внутреннияя ошибка сервера.'
ERROR_INVALID_TELEGRAM_USERNAME = 'Пользователь с указанным Telegram username уже существует.'

# Пагинация
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
MIN_PAGE_SIZE = 1

# Фильтрация и сортировка для лицензии
FILTER_NAME_DESCRIPTION = 'Фильтр по названию лицензии'
SORTING_DESCRIPTION = (
    "Сортировка по полю (name, created_at, updated_at). '-' означает сортировку в обратном порядке"
)

# Поля ответа
TOTAL_DESCRIPTION = 'Общее количество записей'
PAGE_DESCRIPTION = 'Текущая страница'
PAGE_SIZE_DESCRIPTION = 'Количество записей на странице'
ITEMS_DESCRIPTION = 'Список лицензий'

# Константы для summary в эндпоинтах лицензий
SUMMARY_GET_LICENSES = 'Получить список всех лицензий с фильтрацией и сортировкой'
SUMMARY_CREATE_LICENSE = 'Создать новую лицензию'
SUMMARY_GET_LICENSE = 'Получить данные лицензии'
SUMMARY_UPDATE_LICENSE = 'Обновить данные лицензии'
SUMMARY_DELETE_LICENSE = 'Удалить лицензию'

# Константы для валидаторов
VALID_PHONE_NUMBER_PATTERN = r'^7\d{10}'
VALID_TELEGRAM_USERNAME_PATTERN = r'\w+'
VALID_INVALID_PASSWORD = 'Указан некорректный формат пароля.'
VALID_INVALID_PHONE_NUMBER = 'Некорректный формат номера телефона.'
VALID_INVALID_TELEGRAM_USERNAME = (
    'Telegram username должен состоять только из латинских букв и цифр.'
)
VALID_INVALID_DATE = 'Указана некорректная дата.'
VALID_INVALID_START_DATE = (
    'Параметр start_date_employment не может быть больше end_date_employment.'
)

TITLE_NAME_USER: str = 'Имя пользователя сервиса'
TITLE_SURNAME_USER: str = 'Фамилия пользователя сервиса'
TITLE_PATRONYMIC_USER: str = 'Отчество пользователя сервиса'
TITLE_PHONE_NUMBER_USER: str = 'Контактный телефон пользователя сервиса'
TITLE_IS_ACTIVE_USER: str = 'Активен ли пользователь'
TITLE_BIRTHDAY_USER: str = 'День рождение пользователя'
TITLE_TELEGRAM_USERNAME_USER: str = 'Имя пользователя в Telegram'
TITLE_ROLE_USER: str = 'Роль пользователя компании.'
TITLE_START_DATE_EMPLOYMENT_USER: str = 'Дата начало работы сотрудника в компании'
TITLE_END_DATE_EMPLOYMENT_USER: str = 'Дата конца работы сотрудника в компании'
TITLE_AVATAR_LINK_USER: str = 'Ссылка на аватар пользователя'
TITLE_COMPANY_ID_USER: str = 'id компании, в которой работает пользователь'
TITLE_CURRENT_DEPARTMENT_ID_USER: str = 'id отдела, в котором работает пользователь'
TITLE_PREVIOUS_DEPARTMENT_ID_USER: str = 'id отдела, в котором работал пользователь до этого'
TITLE_DEPARTMENT_TRANSITION_DATE_USER: str = 'Последняя дата перехода из одного отдела в другой'
TITLE_EMPLOYEE_POSITION_USER: str = 'Позиция в коллективе, указывается админом компании'
TITLE_CREATED_AT_USER: str = 'Дата создания профиля пользователя'
TITLE_UPDATED_AT_USER: str = 'Дата обновления профиля пользователя'


TITLE_NAME_TAG: str = 'Имя тэга'
TITLE_COMPANY_ID_TAG: str = 'id компании, в которой используется тэг'

# Константы к валидаторам (Общие)
ERROR_COMPANY_NOT_FOUND = 'Такая компания не найдена'
ERROR_PROBLEM_NOT_FOUND = 'Такая проблема не найдена'
ERROR_TASK_NOT_FOUND = 'Такая задача не найдена'
ERROR_MEETING_NOT_FOUND = 'Такая встреча не найдена'


# Константы к валидаторам (Problem)
ERROR_PROBLEM_NAME_EMPTY = 'Название проблемы не может быть пустым'
ERROR_PROBLEM_NUMBER: str = 'Вы уже участвуете в решение {} или более проблем.'

# Константы к валидаторам (Meeting)
ERROR_MEETING_TITLE_EMPTY = 'Название встречи не может быть пустым'
ERROR_MEETING_TITLE_ALREADY_IN_USE = 'Такое название встречи уже используется'
ERROR_DATE_CANNOT_BE_EARLIER = 'Дата не может быть раньше'
ERROR_DATE_MEETING_ALREADY_IN_USE = 'Дата встречи уже занята'


# Константы к валидаторам (Task)
ERROR_TASK_NAME_EMPTY = 'Название задачи не может быть пустым'
ERROR_EXECUTORS_MUST_BE_UUID_FORMAT = 'Исполнители должны быть в формате UUID'
ERROR_TASK_FOR_PROBLEM_NOT_FOUND = 'Задач для проблем нет'
ERROR_DATE_SHOULD_BE_FUTURE = 'Дата должна быть в будущем'


# Константы к схемам
TITLE_COMMENTS_TEXT_CREATE: str = 'Новый комментарий к треду.'
TITLE_COMMENTS_TEXT_UPDATE: str = 'Обновить комментарий к треду.'
TITLE_MESSAGE_FEED_IMPORTANT: str = 'Важность треда.'
TITLE_MESSAGE_FEED_TEXT: str = 'Название треда.'

# Константы к валидаторам
VALID_WRONG_COMPANY: str = 'Разрешён доступ только к своей компании.'
VALID_WRONG_PROBLEM: str = 'Разрешён доступ только к проблемам своей компании.'
VALID_WRONG_MESSAGE_FEED: str = 'Для указанной проблемы запрошенный тред не найден.'
VALID_WRONG_COMMENT: str = 'Для указанного треда запрашиваемый комментарий не найден'
VALID_COMMENT_NOT_OWNER: str = 'Вы можете изменять только свои комментарии.'
VALID_LIKE_OWN_COMMENT: str = 'Нельзя менять рейтинг собственного комментария.'
VALID_REPEATED_LIKE: str = 'Вы уже лайкнули данный комментарий.'
VALID_NOT_LIKED_COMMENT: str = 'Вы не лайкали данный комментарий.'
VALID_NOT_UNIQUE_RESULT_MEETING: str = 'Вы уже создали результат данной встречи.'

PHONE_REGEX = r'^\+7\d{10}$'
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
