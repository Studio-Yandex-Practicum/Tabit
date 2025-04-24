from config.constants.src import DefaultBase, DirectoryBase, MiscConstantsBase, TextErrorBase


class Default(DefaultBase):
    """Класс констант значений по умолчанию для пагинации и лимитов.

    Наследует все константы из DefaultBase.

    Атрибуты:
        AUTO_COMMIT (bool): Флаг автоматического коммита по умолчанию.
    """

    AUTO_COMMIT: bool = True


class Directory(DirectoryBase):
    """Класс констант путей к директориям.

    Наследует все константы из DirectoryBase. Примеры:
    - LOGO (str): Название поддиректории для логотипов.
    - MEDIA (str): Название директории для медиафайлов и т.д.
    """


class MiscConstants(MiscConstantsBase):
    """Различные константы приложения.

    Содержит константы, которые не относятся к другим конкретным категориям.

    Наследует все константы из MiscConstantsBase. Примеры:
    - BASE_DIR (Path): Корневая директория проекта.
    - ZERO (int): Числовая константа нуля для унификации и т.д.
    """


class TextError(TextErrorBase):
    """Класс для хранения стандартных текстов ошибок приложения.

    Наследует все константы из TextErrorBase.

    Атрибуты:
        CREATE_SERVER (str): Сообщение об ошибке при создании объекта.
        CREATE_SERVER_LOG (str): Лог ошибки при создании.
        CREATE_UNIQUE_LOG (str): Лог ошибки уникальности при создании.
        DELETE_SERVER_LOG (str): Лог ошибки при удалении.
        INTERNAL_SERVER (str): Сообщение о внутренней ошибке сервера.
        NOT_FOUND_BY_SLUG (str): Сообщение если объект не найден по slug.
        UNIQUE (str): Сообщение об ошибке уникальности.
        UPDATE_SERVER_LOG (str): Лог ошибки при обновлении.
        USER_ALREADY_EXISTS (str): Сообщение если пользователь уже существует.
        USER_NOT_EXISTS (str): Сообщение если пользователь не существует.
    """

    CREATE_SERVER: str = 'Ошибка сервера при создании объекта.'
    CREATE_SERVER_LOG: str = 'Ошибка при создании'
    CREATE_UNIQUE_LOG: str = 'Ошибка уникальности при создании'
    DELETE_SERVER_LOG: str = 'Ошибка при удалении'
    INTERNAL_SERVER: str = 'Внутренняя ошибка сервера.'
    NOT_FOUND_BY_SLUG: str = 'Не найден объект {obj} по данному slug: {slug}'
    UNIQUE: str = 'Ошибка уникальности. Такой объект уже существует.'
    UPDATE_SERVER_LOG: str = 'Ошибка при обновлении'
    USER_ALREADY_EXISTS: str = 'Пользователь с данным email уже существует.'
    USER_NOT_EXISTS: str = 'Пользователь с таким UUID не существует.'
