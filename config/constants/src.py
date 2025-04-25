"""
Модуль базовых констант `src`.

Содержит глобальные константы, используемые в пакете `src`:
- Значения по умолчанию для пагинации и лимитов.
- Текстовые описания и заголовки.
- Пути к системным директориям.
- Ограничения длины полей.
- Общие технические константы.
- Стандартные тексты ошибок.
- Правила валидации данных.

Все классы наследуют соответствующие базовые классы из ConstantsBase.

Структура модуля:
- DefaultBase: базовые параметры по умолчанию для системных настроек.
- DescriptionBase: базовые подробные описания API endpoints для документации.
- DirectoryBase: базовые пути к директориям файловой системы.
- LengthBase: базовый ограничения длины.
- MiscConstantsBase: базовые технические константы.
- SummaryBase: базовые краткие описания.
- TextErrorBase: базовые сообщения об ошибках.
- TitleBase: базовые заголовки элементов.
- ValidationBase: базовые правила валидации данных

Важные особенности:
- Неизменяемые классы помечены @dataclass(frozen=True).
- Все строковые константы типизированыю.
- Регулярные выражения документированыю.
- Пути используют Path для кроссплатформенностию и вычисляются
  относительно расположения этого файла.
- Наследуемые значения можно переопределятью.

Пример использования:
- from config.constants.src import LengthBase, TextErrorBase
- max_name_len = LengthBase.MAX_NAME
- error_msg = TextErrorBase.NOT_FOUND.format(obj="User", id=123)
"""

from dataclasses import dataclass
from pathlib import Path

from config.constants.core import ConstantsBase


class DefaultBase(ConstantsBase.Default):
    """
    Базовый класс констант значений по умолчанию для пагинации и лимитов,
    используемых в пакете `src`.

    Так же класс наследует значения из ConstantsBase.Default.

    Атрибуты:
    - LIMIT (int): Максимальный лимит элементов.
    - SKIP (int): Значение по умолчанию для пропуска элементов.
    """

    LIMIT: int = 100
    SKIP: int = 0


class DescriptionBase(ConstantsBase.Description):
    """
    Базовый класс констант для текстовых описаний, используемых в пакете `src`.

    Так же класс наследует значения из ConstantsBase.Description.
    """


class DirectoryBase(ConstantsBase.Directory):
    """
    Базовый класс констант путей к директориям, используемых в пакете `src`.

    Так же класс наследует значения из ConstantsBase.Directory.
    """


class LengthBase(ConstantsBase.Length):
    """
    Базовый класс констант, определяющих ограничения длины для различных полей,
    используемых в пакете `src`.

    Так же класс наследует значения из ConstantsBase.Length.

    Атрибуты:
    - FILE_LINK (int): Максимальная длина ссылки на файл.
    - MAX_NAME (int): Максимальная длина имени.
    - MAX_NAME_COMPANY (int): Максимальная длина названия компании.
    - MAX_TELEGRAM_USERNAME (int): Максимальная длина Telegram username.
    - MIN_PASSWORD (int): Минимальная длина пароля.
    - SLUG (int): Максимальная длина slug.
    """

    FILE_LINK: int = 2048
    MAX_NAME_COMPANY: int = 255
    MAX_TELEGRAM_USERNAME: int = 100
    MIN_PASSWORD: int = 8
    SLUG: int = 110


@dataclass(frozen=True)
class MiscConstantsBase(ConstantsBase.MiscConstants):
    """
    Базовый класс разных общесистемных констант, используемых в пакете `src`.

    Класс реализован, как неизменяемый.

    Так же класс наследует значения из ConstantsBase.MiscConstants.

    Атрибуты:
    - BASE_DIR (Path): Корневая директория проекта.
    """

    BASE_DIR: Path = Path(__file__).resolve().parents[2]


class SummaryBase(ConstantsBase.Summary):
    """Базовый класс констант кратких описаний, используемых в пакете `src`.

    Так же класс наследует значения из ConstantsBase.Summary.
    """


class TextErrorBase(ConstantsBase.TextError):
    """
    Базовый класс констант для хранения стандартных текстов ошибок,
    используемых в пакете `src`.

    Так же класс наследует значения из ConstantsBase.TextError.

    Атрибуты:
    - EXISTS_EMAIL (str): Сообщение о существующем email.
    - INVALID_PASSWORD (str): Сообщение о невалидном пароле.
    - NOT_FOUND (str): Шаблон сообщения об отсутствии объекта.
    """

    EXISTS_EMAIL: str = 'Пользователь с такой электронной почтой уже существует.'
    INVALID_PASSWORD: str = (
        'Пароль должен содержать символы латинского алфавита в обоих регистрах, '
        f'числа и иметь минимальную длину в {LengthBase.MIN_PASSWORD} символов.'
    )
    NOT_FOUND: str = 'Не найден объект {obj} по данному id: {id}'


class TitleBase(ConstantsBase.Title):
    """
    Базовый класс констант - заголовков, используемых в пакете `src`.

    Так же класс наследует значения из ConstantsBase.Title.
    """


@dataclass(frozen=True)
class ValidationBase(ConstantsBase.Validation):
    """
    Базовый класс констант для валидации данных, используемых в пакете `src`.

    Класс реализован, как неизменяемый.

    Так же класс наследует значения из ConstantsBase.Validation.

    Атрибуты:
    - EMAIL_REGEX (str): Регулярное выражение для валидации email.
    - PHONE_NUMBER_PATTERN (str): Регулярное выражение для валидации телефонных номеров.
    - TELEGRAM_USERNAME_PATTERN (str): Регулярное выражение для Telegram username.
    """

    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    # TODO: Откорректировать формат телефона о требованию фронтэнда
    PHONE_NUMBER_PATTERN: str = r'^(?!.*([\-\(\) ])\1)(?=.*\d)\+*[\d\-\(\) ]+$'
    TELEGRAM_USERNAME_PATTERN = r'\w+'
