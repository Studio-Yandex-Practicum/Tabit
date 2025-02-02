# TODO: создать класс Length, декорировать dataclass. Все длины упаковать в этот класс, из названий
# констант удалить слово LENGTH
MIN_LENGTH_NAME: int = 2
MIN_LENGTH_PASSWORD: int = 8
LENGTH_NAME_USER: int = 100
LENGTH_NAME_LICENSE: int = 100
LENGTH_NAME_COMPANY: int = 255
LENGTH_NAME_DEPARTMENT: int = 255
LENGTH_NAME_PROBLEM: int = 255
LENGTH_NAME_MEETING_PLACE: int = 255
LENGTH_SMALL_NAME: int = 30
LENGTH_TELEGRAM_USERNAME: int = 100
LENGTH_FILE_LINK: int = 2048
LENGTH_SLUG: int = 25

ZERO: int = 0

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
