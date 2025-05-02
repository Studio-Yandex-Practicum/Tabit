"""
Модуль констант приложения.

Содержит константы, используемые в бизнес-логике приложения.
Организован по принципу тематической группировки констант в классах-контейнерах.

Структура модуля:
- DefaultConstants: параметры по умолчанию для системных настроек.
- LengthConstants: ограничения длины.
- MiscConstants: различные технические константы.

Все классы наследуют соответствующие базовые классы из src.core.constants,
что обеспечивает согласованность констант во всем проекте.

Импортируемые базовые классы:
- DefaultBaseConstants: базовые значения по умолчанию.
- LengthBaseConstants: базовые ограничения длины.
- MiscBaseConstants: базовые общие технические константы.

Важные особенности:
- Все классы наследуют соответствующие базовые классы констант.
- Дополнительные константы добавляются в дочерние классы.
- Все строковые константы должны быть типизированы.
- Все константы имеют явные type hints (аннотации типов).
- Наследуемые значения могут быть переопределены.

Примеры использования:
- from src.models.constants import DefaultConstants, LengthConstants
- license_days = DefaultConstants.LICENSE_TERM
- max_dept_name_len = LengthConstants.MAX_NAME_DEPARTMENT
"""

from src.core.constants import DefaultBaseConstants, LengthBaseConstants, MiscBaseConstants


class DefaultConstants(DefaultBaseConstants):
    """
    Класс констант значений по умолчанию для пагинации и лимитов.

    Наследует все константы из DefaultBaseConstants.

    Атрибуты:
    - LICENSE_TERM (int): Количество дней действия лицензии по умолчанию.
    """

    LICENSE_TERM: int = 1


class LengthConstants(LengthBaseConstants):
    """
    Класс для хранения констант, связанных с допустимой длиной полей.

    Наследует все константы из LengthBaseConstants.

    Атрибуты:
    - MAX_NAME_DEPARTMENT (int): Максимальная длина названия отдела.
    - MAX_NAME_MEETING_PLACE (int): Максимальная длина названия места встречи.
    - MAX_NAME_PROBLEM (int): Максимальная длина названия проблемы.
    """

    MAX_NAME_DEPARTMENT: int = 100
    MAX_NAME_MEETING_PLACE: int = 100
    MAX_NAME_PROBLEM: int = 100
    MAX_NAME_MEETING: int = 100
    MAX_NAME_TASK: int = 100


class MiscConstants(MiscBaseConstants):
    """
    Различные константы приложения.

    Содержит константы, которые не относятся к другим конкретным категориям.

    Наследует все константы из MiscBaseConstants.

    Примеры:
    - BASE_DIR (Path): Корневая директория проекта.
    - ZERO (int): Числовая константа нуля для унификации и т.д.
    """
