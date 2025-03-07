from re import compile

DEFAULT_NUMBER_DEY_LICENSE: int = 1
DEFAULT_LICENSE_TERM: dict[str, int] = {'days': 1}

TITLE_NAME_LICENSE: str = 'Название лицензии'
TITLE_LICENSE_TERM: str = 'Срок действия лицензии в днях'
TITLE_MAX_ADMINS_COUNT: str = 'Максимальное количество админов'
TITLE_MAX_EMPLOYEES_COUNT: str = 'Максимальное количество сотрудников'
TITLE_NAME_ADMIN: str = 'Имя админа сервиса'
TITLE_SURNAME_ADMIN: str = 'Фамилия админа сервиса'
TITLE_PATRONYMIC_ADMIN: str = 'Отчество админа сервиса'
TITLE_PHONE_NUMBER_ADMIN: str = 'Контактный телефон админа сервиса'
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
