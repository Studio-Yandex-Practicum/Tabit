"""
Базовый модуль констант проекта.

Содержит фундаментальные константы, используемые во всех компонентах системы.
Организован по принципу "контейнеров констант" - вложенных классов, группирующих
константы по функциональному назначению.

Структура модуля:
- DefaultBaseConstants: значения по умолчанию для системных настроек.
- DescriptionBaseConstants: подробные описания API endpoints для документации.
- DirectoryBaseConstants: пути к директориям файловой системы.
- LengthBaseConstants: базовые ограничения длины.
- LoggingBaseConstants: конфигурация системы логирования.
- MiscBaseConstants: базовые технические константы.
- SummaryBaseConstants: базовые краткие описания.
- TextErrorBaseConstants: базовые сообщения об ошибках.
- TitleBaseConstants: базовые заголовки элементов.
- ValidationBaseConstants: базовые правила валидации данных.

Принципы организации:
- Логическая группировка - каждая категория констант в своем классе.
- Неизменяемость - изменяемые классы помечены @dataclass(frozen=True).
- Типизация - все константы имеют явные type hints.
- Наследование - может использоваться для расширения в дочерних модулях.
- Документирование - каждый класс и значимая константа имеет docstring.

Пример использования:
- from src.core.constants import DefaultBaseConstants, DirectoryBaseConstants
- page_size = DefaultBaseConstants.PAGE_SIZE
- media_dir = DirectoryBaseConstants.MEDIA

Рекомендации:
- Для доступа к константам использовать полный путь через ConstantsBase.
- Новые константы добавлять в соответствующий тематический класс.
- Для проекто-специфичных констант создавать дочерние модули.
- Избегать дублирования констант между модулями.
"""

from dataclasses import dataclass
from pathlib import Path


class DefaultBaseConstants:
    """
    Базовый класс констант значений по умолчанию.

    Атрибуты:
    - LIMIT (int): Максимальный лимит элементов.
    - PAGE_SIZE (int): Размер страницы по умолчанию.
    - SKIP (int): Значение по умолчанию для пропуска элементов.
    """

    LIMIT: int = 100
    PAGE_SIZE: int = 20
    SKIP: int = 0


class DescriptionBaseConstants:
    """
    Базовый класс констант для текстовых описаний.
    """


class DirectoryBaseConstants:
    """
    Базовый класс констант путей к директориям.

    Атрибуты:
    - LOGO (str): Название поддиректории для логотипов.
    - MEDIA (str): Название директории для медиафайлов.
    """

    LOGO: str = 'logo'
    MEDIA: str = 'media'


class LengthBaseConstants:
    """
    Базовый класс констант, определяющих ограничения длины для различных полей.

    Атрибуты:
    - FILE_LINK (int): Максимальная длина ссылки на файл.
    - MAX_NAME (int): Максимальная длина имени.
    - MAX_NAME_COMPANY (int): Максимальная длина названия компании.
    - MAX_NAME_DEPARTMENT (int): Максимальная длина названия отдела.
    - SLUG (int): Максимальная длина slug.
    - MAX_SMALL_NAME (int): Максимальная длина короткого названия.
    - MAX_TELEGRAM_USERNAME (int): Максимальная длина Telegram username.
    - MIN_PASSWORD (int): Минимальная длина пароля.
    """

    FILE_LINK: int = 2048
    MAX_NAME: int = 100
    MAX_NAME_COMPANY: int = 255
    MAX_NAME_DEPARTMENT: int = MAX_NAME_COMPANY
    SLUG: int = MAX_NAME_COMPANY + 5
    MAX_SMALL_NAME: int = 200
    MAX_TELEGRAM_USERNAME: int = 100
    MIN_PASSWORD: int = 8


class LoggingBaseConstants:
    """
    Базовый класс констант для хранения настроек логирования приложения.

    Атрибуты:
    - FAKE_DB_DATA_LOG_FILE (str): Путь к файлу логов для фейковых данных БД.
    - LOG_FILE (str): Путь к основному файлу логов.
    - LOG_RETENTION (str): Срок хранения логов (например, '7 days').
    - LOG_ROTATION (str): Периодичность ротации логов (например, '1 day').
    """

    FAKE_DB_DATA_LOG_FILE: str = 'logs/fake_db_data.log'
    LOG_FILE: str = 'logs/tabit.log'
    LOG_RETENTION: str = '7 days'
    LOG_ROTATION: str = '1 day'


