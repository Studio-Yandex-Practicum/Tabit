"""
Модуль констант приложения.

Содержит глобальные константы, используемые во всем проекте.
Все константы должны быть написаны в UPPER_CASE нотации.

Примеры использования:
    from src import constants
    print(constants.BASE_DIR)

Константы разделены на логические группы с комментариями.
Новые константы должны добавляться в соответствующие секции.

Примечания:
    - Не рекомендуется изменять значения констант во время выполнения
    - Все числовые константы должны иметь поясняющий комментарий
    - Строковые константы должны быть документально оформлены
    - Сложные константы должны содержать примеры значений
"""

from pathlib import Path


class DefaultBase:
    """Базовый класс констант значений по умолчанию для пагинации и лимитов.

    Атрибуты:
        LIMIT (int): Максимальный лимит элементов.
        PAGE_SIZE (int): Размер страницы по умолчанию.
        SKIP (int): Значение по умолчанию для пропуска элементов.
    """

    LIMIT: int = 100
    PAGE_SIZE: int = 20
    SKIP: int = 0


class DescriptionBase:
    """Базовый класс для текстовых описаний."""


class DirectoryBase:
    """Базовый класс констант путей к директориям.

    Атрибуты:
        LOGO (str): Название поддиректории для логотипов.
        MEDIA (str): Название директории для медиафайлов.
    """

    LOGO: str = 'logo'
    MEDIA: str = 'media'


class LengthBase:
    """Константы, определяющие ограничения длины для различных полей.

    Атрибуты:
        FILE_LINK (int): Максимальная длина ссылки на файл.
        MAX_NAME (int): Максимальная длина имени.
        MAX_NAME_COMPANY (int): Максимальная длина названия компании.
        MAX_TELEGRAM_USERNAME (int): Максимальная длина Telegram username.
        MIN_PASSWORD (int): Минимальная длина пароля.
        SLUG (int): Максимальная длина slug.
    """

    FILE_LINK: int = 2048
    MAX_NAME: int = 100
    MAX_NAME_COMPANY: int = 255
    MAX_TELEGRAM_USERNAME: int = 100
    MIN_PASSWORD: int = 8
    SLUG: int = 110


class MiscConstantsBase:
    """Базовые константы приложения разного назначения.

    Атрибуты:
        BASE64_STARTSWITH (str): Префикс строк base64 для изображений.
        BASE_DIR (Path): Корневая директория проекта.
        ZERO (int): Числовая константа нуля для унификации.
    """

    BASE64_STARTSWITH: str = 'data:image'
    BASE_DIR = Path(__file__).resolve().parent.parent
    ZERO: int = 0


class SummaryBase:
    """Базовый класс для констант-описаний."""


class TextErrorBase:
    """Базовый класс для хранения стандартных текстов ошибок приложения.

    Атрибуты:
        BASE64_FATAL (str): Шаблон сообщения об ошибке сохранения изображения.
        BASE64_TYPE (str): Сообщение о неверном формате base64.
        EXISTS_EMAIL (str): Сообщение о существующем email.
        INVALID_PASSWORD (str): Сообщение о невалидном пароле.
        INVALID_TELEGRAM_USERNAME (str): Сообщение о занятом Telegram username.
        NOT_FOUND (str): Шаблон сообщения об отсутствии объекта.
    """

    BASE64_FATAL: str = 'Ошибка при сохранение картинки {image}: {error_class}: {error_text}'
    BASE64_TYPE: str = (
        'Переданный файл не является строкой начинающийся '
        f'на с {MiscConstantsBase.BASE64_STARTSWITH}'
    )
    EXISTS_EMAIL: str = 'Пользователь с такой электронной почтой уже существует.'
    INVALID_PASSWORD: str = (
        'Пароль должен содержать символы латинского алфавита в обоих регистрах, '
        f'числа и иметь минимальную длину в {LengthBase.MIN_PASSWORD} символов.'
    )
    INVALID_TELEGRAM_USERNAME: str = 'Пользователь с указанным Telegram username уже существует.'
    NOT_FOUND: str = 'Не найден объект {obj} по данному id: {id}'


class TitleBase:
    """Базовый класс для констант-заголовков."""


class ValidationBase:
    """Базовый класс регулярных выражений для валидации данных.

    Атрибуты:
        EMAIL_REGEX (str): Регулярное выражение для валидации email.
        PHONE_NUMBER_PATTERN (str): Регулярное выражение для российских номеров (начинаются с 7).
        PHONE_REGEX (str): Регулярное выражение для номеров в формате +7.
        TELEGRAM_USERNAME_PATTERN (str): Регулярное выражение для Telegram username.
    """

    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    # Нужно понять, какое выражение оставляем для номера телефона с + или без
    PHONE_NUMBER_PATTERN = r'^7\d{10}'
    PHONE_REGEX = r'^\+7\d{10}$'
    TELEGRAM_USERNAME_PATTERN = r'\w+'
