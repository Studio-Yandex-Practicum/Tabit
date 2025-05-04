"""
Модуль констант приложения.

Содержит константы, используемые в бизнес-логике приложения.
Организован по принципу тематической группировки констант в классах-контейнерах.

Структура модуля:
- DefaultConstants: параметры по умолчанию для системных настроек.
- LengthConstants: ограничения длины.
- MiscConstantsConstants: различные технические константы.
- TextErrorConstants: стандартные тексты ошибок.
- TitleConstants: заголовки полей и элементов интерфейса.
- ValidationBaseConstants: базовые правила валидации.

Все классы наследуют соответствующие базовые классы из src.core.constants,
что обеспечивает согласованность констант во всем проекте.

Импортируемые базовые классы:
- DefaultBase: базовые значения по умолчанию.
- LengthBase: базовые ограничения длины.
- MiscBaseConstants: общие технические константы.
- TextErrorBase: стандартные тексты ошибок.
- TitleBase: базовые заголовки элементов.
- ValidationBase: базовые правила валидации.

Важные особенности:
- Все классы наследуют соответствующие базовые классы констант.
- Дополнительные константы добавляются в дочерние классы.
- Все строковые константы должны быть типизированы.
- Все константы имеют явные type hints (аннотации типов).
- Наследуемые значения могут быть переопределены.

Примеры использования:
- from src.schemas.constants import DefaultConstants, TextErrorConstants
- max_page_size = DefaultConstants.MAX_PAGE_SIZE
- phone_error = TextErrorConstants.INVALID_PHONE_NUMBER
"""

from re import Pattern, compile

from src.core.constants import (
    DefaultBaseConstants,
    LengthBaseConstants,
    MiscBaseConstants,
    TextErrorBaseConstants,
    TitleBaseConstants,
    ValidationBaseConstants,
)


class DefaultConstants(DefaultBaseConstants):
    """
    Класс констант значений по умолчанию для пагинации и лимитов.

    Наследует все константы из DefaultBaseConstants.

    Атрибуты:
    - LICENSE_TERM (dict): Срок действия лицензии по умолчанию в днях.
    - MAX_PAGE_SIZE (int): Максимальный размер страницы для пагинации.
    - MIN_PAGE_SIZE (int): Минимальный размер страницы для пагинации.
    - PAGE (int): Номер страницы по умолчанию.
    - PAGE_DESCRIPTION (str): Описание поля страницы.
    - PAGE_SIZE_DESCRIPTION (str): Описание поля размера страницы.
    """

    LICENSE_TERM: dict[str, int] = {'days': 1}
    MAX_PAGE_SIZE: int = 100
    MIN_PAGE_SIZE: int = 1
    PAGE: int = 1
    PAGE_DESCRIPTION: str = 'Текущая страница'
    PAGE_SIZE_DESCRIPTION: str = 'Количество записей на странице'


class LengthConstants(LengthBaseConstants):
    """
    Класс для хранения констант, связанных с допустимой длиной полей.

    Наследует все константы из LengthBaseConstants.

    Атрибуты:
    - MAX_ADDRESS_LENGTH (int): Максимальная длина адреса.
    - MAX_DESCRIPTION_COMPANY (int): Максимальная длина описания компании.
    - MAX_FILE_LINK_LENGTH (int): Максимальная длина ссылки на файл (например, аватар).
    - MAX_NAME (int): Максимальная длина имени.
    - MAX_PHONE_LENGTH (int): Максимальная длина телефонного номера.
    - MAX_TEXT_LENGTH (int): Максимальная длина текста.
    - MIN_DESCRIPTION (int): Минимальная длина описания.
    - MIN_NAME (int): Минимальная длина имени.
    - MIN_TELEGRAMM_USERNAME (int): Минимальная длина Telegram username.
    - MIN_TEXT_LENGTH (int): Минимальная длина текста.
    """

    MAX_ADDRESS_LENGTH: int = 255
    MAX_DESCRIPTION_COMPANY: int = 255
    MAX_FILE_LINK_LENGTH: int = 255
    MAX_NAME: int = 100
    MAX_PHONE_LENGTH: int = 100
    MAX_TEXT_LENGTH: int = 1000
    MIN_DESCRIPTION: int = 2
    MIN_NAME: int = 2
    MIN_TELEGRAMM_USERNAME: int = 5
    MIN_TEXT_LENGTH: int = 1


