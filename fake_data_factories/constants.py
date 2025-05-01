"""
Модуль констант для генерации тестовых данных в Faker-сидерах пакета `fake_data_factories`.

Содержит все необходимые константы для работы фабрик тестовых данных:
- Цветовые константы для консольного вывода.
- Значения по умолчанию для генерации сущностей.
- Параметры для Faker.
- Ограничения длины полей.
- Различные системные константы.

Структура модуля:
- ColorCPrintConstants: цвета для форматированного вывода в консоль.
- DefaultConstants: параметры по умолчанию для системных настроек.
- FakerConstants: настройки генератора фейковых данных.
- LengthConstants: ограничения длины.
- MiscConstants: различные технические константы.

Импортируемые базовые классы:
- ConstantsBase.Default: базовые значения по умолчанию.
- ConstantsBase.Length: базовые ограничения длины.
- ConstantsBase.MiscConstants: базовые технические константы.

Важные особенности::
- Все классы наследуют соответствующие базовые классы констант.
- Дополнительные константы добавляются в дочерние классы.
- Неизменяемые классы помечены @dataclass(frozen=True).
- Все строковые константы типизированы.
- Значения подобраны для реалистичной генерации тестовых данных.

Пример использования:
- from fake_data_factories.constants import DefaultConstants, FakerConstants
- dept_name = random.choice(DefaultConstants.DEPARTMENT_NAMES)
- user_count = FakerConstants.USER_COUNT
"""

from dataclasses import dataclass

from src.core.constants import DefaultBaseConstants, LengthBaseConstants, MiscBaseConstants


@dataclass(frozen=True)
class ColorCPrintConstants:
    """
    Класс констант - цветов для вывода текста в консоли с помощью cprint.

    Класс реализован как неизменяемый (immutable) контейнер цветовых констант.

    Атрибуты:
    - black (str): черный
    - blue (str): синий
    - cyan (str): голубой
    - dark_grey (str): темно-серый
    - green (str): зеленый
    - light_blue (str): светло-синий
    - light_cyan (str): светло-голубой
    - light_green (str): светло-зеленый
    - light_grey (str): светло-серый
    - light_magenta (str): светло-пурпурный
    - light_red (str): светло-красный
    - light_yellow (str): светло-желтый
    - magenta (str): пурпурный
    - red (str): красный
    - white (str): белый
    - yellow (str): желтый
    """

    black: str = 'black'
    blue: str = 'blue'
    cyan: str = 'cyan'
    dark_grey: str = 'dark_grey'
    green: str = 'green'
    light_blue: str = 'light_blue'
    light_cyan: str = 'light_cyan'
    light_green: str = 'light_green'
    light_grey: str = 'light_grey'
    light_magenta: str = 'light_magenta'
    light_red: str = 'light_red'
    light_yellow: str = 'light_yellow'
    magenta: str = 'magenta'
    red: str = 'red'
    white: str = 'white'
    yellow: str = 'yellow'


class DefaultConstants(DefaultBaseConstants):
    """
    Класс констант значений по умолчанию, используемых в пакете `fake_data_factories`.

    Так же класс наследует значения из DefaultBaseConstants.

    Атрибуты:
    - DEPARTMENT_NAMES (list): список названий отделов по умолчанию
    - LICENSE_TERM (int): срок действия лицензии по умолчанию (в днях)
    - PATRONYMIC (list): Список распространенных отчеств для генерации ФИО сотрудников
    - PROBLEM_DESCRIPTIONS (list): описания проблем по умолчанию
    - PROBLEM_NAMES (list): названия проблем по умолчанию
    - TASK_NAMES (list): названия задач по умолчанию
    """

    DEPARTMENT_NAMES: list[str] = [
        'IT-отдел',
        'Отдел кадров',
        'Отдел менеджмента',
        'Отдел продаж',
        'Технический отдел',
    ]
    LICENSE_TERM: int = 365
    PATRONYMIC: list[str] = [
        'Александрович',
        'Алексеевич',
        'Дмитриевич',
        'Евгеньевич',
        'Иванович',
        'Петрович',
        'Сергеевич',
        'Николаевич',
        'Федосеивич',
    ]
    PROBLEM_DESCRIPTIONS: list[str | None] = [
        None,
        'Из проектов исчезло поле с дедлайном.',
        'Общение через почту слишком неэффективно.',
        'Проблемы возникают на этапе взаимодействия с менеджерами.',
        'Слишком много времени тратится впустую.',
    ]
    PROBLEM_NAMES: list[str] = [
        'Медленный отклик на заявку',
        'Несоблюдение делового стиля общения',
        'Нехватка персонала',
        'Неэффективные встречи',
        'Переносы сроков проектов',
    ]
    TASK_NAMES: list[str] = [
        'Пересмотреть активные сделки',
        'Подготовить список клиентов, которые заказали на сумму менее 500 тыс.',
        'Подготовить отчётность о сделках за последний квартал',
        'Позвонить клиентам, которые давно к нам не обращались',
        'Разработка новой формы договора',
        'Собрать список незакрытых сделок',
    ]


