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

ERROR_FIELD_INTERVAL = (
    'Поле не может быть пустым. '
    'Может быть целым числом, или строкой, обозначающее целое число, '
    'или строкой формата "P1D", "P1Y", "P1Y1D".'
)
ERROR_FIELD_START_OR_END_SPACE = 'Поле не может начинаться или заканчиваться пробелом.'
ERROR_UPDATE_METHOD = 'Пользователь с указанными email и/или phone_number уже существует.'
