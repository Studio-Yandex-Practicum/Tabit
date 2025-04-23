from src.constants import DefaultBase, LengthBase, MiscConstantsBase


class Default(DefaultBase):
    """Класс констант значений по умолчанию для пагинации и лимитов.

    Наследует все константы из DefaultBase.

    Атрибуты:
        NUMBER_DAY_LICENSE (int): Количество дней действия лицензии по умолчанию.
    """

    NUMBER_DAY_LICENSE: int = 1


class Length(LengthBase):
    """Класс для хранения констант, связанных с допустимой длиной полей.

    Наследует все константы из LengthBase.

    Атрибуты:
        MAX_NAME_DEPARTMENT (int): Максимальная длина названия отдела.
        MAX_NAME_MEETING_PLACE (int): Максимальная длина названия места встречи.
        MAX_NAME_PROBLEM (int): Максимальная длина названия проблемы.
        MAX_SMALL_NAME (int): Максимальная длина короткого названия.
    """

    MAX_NAME_DEPARTMENT: int = 255
    MAX_NAME_MEETING_PLACE: int = 255
    MAX_NAME_PROBLEM: int = 255
    MAX_SMALL_NAME: int = 30


class MiscConstants(MiscConstantsBase):
    """Различные константы приложения.

    Содержит константы, которые не относятся к другим конкретным категориям.

    Наследует все константы из MiscConstantsBase. Примеры:
    - BASE_DIR (Path): Корневая директория проекта.
    - ZERO (int): Числовая константа нуля для унификации и т.д.
    """