class MiscConstants(MiscBaseConstants):
    """
    Класс для хранения различных текстовых констант.

    Наследует все константы из MiscBaseConstants.

    Атрибуты:
    - FILTER_NAME_DESCRIPTION (str): Описание фильтра по названию лицензии.
    - SORTING_DESCRIPTION (str): Описание параметров сортировки.
    """

    FILTER_NAME_DESCRIPTION: str = 'Фильтр по названию лицензии'
    SORTING_DESCRIPTION: str = (
        "Сортировка по полю (name, created_at, updated_at) '-' "
        ' означает сортировку в обратном порядке.'
    )


class TextErrorConstants(TextErrorBaseConstants):
    """
    Класс констант для хранения стандартных текстов ошибок приложения.

    Наследует все константы из TextErrorBaseConstants.

    Атрибуты:
    - DATE_CANNOT_BE_EARLIER (str): Ошибка о невозможности указать более раннюю дату.
    - DATE_SHOULD_BE_FUTURE (str): Ошибка о необходимости указать будущую дату.
    - EXECUTORS_MUST_BE_UUID_FORMAT (str): Ошибка о формате UUID для исполнителей.
    - FIELD_INTERVAL (str): Ошибка о недопустимом формате интервала.
    - FIELD_START_OR_END_SPACE (str): Ошибка о пробелах в начале/конце поля.
    - INVALID_CHARACTERS_NAME (str): Ошибка о недопустимых символах в имени.
    - INVALID_CHARACTERS_SURNAME (str): Ошибка о недопустимых символах в фамилии.
    - INVALID_DATE (str): Ошибка о недопустимой дате.
    - INVALID_PHONE_NUMBER (str): Ошибка о неверном формате телефона.
    - INVALID_START_DATE (str): Ошибка о недопустимой дате начала.
    - INVALID_TELEGRAM_USERNAME (str): Ошибка о неверном формате Telegram username.
    - LICENSE_FIELDS (str): Ошибка о необходимости одновременного заполнения полей лицензии.
    - MEETING_TITLE_EMPTY (str): Ошибка о пустом названии встречи.
    - PROBLEM_NAME_EMPTY (str): Ошибка о пустом названии проблемы.
    - TASK_NAME_EMPTY (str): Ошибка о пустом названии задачи.
    - UNIQUE_NAME_SURNAME (str): Ошибка о совпадении имени и фамилии.
    """

    DATE_CANNOT_BE_EARLIER: str = 'Дата не может быть раньше.'
    DATE_SHOULD_BE_FUTURE: str = 'Дата должна быть в будущем.'
    EXECUTORS_MUST_BE_UUID_FORMAT: str = 'Исполнители должны быть в формате UUID.'
    FIELD_INTERVAL: str = (
        'Поле не может быть пустым. '
        'Может быть целым числом, или строкой, обозначающее целое число, '
        'или строкой формата "P1D", "P1Y", "P1Y1D".'
    )
    FIELD_START_OR_END_SPACE: str = 'Поле не может начинаться или заканчиваться пробелом.'
    INVALID_CHARACTERS_NAME: str = 'Имя содержит недопустимые символы!'
    INVALID_CHARACTERS_SURNAME: str = 'Фамилия содержит недопустимые символы!'
    INVALID_DATE: str = 'Указана некорректная дата.'
    INVALID_PHONE_NUMBER: str = 'Некорректный формат номера телефона.'
    INVALID_START_DATE: str = (
        'Параметр start_date_employment не может быть больше end_date_employment.'
    )
    INVALID_TELEGRAM_USERNAME: str = (
        'Telegram username должен состоять только из латинских букв и цифр.'
    )
    LICENSE_FIELDS: str = 'Поля начала действия лицензии и тип лицензии заполняются одновременно.'
    MEETING_TITLE_EMPTY: str = 'Название встречи не может быть пустым.'
    PROBLEM_NAME_EMPTY: str = 'Название проблемы не может быть пустым.'
    TASK_NAME_EMPTY: str = 'Название задачи не может быть пустым.'
    UNIQUE_NAME_SURNAME: str = 'Имя и фамилия не могут совпадать!'


