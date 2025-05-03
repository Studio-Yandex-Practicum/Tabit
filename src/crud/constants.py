"""
Модуль констант приложения.

Содержит значения по умолчанию для системных параметров, пути к критически важным директориям,
общие технические константы, стандартные тексты ошибок.
Организован в виде классов-контейнеров, сгруппированных по функциональному назначению.

Структура модуля:
- DefaultConstants: параметры по умолчанию для системных настроек.
- DirectoryConstants: пути к директориям файловой системы.
- MiscConstants: различные технические константы приложения.
- TextErrorConstants: стандартные сообщения об ошибках.

Импортируемые базовые классы:
- DefaultBaseConstants: базовые значения по умолчанию.
- DirectoryBaseConstants: основные пути к директориям.
- MiscBaseConstants: общие технические константы.
- TextErrorBaseConstants: стандартные тексты ошибок.

Важные особенности:
- Все классы наследуют соответствующие базовые классы констант.
- Дополнительные константы добавляются в дочерние классы.
- Константы путей всегда используют Path для кроссплатформенности.
- Сообщения об ошибках поддерживают .format() для параметризации.
- Все константы должны быть типизированы.
- Флаги имеют явные булевы значения.

Пример использования:
- from src.core.constants import DefaultBaseConstants, TextErrorBaseConstants
- pagination_limit = DefDefaultBaseConstantsault.PAGINATION_LIMIT
- error_msg = TextErrorBaseConstants.NOT_FOUND_BY_SLUG.format(obj="User", slug="test")
"""

from src.core.constants import (
    DefaultBaseConstants,
    DirectoryBaseConstants,
    MiscBaseConstants,
    TextErrorBaseConstants,
)


class DefaultConstants(DefaultBaseConstants):
    """
    Класс констант значений по умолчанию для пагинации и лимитов.

    Наследует все константы из DefaultBaseConstants.

    Атрибуты:
    - AUTO_COMMIT (bool): Флаг автоматического коммита.
    """

    AUTO_COMMIT: bool = True


class DirectoryConstants(DirectoryBaseConstants):
    """
    Класс констант путей к директориям.

    Наследует все константы из DirectoryBaseConstants.

    Примеры:
    - LOGO (str): Название поддиректории для логотипов.
    - MEDIA (str): Название директории для медиафайлов и т.д.
    """


class MiscConstants(MiscBaseConstants):
    """
    Класс различных константы приложения.

    Содержит константы, которые не относятся к другим конкретным категориям.

    Наследует все константы из MiscBaseConstants.

    Примеры:
    - BASE_DIR (Path): Корневая директория проекта.
    - ZERO (int): Числовая константа нуля для унификации и т.д.
    """


class TextErrorConstants(TextErrorBaseConstants):
    """
    Класс констант для хранения стандартных текстов ошибок приложения.

    Наследует все константы из TextErrorBaseConstants.

    Атрибуты:
    - CREATE_SERVER (str): Сообщение об ошибке при создании объекта.
    - CREATE_SERVER_LOG (str): Лог ошибки при создании.
    - CREATE_UNIQUE_LOG (str): Лог ошибки уникальности при создании.
    - DELETE_SERVER_LOG (str): Лог ошибки при удалении.
    - INTERNAL_SERVER (str): Сообщение о внутренней ошибке сервера.
    - NOT_IS_MEMBERS (str): Сообщение об ошибке доступа при отсутствии членства.
    - NOT_FOUND_BY_SLUG (str): Сообщение если объект не найден по slug.
    - UNIQUE (str): Сообщение об ошибке уникальности.
    - UPDATE_SERVER_LOG (str): Лог ошибки при обновлении.
    - USER_ALREADY_EXISTS (str): Сообщение если пользователь уже существует.
    - USER_NOT_EXISTS (str): Сообщение если пользователь не существует.
    """

    CREATE_SERVER: str = 'Ошибка сервера при создании объекта.'
    CREATE_SERVER_LOG: str = 'Ошибка при создании'
    CREATE_UNIQUE_LOG: str = 'Ошибка уникальности при создании'
    DELETE_SERVER_LOG: str = 'Ошибка при удалении'
    INTERNAL_SERVER: str = 'Внутренняя ошибка сервера.'
    NOT_IS_MEMBERS: str = (
        'Вы не можете принять участие в решение проблемы, так как вы не являетесь её участником.'
    )
    NOT_FOUND_BY_SLUG: str = 'Не найден объект {obj} по данному slug: {slug}'
    UNIQUE: str = 'Ошибка уникальности. Такой объект уже существует.'
    UPDATE_SERVER_LOG: str = 'Ошибка при обновлении'
    USER_ALREADY_EXISTS: str = 'Пользователь с данным email уже существует.'
    USER_NOT_EXISTS: str = 'Пользователь с таким UUID не существует.'
