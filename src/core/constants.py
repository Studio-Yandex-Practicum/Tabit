from src.constants import LengthBase, MiscConstantsBase, TextErrorBase, ValidationBase


class Length(LengthBase):
    """Класс для хранения констант, связанных с допустимой длиной полей.

    Наследует все константы из LengthBase. Примеры возможных полей:
    - MAX_NAME: максимальная длина имени.
    - MIN_PASSWORD (int): Минимальная длина пароля и т. д.
    """


class Logging:
    """Класс для хранения настроек логирования приложения.

    Атрибуты:
        FAKE_DB_DATA_LOG_FILE: Путь к файлу логов для фейковых данных БД.
        LOG_FILE: Путь к основному файлу логов.
        LOG_RETENTION: Срок хранения логов (например, '7 days').
        LOG_ROTATION: Периодичность ротации логов (например, '1 day').
    """

    FAKE_DB_DATA_LOG_FILE: str = 'logs/fake_db_data.log'
    LOG_FILE: str = 'logs/tabit.log'
    LOG_RETENTION: str = '7 days'
    LOG_ROTATION: str = '1 day'


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
        FORBIDDEN_ROLE_ADMIN: Сообщение об ошибке доступа для действий,
            требующих прав администратора компании.
    """

    FORBIDDEN_ROLE_ADMIN: str = 'Доступно только админам компаний'


class Validation(ValidationBase):
    """Класс для хранения правил валидации данных.

    Наследует все константы из ValidationBase.

    Атрибуты:
        PATTERN_PASSWORD: Регулярное выражение для проверки сложности пароля.
            Требования:
            - минимум одна строчная буква,
            - минимум одна заглавная буква,
            - минимум одна цифра,
            - только латинские буквы и цифры,
            - минимальная длина из Length.MIN_PASSWORD.
    """

    PATTERN_PASSWORD: str = (
        rf'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{{{Length.MIN_PASSWORD},}}$'
    )