class TitleConstants(TitleBaseConstants):
    """
    Класс констант для хранения заголовков полей.

    Наследует все константы из TitleBaseConstants.

    Атрибуты:
    - AVATAR_LINK_USER (str): Заголовок для ссылки на аватар пользователя.
    - BIRTHDAY_USER (str): Заголовок для дня рождения пользователя.
    - COMPANY_ID_TAG (str): Заголовок для ID компании тега.
    - COMPANY_ID_USER (str): Заголовок для ID компании пользователя.
    - CREATE_COMMENTS_TEXT (str): Заголовок для текста нового комментария.
    - CREATED_AT_USER (str): Заголовок для даты создания пользователя.
    - CURRENT_DEPARTMENT_ID_USER (str): Заголовок для текущего отдела пользователя.
    - DEPARTMENT_TRANSITION_DATE_USER (str): Заголовок для даты перехода между отделами.
    - EMAIL_USER (str): Заголовок для email пользователя.
    - EMPLOYEE_POSITION_USER (str): Заголовок для позиции сотрудника.
    - END_DATE_EMPLOYMENT_USER (str): Заголовок для даты окончания работы.
    - IS_ACTIVE_USER (str): Заголовок для статуса активности пользователя.
    - IS_SUPERUSER_ADMIN (str): Заголовок для статуса суперпользователя.
    - LICENSE_ID_COMPANY (str): Заголовок для ID типа лицензии компании.
    - LIMIT (str): Заголовок для лимита списка объектов.
    - LOGO_COMPANY (str): Заголовок для логотипа компании.
    - MAX_EMPLOYEES_COUNT (str): Заголовок для максимального числа сотрудников.
    - MAX_MODERATORS_COUNT (str): Заголовок для максимального числа модераторов.
    - MEETING_CREATED_AT (str): Заголовок для даты создания встречи.
    - MEETING_DATE (str): Заголовок для даты проведения встречи.
    - MEETING_DESCRIPTION (str): Заголовок для описания встречи.
    - MEETING_FEEDBACK (str): Заголовок для отзыва о встрече.
    - MEETING_ID (str): Заголовок для идентификатора встречи.
    - MEETING_MEMBER_ID (str): Заголовок для идентификатора участника встречи.
    - MEETING_MEMBERS (str): Заголовок для участников встречи.
    - MEETING_OWNER_ID (str): Заголовок для идентификатора создателя встречи.
    - MEETING_PLACE (str): Заголовок для места проведения встречи.
    - MEETING_PROBLEM_ID (str): Заголовок для идентификатора проблемы встречи.
    - MEETING_RESULT (str): Заголовок для результата встречи.
    - MEETING_STATUS (str): Заголовок для статуса встречи.
    - MEETING_TITLE (str): Заголовок для названия встречи.
    - MEETING_TRANSFER_COUNTER (str): Заголовок для количества переносов встречи.
    - MEETING_UPDATED_AT (str): Заголовок для даты обновления встречи.
    - MESSAGE_FEED_IMPORTANT (str): Заголовок для важности треда.
    - MESSAGE_FEED_TEXT (str): Заголовок для текста треда.
    - NAME_COMPANY (str): Заголовок для названия компании.
    - NAME_DEPARTMENT (str): Заголовок для названия отдела.
    - NAME_LICENSE (str): Заголовок для названия лицензии.
    - NAME_MODERATOR (str): Заголовок для имени модератора.
    - NAME_TAG (str): Заголовок для имени тега.
    - NAME_USER (str): Заголовок для имени пользователя.
    - PARTICIPANT_ENGAGEMENT (str): Заголовок для участия в встрече.
    - PASSWORD_USER (str): Заголовок для пароля пользователя.
    - PATRONYMIC_MODERATOR (str): Заголовок для отчества модератора.
    - PATRONYMIC_USER (str): Заголовок для отчества пользователя.
    - PHONE_NUMBER_MODERATOR (str): Заголовок для телефона модератора.
    - PHONE_NUMBER_USER (str): Заголовок для телефона пользователя.
    - PREVIOUS_DEPARTMENT_ID_USER (str): Заголовок для предыдущего отдела пользователя.
    - PROBLEM_COLOR (str): Заголовок для цвета проблемы.
    - PROBLEM_COMPANY_ID (str): Заголовок для идентификатора компании проблемы.
    - PROBLEM_CREATED_AT (str): Заголовок для даты создания проблемы.
    - PROBLEM_DESCRIPTION (str): Заголовок для описания проблемы.
    - PROBLEM_ID (str): Заголовок для идентификатора проблемы.
    - PROBLEM_MEMBER_ID (str): Заголовок для идентификатора участника проблемы.
    - PROBLEM_MEMBER_STATUS (str): Заголовок для статуса участия в проблеме.
    - PROBLEM_MEMBERS (str): Заголовок для участников проблемы.
    - PROBLEM_NAME (str): Заголовок для названия проблемы.
    - PROBLEM_OWNER_ID (str): Заголовок для идентификатора владельца проблемы.
    - PROBLEM_SOLUTION (str): Заголовок для решения проблемы.
    - PROBLEM_STATUS (str): Заголовок для статуса проблемы.
    - PROBLEM_TYPE (str): Заголовок для типа проблемы.
    - PROBLEM_UPDATED_AT (str): Заголовок для даты обновления проблемы.
    - ROLE_USER (str): Заголовок для роли пользователя.
    - SKIP (str): Заголовок для пропуска n объектов.
    - SLUG_COMPANY (str): Заголовок для slug компании.
    - SLUG_USER (str): Заголовок для slug пользователя.
    - START_DATE_EMPLOYMENT_USER (str): Заголовок для даты начала работы.
    - START_LICENSE_TIME_COMPANY (str): Заголовок для даты начала лицензии.
    - SURNAME_MODERATOR (str): Заголовок для фамилии модератора.
    - SURNAME_USER (str): Заголовок для фамилии пользователя.
    - TASK_CREATED_AT (str): Заголовок для даты создания задачи.
    - TASK_DATE_COMPLETION (str): Заголовок для даты выполнения задачи.
    - TASK_DESCRIPTION (str): Заголовок для описания задачи.
    - TASK_EXECUTOR_ID (str): Заголовок для идентификатора исполнителя задачи.
    - TASK_EXECUTORS (str): Заголовок для исполнителей задачи.
    - TASK_ID (str): Заголовок для идентификатора задачи.
    - TASK_NAME (str): Заголовок для названия задачи.
    - TASK_OWNER_ID (str): Заголовок для идентификатора создателя задачи.
    - TASK_PROBLEM_ID (str): Заголовок для идентификатора проблемы задачи.
    - TASK_STATUS (str): Заголовок для статуса задачи.
    - TASK_TRANSFER_COUNTER (str): Заголовок для счетчика переноса задачи.
    - TASK_UPDATED_AT (str): Заголовок для даты обновления задачи.
    - TELEGRAM_USERNAME (str): Заголовок для Telegram username.
    - LICENSE_TERM (str): Заголовок для срока действия лицензии.
    - UPDATE_COMMENTS_TEXT (str): Заголовок для текста обновления комментария.
    - UPDATED_AT_USER (str): Заголовок для даты обновления пользователя.
    - VOTING_ID (str): Заголовок для ID голосования.
    - VOTING_MESSAGE_ID (str): Заголовок для ID сообщения голосования.
    - VOTING_RECORD_ID (str): Заголовок для ID записи голосования.
    - VOTING_TEXT (str): Заголовок для текста голосования.
    - VOTING_USER_ID (str): Заголовок для ID пользователя голосования.
    - WHATSAPP_USERNAME (str): Заголовок для Whatsapp username.
    """

    AVATAR_LINK_USER: str = 'Ссылка на аватар пользователя'
    BIRTHDAY_USER: str = 'День рождение пользователя'
    COMPANY_ID_TAG: str = 'id компании, в которой используется тэг'
    COMPANY_ID_USER: str = 'id компании, в которой работает пользователь'
    CREATE_COMMENTS_TEXT: str = 'Новый комментарий к треду.'
    CREATED_AT_USER: str = 'Дата создания профиля пользователя'
    CURRENT_DEPARTMENT_ID_USER: str = 'id отдела, в котором работает пользователь'
    DEPARTMENT_TRANSITION_DATE_USER: str = 'Последняя дата перехода из одного отдела в другой'
    EMAIL_USER: str = 'Электронная почта пользователя'
    EMPLOYEE_POSITION_USER: str = 'Позиция в коллективе, указывается админом компании'
    END_DATE_EMPLOYMENT_USER: str = 'Дата конца работы сотрудника в компании'
    IS_ACTIVE_USER: str = 'Активен ли пользователь'
    IS_SUPERUSER_ADMIN: str = 'Бул поле, для указания, является ли пользователь суперпользователем'
    LICENSE_ID_COMPANY: str = 'Ссылка на тип лицензии'
    LIMIT: str = 'Лимитировать список объектов'
    LOGO_COMPANY: str = 'Логотип'
    MAX_EMPLOYEES_COUNT: str = 'Максимальное количество сотрудников'
    MAX_MODERATORS_COUNT: str = 'Максимальное количество модераторов'
    MEETING_CREATED_AT: str = 'Дата создания'
    MEETING_DATE: str = 'Дата проведения встречи'
    MEETING_DESCRIPTION: str = 'Описание встречи'
    MEETING_FEEDBACK: str = 'Отзыв о встрече'
    MEETING_ID: str = 'Идентификатор встречи'
    MEETING_MEMBER_ID: str = 'Идентификатор участника'
    MEETING_MEMBERS: str = 'Участники встречи'
    MEETING_OWNER_ID: str = 'Идентификатор создателя'
    MEETING_PLACE: str = 'Место проведения встречи'
    MEETING_PROBLEM_ID: str = 'Идентификатор проблемы'
    MEETING_RESULT: str = 'Результат встречи'
    MEETING_STATUS: str = 'Статус встречи'
    MEETING_TITLE: str = 'Название встречи'
    MEETING_TRANSFER_COUNTER: str = 'Количество переносов'
    MEETING_UPDATED_AT: str = 'Дата обновления'
    MESSAGE_FEED_IMPORTANT: str = 'Важность треда.'
    MESSAGE_FEED_TEXT: str = 'Название треда.'
    NAME_COMPANY: str = 'Название компании'
    NAME_DEPARTMENT: str = 'Название отдела'
    NAME_LICENSE: str = 'Название лицензии'
    NAME_MODERATOR: str = 'Имя модератора сервиса'
    NAME_TAG: str = 'Имя тэга'
    NAME_USER: str = 'Имя пользователя сервиса'
    PARTICIPANT_ENGAGEMENT: str = 'Участие в встрече'
    PASSWORD_USER: str = 'Пароль пользователя'
    PATRONYMIC_MODERATOR: str = 'Отчество модератора сервиса'
    PATRONYMIC_USER: str = 'Отчество пользователя сервиса'
    PHONE_NUMBER_MODERATOR: str = 'Контактный телефон модератора сервиса'
    PHONE_NUMBER_USER: str = 'Контактный телефон пользователя сервиса'
    PREVIOUS_DEPARTMENT_ID_USER: str = 'id отдела, в котором работал пользователь до этого'
    PROBLEM_COLOR: str = 'Цвет проблемы'
    PROBLEM_COMPANY_ID: str = 'Идентификатор компании'
    PROBLEM_CREATED_AT: str = 'Дата создания'
    PROBLEM_DESCRIPTION: str = 'Описание проблемы'
    PROBLEM_ID: str = 'Идентификатор проблемы'
    PROBLEM_MEMBER_ID: str = 'Идентификатор участника'
    PROBLEM_MEMBER_STATUS: str = 'Статус участия'
    PROBLEM_MEMBERS: str = 'Участники проблемы'
    PROBLEM_NAME: str = 'Название проблемы'
    PROBLEM_OWNER_ID: str = 'Идентификатор владельца'
    PROBLEM_SOLUTION: str = 'Решение проблемы'
    PROBLEM_STATUS: str = 'Статус проблемы'
    PROBLEM_TYPE: str = 'Тип проблемы'
    PROBLEM_UPDATED_AT: str = 'Дата обновления'
    ROLE_USER: str = 'Роль пользователя компании.'
    SKIP: str = 'Пропустить n объектов'
    SLUG_COMPANY: str = 'Slug компании'
    SLUG_USER: str = 'Slug пользователя'
    START_DATE_EMPLOYMENT_USER: str = 'Дата начало работы сотрудника в компании'
    START_LICENSE_TIME_COMPANY: str = 'Дата начала действия лицензии'
    SURNAME_MODERATOR: str = 'Фамилия модератора сервиса'
    SURNAME_USER: str = 'Фамилия пользователя сервиса'
    TASK_CREATED_AT: str = 'Дата создания'
    TASK_DATE_COMPLETION: str = 'Дата выполнения'
    TASK_DESCRIPTION: str = 'Описание задачи'
    TASK_EXECUTOR_ID: str = 'Идентификатор исполнителя'
    TASK_EXECUTORS: str = 'Исполнители задачи'
    TASK_ID: str = 'Идентификатор задачи'
    TASK_NAME: str = 'Название задачи'
    TASK_OWNER_ID: str = 'Идентификатор создателя'
    TASK_PROBLEM_ID: str = 'Идентификатор проблемы'
    TASK_STATUS: str = 'Статус задачи'
    TASK_TRANSFER_COUNTER: str = 'Счетчик переноса'
    TASK_UPDATED_AT: str = 'Дата обновления'
    TELEGRAM_USERNAME: str = 'Имя пользователя в Telegram'
    LICENSE_TERM: str = 'Срок действия лицензии в днях'
    UPDATE_COMMENTS_TEXT: str = 'Обновить комментарий к треду.'
    UPDATED_AT_USER: str = 'Дата обновления профиля пользователя'
    VOTING_ID: str = 'ID голосования'
    VOTING_MESSAGE_ID: str = 'ID сообщения'
    VOTING_RECORD_ID: str = 'ID записи'
    VOTING_TEXT: str = 'Текст голосования'
    VOTING_USER_ID: str = 'ID пользователя'
    WHATSAPP_USERNAME: str = 'Имя пользователя в Whatsapp'


class ValidationConstants(ValidationBaseConstants):
    """
    Класс констант для хранения правил валидации данных.

    Наследует все константы из ValidationBaseConstants.

    Атрибуты:
    - ALLOWED_FILE_EXTENSIONS (tuple): Допустимые расширения файлов.
    - ALLOWED_FILE_SIZE (int): Максимальный допустимый размер файла.
    - LICENSE_TERM_REGEX (Pattern): Регулярное выражение для проверки срока лицензии.
    """

    ALLOWED_FILE_EXTENSIONS: tuple[str, ...] = ('.pdf', '.doc', '.docx')
    ALLOWED_FILE_SIZE: int = 10 * 1024 * 1024
    LICENSE_TERM_REGEX: Pattern[str] = compile(r'^P.*Y$|^P.*D$')
