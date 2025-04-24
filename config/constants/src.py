"""
Модуль констант пакета `src`.

Содержит глобальные константы, используемые в пакете `src`.
Все константы должны быть написаны в UPPER_CASE нотации.

Примеры использования:
    from config.constants.src import MiscConstantsBase
    print(MiscConstantsBase.BASE_DIR)

Константы разделены на логические группы с комментариями.
Новые константы должны добавляться в соответствующие секции.

Примечания:
    - Не рекомендуется изменять значения констант во время выполнения
    - Все числовые константы должны иметь поясняющий комментарий
    - Строковые константы должны быть документально оформлены
    - Сложные константы должны содержать примеры значений
    - Все пути вычисляются относительно расположения этого файла
"""

from dataclasses import dataclass
from pathlib import Path

from config.constants.core import ConstantsBase


class DefaultBase(ConstantsBase.Default):
    """Базовый класс констант значений по умолчанию для пагинации и лимитов,
    используемых в пакете `src`.

    Так же класс наследует значения из ConstantsBase.Default.

    Атрибуты:
        LIMIT (int): Максимальный лимит элементов.
        SKIP (int): Значение по умолчанию для пропуска элементов.
    """

    LIMIT: int = 100
    SKIP: int = 0


class DescriptionBase(ConstantsBase.Description):
    """Базовый класс для текстовых описаний, используемых в пакете `src`.

    Так же класс наследует значения из ConstantsBase.Description.
    """


class DirectoryBase(ConstantsBase.Directory):
    """Базовый класс констант путей к директориям, используемых в пакете `src`.

    Так же класс наследует значения из ConstantsBase.Directory.
    """


class LengthBase(ConstantsBase.Length):
    """Базовый класс констант, определяющих ограничения длины для различных полей,
    используемых в пакете `src`.

    Так же класс наследует значения из ConstantsBase.Length.

    Атрибуты:
        FILE_LINK (int): Максимальная длина ссылки на файл.
        MAX_NAME (int): Максимальная длина имени.
        MAX_NAME_COMPANY (int): Максимальная длина названия компании.
        MAX_TELEGRAM_USERNAME (int): Максимальная длина Telegram username.
        MIN_PASSWORD (int): Минимальная длина пароля.
        SLUG (int): Максимальная длина slug.
    """

    FILE_LINK: int = 2048
    MAX_NAME_COMPANY: int = 255
    MAX_TELEGRAM_USERNAME: int = 100
    MIN_PASSWORD: int = 8
    SLUG: int = 110


@dataclass(frozen=True)
class MiscConstantsBase(ConstantsBase.MiscConstants):
    """Базовый класс разных общесистемных констант, используемых в пакете `src`.

    Класс реализован, как неизменяемый.

    Так же класс наследует значения из ConstantsBase.MiscConstants.

    Атрибуты:
        BASE_DIR (Path): Корневая директория проекта.
    """

    BASE_DIR: Path = Path(__file__).resolve().parents[2]


class SummaryBase(ConstantsBase.Summary):
    """Базовый класс констант кратких описаний, используемых в пакете `src`.

    Так же класс наследует значения из ConstantsBase.Summary.
    """


class TextErrorBase(ConstantsBase.TextError):
    """Базовый класс для хранения стандартных текстов ошибок,
    используемых в пакете `src`.

    Так же класс наследует значения из ConstantsBase.TextError.

    Атрибуты:
        EXISTS_EMAIL (str): Сообщение о существующем email.
        INVALID_PASSWORD (str): Сообщение о невалидном пароле.
        NOT_FOUND (str): Шаблон сообщения об отсутствии объекта.
    """

    EXISTS_EMAIL: str = 'Пользователь с такой электронной почтой уже существует.'
    INVALID_PASSWORD: str = (
        'Пароль должен содержать символы латинского алфавита в обоих регистрах, '
        f'числа и иметь минимальную длину в {LengthBase.MIN_PASSWORD} символов.'
    )
    NOT_FOUND: str = 'Не найден объект {obj} по данному id: {id}'


class TitleBase(ConstantsBase.Title):
    """Базовый класс констант-заголовков, используемых в пакете `src`.

    Так же класс наследует значения из ConstantsBase.Title.
    """


@dataclass(frozen=True)
class ValidationBase(ConstantsBase.Validation):
    """Базовый класс для валидации данных, используемых в пакете `src`.

    Класс реализован, как неизменяемый.

    Так же класс наследует значения из ConstantsBase.Validation.

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
