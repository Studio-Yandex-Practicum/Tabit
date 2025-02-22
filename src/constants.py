from dataclasses import dataclass

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

ERROR_INVALID_PASSWORD_LENGTH = f'Пароль не может быть короче {MIN_LENGTH_PASSWORD} символов.'

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

TEXT_ERROR_EXISTS_EMAIL: str = 'Пользователь с такой электронной почтой уже есть'
TEXT_ERROR_INVALID_PASSWORD: str = 'Не корректный пароль'


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
