import string

from src.constants import DirectoryBase, LengthBase, MiscConstantsBase, TextErrorBase


class Directory(DirectoryBase):
    """Класс констант путей к директориям.

    Наследует все константы из DirectoryBase. Примеры:

    Атрибуты:
        WAIF: Относительный путь к директории, связанной с функционалом 'waif'.
    """

    WAIF: str = 'waif'


class Length(LengthBase):
    """Класс для хранения констант, связанных с допустимой длиной полей.

    Наследует все константы из LengthBase.

    Атрибуты:
        GENERATED_SLUG_SUFFIX_RANGE: Длина суффикса, добавляемого к сгенерированным slug'ам.
    """

    GENERATED_SLUG_SUFFIX_RANGE: int = 3


class MiscConstants(MiscConstantsBase):
    """Класс для хранения различных текстовых констант.

    Наследует все константы из MiscConstantsBase.

    Атрибуты:
        SHORT_SYMBOLS: Набор символов, которые могут использоваться для генерации коротких строк.
                       По умолчанию содержит все буквы латинского алфавита.
    """

    SHORT_SYMBOLS: str = string.ascii_letters


class TextError(TextErrorBase):
    """Класс для хранения стандартных текстов ошибок приложения.

    Наследует все константы из TextErrorBase. Примеры:
    - INVALID_PASSWORD (str): Сообщение о невалидном пароле.
    - INVALID_TELEGRAM_USERNAME (str): Сообщение о занятом Telegram username и т.д.
    """
