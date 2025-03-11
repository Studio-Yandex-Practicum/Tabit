from dataclasses import dataclass
from pathlib import Path

# Константы для путей
BASE_DIR = Path(__file__).resolve().parent.parent

# Константы для логгирования
LOG_FILE = 'logs/tabit.log'
LOG_ROTATION = '1 day'
LOG_RETENTION = '7 days'

# Константы для валидации
MIN_LENGTH_PASSWORD: int = 8
PATTERN_PASSWORD: str = rf'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{{{MIN_LENGTH_PASSWORD},}}$'


# Константы для текстовых сообщений
@dataclass
class TextError:
    """Содержит текст сообщений об ошибке."""

    FORBIDDEN_ROLE_ADMIN: str = 'Доступно только админам компаний'
    LOGIN = 'Неверные учетные данные для входа в систему'
    IS_SUPERUSER: str = 'Объект - суперпользователь'
    DEPARTMENT_EXIST_ERROR_MESSAGE = 'Объект с таким именем уже существует.'


# Константы для CRUD операций
DEFAULT_SKIP: int = 0
DEFAULT_LIMIT: int = 100
DEFAULT_AUTO_COMMIT: bool = True

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