class FakerConstants:
    """
    Класс констант - основных параметров генерации тестовых данных с помощью Faker,
    используемых в пакете `fake_data_factories`.

    Атрибуты:
    - AMOUNT_OF_MODERATORS (int): количество модераторов на компанию
    - COMMENT_COUNT (int): количество комментариев
    - COMMENT_WORDS_COUNT (int): количество слов в комментарии
    - COMPANY_COUNT (int): количество компаний
    - DEPARTMENT_COUNT (int): количество отделов
    - MAX_COMMENT_RATING (int): максимальный рейтинг комментария
    - MESSAGE_FEEDS_COUNT (int): количество лент сообщений
    - MIN_COMMENT_RATING (int): минимальный рейтинг комментария
    - PROBLEMS_COUNT (int): количество проблем
    - TASK_COUNT (int): количество задач
    - USER_COUNT (int): количество пользователей
    - USER_TAGS_COUNT (int): количество тегов пользователя
    - VOTING_FEEDS_COUNT (int): количество лент голосований
    """

    AMOUNT_OF_MODERATORS: int = 1
    COMMENT_COUNT: int = 5
    COMMENT_WORDS_COUNT: int = 7
    COMPANY_COUNT: int = 5
    DEPARTMENT_COUNT: int = 5
    MAX_COMMENT_RATING: int = 5
    MESSAGE_FEEDS_COUNT: int = 5
    MIN_COMMENT_RATING: int = 0
    PROBLEMS_COUNT: int = 5
    TASK_COUNT: int = 5
    USER_COUNT: int = 5
    USER_TAGS_COUNT: int = 3
    VOTING_FEEDS_COUNT: int = 5


class LengthConstants(LengthBaseConstants):
    """
    Класс констант, определяющих ограничения длины для различных полей,
    используемых в пакете `fake_data_factories`.

    Так же класс наследует значения из LengthBaseConstants.

    Атрибуты:
    - LICENSE_MAX_ADMINS (int): максимальное количество администраторов
    - LICENSE_MAX_EMPLOYEES (int): максимальное количество сотрудников
    - LICENSE_TYPE_COUNT (int): количество типов лицензий
    - TASK_DESCRIPTION_LENGTH (int): длина описания задачи
    """

    LICENSE_MAX_ADMINS: int = 100
    LICENSE_MAX_EMPLOYEES: int = 1000
    LICENSE_TYPE_COUNT: int = 5
    TASK_DESCRIPTION: int = 256


@dataclass(frozen=True)
class MiscConstants(MiscBaseConstants):
    """
    Класс разных общесистемных констант, используемых в пакете `fake_data_factories`.

    Класс реализован, как неизменяемый.

    Так же класс наследует значения из MiscBaseConstants.

    Атрибуты:
    - COMPANY_USER_CREATED_TEXT (str): шаблон сообщения о создании пользователя компании.
    """

    COMPANY_USER_CREATED_TEXT: str = (
        '{role} компании c id={company_id}: {user_email}, пасс: {password}'
    )
