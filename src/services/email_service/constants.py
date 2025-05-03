"""
Модуль констант для работы с email-сообщениями

Содержит константы, используемые для валидации, обработки и отображения
email-сообщений в приложении.
Организован по принципу тематической группировки констант в логические классы.

Структура модуля:
- LengthConstants: ограничения длины.
- TextErrorConstants: стандартные тексты ошибок.
- TitleConstants: заголовки полей и элементов интерфейса.

Все классы наследуют соответствующие базовые классы из cosrc.core.constants,
что обеспечивает согласованность констант во всем проекте.

Импортируемые базовые классы:
- LengthBaseConstants: базовые ограничения длины.
- TextErrorBaseConstants: стандартные тексты ошибок.
- TitleBaseConstants: базовые заголовки элементов.

Важные особенности:
- Все классы наследуют соответствующие базовые классы констант.
- Дополнительные константы добавляются в дочерние классы.
- Все строковые константы должны быть типизированы.
- Все константы имеют явные type hints (аннотации типов).
- Наследуемые значения могут быть переопределены.

Примеры использования:
- from src.services.constants import LengthConstants, TextErrorConstants, TitleConstants
- if len(email) > LengthConstants.MAX_EMAIL:
- raise ValueError(TextErrorConstants.CAN_NOT_EMPTY_STRING)
- email_field_label = TitleConstants.EMAIL_NAME
"""

from src.core.constants import LengthBaseConstants, TextErrorBaseConstants, TitleBaseConstants


class LengthConstants(LengthBaseConstants):
    """
    Класс для хранения констант, связанных с допустимой длиной полей.

    Наследует все константы из LengthBaseConstants.

    Атрибуты:
    - MAX_EMAIL (int): Максимально допустимая длина email-адреса.
    """

    MAX_EMAIL: int = 100


class TextErrorConstants(TextErrorBaseConstants):
    """
    Класс констант для хранения стандартных текстов ошибок приложения.

    Наследует все константы из TextErrorBaseConstants.

    Атрибуты:
    - CAN_NOT_EMPTY_STRING (str): Сообщение об ошибке при пустом поле ввода.
    """

    CAN_NOT_EMPTY_STRING: str = 'Значение не может быть пустой строкой!'


class TitleConstants(TitleBaseConstants):
    """
    Класс констант для хранения заголовков полей.

    Наследует все константы из TitleBaseConstants.

    Атрибуты:
    - EMAIL_NAME (str): Заголовок поля для ввода email-адреса получателя.
    - SUBJECT_EMAIL (str): Заголовок поля для ввода темы письма.
    - USER_MESSAGE (str): Заголовок поля для ввода сообщения пользователя.
    """

    EMAIL_NAME: str = 'Email получателя.'
    SUBJECT_EMAIL: str = 'Тема письма.'
    USER_MESSAGE: str = 'Сообщение пользователя.'
