"""
Модуль констант для генерации и работы с уникальными идентификаторами.

Содержит константы, используемые для генерации уникальных строковых идентификаторов (slug),
управления путями файловой системы и обработки ошибок валидации. Организован по принципу
тематической группировки констант в логические классы.

Структура модуля:
- DirectoryConstants: пути к директориям файловой системы.
- LengthConstants: ограничения длины.
- MiscConstants: различные технические константы.
- TextErrorConstants: стандартные тексты ошибок.

Все классы наследуют соответствующие базовые классы из src.core.constants,
что обеспечивает согласованность констант во всем проекте.

Импортируемые базовые классы:
- DirectoryBaseConstants: основные пути к директориям.
- LengthBaseConstants: базовые ограничения длины.
- MiscBaseConstants: общие технические константы.
- TextErrorBaseConstants: стандартные тексты ошибок.

Важные особенности:
- Все классы наследуют соответствующие базовые классы констант.
- Дополнительные константы добавляются в дочерние классы.
- Гибкие настройки для генерации slug-идентификаторов.
- Все строковые константы должны быть типизированы.
- Все константы имеют явные type hints (аннотации типов).
- Наследуемые значения могут быть переопределены.

Примеры использования:
- from src.utils.constants import DirectoryConstants
- waif_path = DirectoryConstants.WAIF  # Получение пути к директории
"""

import string

from src.core.constants import (
    DirectoryBaseConstants,
    LengthBaseConstants,
    MiscBaseConstants,
    TextErrorBaseConstants,
)


class DirectoryConstants(DirectoryBaseConstants):
    """
    Класс констант путей к директориям.

    Наследует все константы из DirectoryBaseConstants.

    Атрибуты:
    - WAIF (str): Относительный путь к директории, связанной с функционалом 'waif'.
    """

    WAIF: str = 'waif'


class LengthConstants(LengthBaseConstants):
    """
    Класс для хранения констант, связанных с допустимой длиной полей.

    Наследует все константы из LengthBaseConstants.

    Атрибуты:
    - GENERATED_SLUG_SUFFIX_RANGE (int): Длина суффикса, добавляемого к сгенерированным slug'ам.
    """

    GENERATED_SLUG_SUFFIX_RANGE: int = 3


class MiscConstants(MiscBaseConstants):
    """
    Класс для хранения различных текстовых констант.

    Наследует все константы из MiscBaseConstants.

    Атрибуты:
    - SHORT_SYMBOLS (str): Набор символов, которые могут использоваться для
      генерации коротких строк.
      По умолчанию содержит все буквы латинского алфавита.
    """

    SHORT_SYMBOLS: str = string.ascii_letters


class TextErrorConstants(TextErrorBaseConstants):
    """
    Класс для хранения стандартных текстов ошибок приложения.

    Наследует все константы из TextErrorBaseConstants.

    Примеры:
    - INVALID_PASSWORD (str): Сообщение о невалидном пароле.
    - INVALID_TELEGRAM_USERNAME (str): Сообщение о занятом Telegram username и т.д.
    """
