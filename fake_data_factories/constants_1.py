"""Константы для генерации тестовых данных в Faker-сидерах.

Модуль содержит настройки и константы для генерации тестовых данных:
- Количество создаваемых объектов (пользователи, компании, отделы и т.д.)
- Текстовые шаблоны
- Списки значений по умолчанию
- Параметры генерации
"""

from dataclasses import dataclass

from src.constants import MiscConstantsBase


@dataclass(frozen=True)
class ColorCPrint:
    """Цвета для вывода текста в консоли с помощью cprint.

    Класс реализован как неизменяемый (immutable) контейнер цветовых констант.

    Атрибуты:
        black: черный
        blue: синий
        cyan: голубой
        dark_grey: темно-серый
        green: зеленый
        light_blue: светло-синий
        light_cyan: светло-голубой
        light_green: светло-зеленый
        light_grey: светло-серый
        light_magenta: светло-пурпурный
        light_red: светло-красный
        light_yellow: светло-желтый
        magenta: пурпурный
        red: красный
        white: белый
        yellow: желтый
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


class Default:
    """Списки значений по умолчанию для генерации тестовых данных.

    Атрибуты:
        DEPARTMENT_NAMES: список названий отделов по умолчанию
        LICENSE_TERM: срок действия лицензии по умолчанию (в днях)
        PROBLEM_DESCRIPTIONS: описания проблем по умолчанию
        PROBLEM_NAMES: названия проблем по умолчанию
        TASK_NAMES: названия задач по умолчанию
    """

    DEPARTMENT_NAMES: list[str] = [
        'IT-отдел',
        'Отдел кадров',
        'Отдел менеджмента',
        'Отдел продаж',
        'Технический отдел',
    ]
    LICENSE_TERM: int = 365
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


class Faker:
    """Основные параметры генерации тестовых данных с помощью Faker.

    Атрибуты:
        AMOUNT_OF_MODERATORS: количество модераторов на компанию
        COMMENT_COUNT: количество комментариев
        COMMENT_WORDS_COUNT: количество слов в комментарии
        COMPANY_COUNT: количество компаний
        DEPARTMENT_COUNT: количество отделов
        MAX_COMMENT_RATING: максимальный рейтинг комментария
        MESSAGE_FEEDS_COUNT: количество лент сообщений
        MIN_COMMENT_RATING: минимальный рейтинг комментария
        PROBLEMS_COUNT: количество проблем
        TASK_COUNT: количество задач
        USER_COUNT: количество пользователей
        USER_TAGS_COUNT: количество тегов пользователя
        VOTING_FEEDS_COUNT: количество лент голосований
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


class Length:
    """Параметры длины и ограничений для генерации данных.

    Атрибуты:
        LICENSE_MAX_ADMINS: максимальное количество администраторов
        LICENSE_MAX_EMPLOYEES: максимальное количество сотрудников
        LICENSE_TYPE_COUNT: количество типов лицензий
        TASK_DESCRIPTION_LENGTH: длина описания задачи
    """

    LICENSE_MAX_ADMINS: int = 100
    LICENSE_MAX_EMPLOYEES: int = 1000
    LICENSE_TYPE_COUNT: int = 5
    TASK_DESCRIPTION_LENGTH: int = 256


class MiscConstants(MiscConstantsBase):
    """Различные текстовые константы и параметры.

    Атрибуты:
        COMPANY_USER_CREATED_TEXT: шаблон сообщения о создании пользователя компании.
    """

    COMPANY_USER_CREATED_TEXT: str = (
        '{role} компании c id={company_id}: {user_email}, пасс: {password}'
    )
