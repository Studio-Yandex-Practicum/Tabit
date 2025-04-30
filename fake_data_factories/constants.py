"""Константы для генерации тестовых данных в Faker-сидерах"""

from dataclasses import dataclass

# Основные параметры генерации
FAKER_USER_COUNT = 5  # Число пользователей для генерации
FAKER_COMPANY_COUNT = 5  # Число компаний для генерации
FAKER_DEPARTMENT_COUNT = 5  # Число отделов для генерации
FAKER_PROBLEMS_COUNT: int = 5  # Число проблем для генерации
FAKER_MEETINGS_COUNT: int = 5  # Число встреч для генерации
FAKER_MEETINGS_RESULT_COUNT: int = 5  # Число результатов встреч для генерации
FAKER_MESSAGE_FEEDS_COUNT: int = 5  # Число лент сообщений для генерации
FAKER_VOTING_FEEDS_COUNT: int = 5  # Число лент голосований для генерации
FAKER_TASK_COUNT: int = 5  # Число задач для генерации
FAKER_COMMENT_COUNT: int = 2  # Число комментариев для генерации
FAKER_COMMENT_WORDS_COUNT: int = 7  # Количество слов в комментарии
FAKER_MIN_COMMENT_RATING: int = 0  # Минимальный рейтинг комментария
FAKER_MAX_COMMENT_RATING: int = 3  # Максимальный рейтинг комментария
FAKER_USER_TAGS_COUNT: int = 3  # Число тэгов для генерации
AMOUNT_OF_MODERATORS = 1  # Количество модераторов создаваемых для компании за 1 запуск скрипта

# Параметры лицензий
LICENSE_TYPE_COUNT = 5
DEFAULT_LICENSE_TERM = 365
LICENSE_MAX_ADMINS = 100
LICENSE_MAX_EMPLOYEES = 1000

# Текстовые константы
COMPANY_USER_CREATED_TEXT = '{role} компании c id={company_id}: {user_email}, пасс: {password}'
DEFAULT_TASK_DESCRIPTION_LENGTH: int = 256

# Списки значений по умолчанию
DEFAULT_DEPARTMENT_NAMES = [
    'Отдел кадров',
    'Отдел менеджмента',
    'Отдел продаж',
    'IT-отдел',
    'Технический отдел',
]  # Имена для отделов компании

DEFAULT_PROBLEM_NAMES: list[str] = [
    'Нехватка персонала',
    'Медленный отклик на заявку',
    'Несоблюдение делового стиля общения',
    'Переносы сроков проектов',
    'Неэффективные встречи',
]

DEFAULT_PROBLEM_DESCRIPTIONS: list[str | None] = [
    None,
    'Проблемы возникают на этапе взаимодействия с менеджерами.',
    'Из проектов исчезло поле с дедлайном.',
    'Слишком много времени тратится впустую.',
    'Общение через почту слишком неэффективно.',
]

DEFAULT_MEETING_TITLES: list[str] = [
    'Узкие места процессов.',
    'Технический долг команды.',
    'Пицца или суши?',
    'Практики ревью кода.',
    'Улучшение взаимодействия с клиентом.',
]

DEFAULT_MEETING_FEEDBACK: list[str] = [
    None,
    'Всё прошло отлично, разобрали все темы.',
    'Часть тем не успели разобрать. Сделаем на следующей встрече.',
    'Было очень мало людей, встречу отменили.',
    'А где все?',
]

DEFAULT_MEETING_DESCRIPTIONS: list[str | None] = [
    None,
    'Будем обсуждать обсуждения.',
    'Что можем делать немного лучше.',
    'Окончательное голосование: Coca-cola или Pepsi.',
    'Как улучшить качество и взаимодействие внутри команды.',
]

DEFAULT_MEETING_PLACES: list[str] = ['Офис 000', 'Офис 422', 'Офис 500', 'Подвал', 'MS Teams']

DEFAULT_TASK_NAMES: list[str] = [
    'Разработка новой формы договора',
    'Пересмотреть активные сделки',
    'Собрать список незакрытых сделок',
    'Позвонить клиентам, которые давно к нам не обращались',
    'Подготовить список клиентов, которые заказали на сумму менее 500 тыс.',
    'Подготовить отчётность о сделках за последний квартал',
]


@dataclass
class ColorCPrint:
    """Набор цветов для cprint."""

    black: str = 'black'
    red: str = 'red'
    green: str = 'green'
    yellow: str = 'yellow'
    blue: str = 'blue'
    magenta: str = 'magenta'
    cyan: str = 'cyan'
    white: str = 'white'
    light_grey: str = 'light_grey'
    dark_grey: str = 'dark_grey'
    light_red: str = 'light_red'
    light_green: str = 'light_green'
    light_yellow: str = 'light_yellow'
    light_blue: str = 'light_blue'
    light_magenta: str = 'light_magenta'
    light_cyan: str = 'light_cyan'