@dataclass(frozen=True)
class MiscBaseConstants:
    """
    Базовый класс разных общесистемных констант.

    Класс реализован, как неизменяемый.

    Атрибуты:
    - BASE_DIR (Path): Корневая директория проекта.
    - BASE64_STARTSWITH (str): Префикс строк base64 для изображений.
    - ONE (int): Числовая константа единицы для унификации.
    - ZERO (int): Числовая константа нуля для унификации.
    """

    BASE_DIR: Path = Path(__file__).resolve().parents[2]
    BASE64_STARTSWITH: str = 'data:image'
    ONE: int = 1
    ZERO: int = 0


class SummaryBaseConstants:
    """
    Базовый класс констант кратких описаний.
    """


class TextErrorBaseConstants:
    """
    Базовый класс констант стандартных текстов ошибок.

    Атрибуты:
    - BASE64_FATAL (str): Шаблон сообщения об ошибке сохранения изображения.
    - BASE64_TYPE (str): Сообщение о неверном формате base64.
    - EXISTS_EMAIL (str): Сообщение о существующем email.
    - FORBIDDEN_ROLE_MODERATOR (str): Сообщение об ошибке доступа для действий,
        требующих прав модератора компании.
    - INVALID_PASSWORD (str): Сообщение о невалидном пароле.
    - INVALID_TELEGRAM_USERNAME (str): Сообщение о занятом Telegram username.
    - NOT_FOUND (str): Шаблон сообщения об отсутствии объекта.
    """

    BASE64_FATAL: str = 'Ошибка при сохранение картинки {image}: {error_class}: {error_text}'
    BASE64_TYPE: str = (
        f'Переданный файл не является строкой начинающейся c {MiscBaseConstants.BASE64_STARTSWITH}'
    )
    EXISTS_EMAIL: str = 'Пользователь с такой электронной почтой уже существует.'
    FORBIDDEN_ROLE_MODERATOR: str = 'Доступно только модераторам компаний.'
    INVALID_PASSWORD: str = (
        'Пароль должен содержать символы латинского алфавита в обоих регистрах, '
        f'числа и иметь минимальную длину в {LengthBaseConstants.MIN_PASSWORD} символов.'
    )
    INVALID_TELEGRAM_USERNAME: str = 'Пользователь с указанным Telegram username уже существует.'
    NOT_FOUND: str = 'Не найден объект {obj} по данному id: {id}'


class TitleBaseConstants:
    """
    Базовый класс констант - заголовков.
    """


@dataclass(frozen=True)
class ValidationBaseConstants:
    """
    Базовый класс констант для валидации данных.

    Класс реализован, как неизменяемый.

    Атрибуты:
    - EMAIL_REGEX (str): Регулярное выражение для валидации email.
    - PATTERN_PASSWORD (str): Регулярное выражение для проверки сложности пароля.
      - Требования:
        1) Минимум одна строчная буква
        2) Минимум одна заглавная буква
        3) Минимум одна цифра
        4) Только латинские буквы и цифры
        5) Минимальная длина из Length.MIN_PASSWORD
    - PHONE_NUMBER_PATTERN (str): Регулярное выражение для валидации телефонных номеров.
    - TELEGRAM_USERNAME_PATTERN (str): Регулярное выражение для Telegram username.
    """

    EMAIL_REGEX: str = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PATTERN_PASSWORD: str = (
        rf'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{{{LengthBaseConstants.MIN_PASSWORD},}}$'
    )
    # TODO: Откорректировать формат телефона о требованию фронтэнда
    PHONE_NUMBER_PATTERN: str = r'^(?!.*([\-\(\) ])\1)(?=.*\d)\+*[\d\-\(\) ]+$'
    TELEGRAM_USERNAME_PATTERN: str = r'\w+'
