from config.constants.src import LengthBase, TextErrorBase, TitleBase


class Length(LengthBase):
    """Класс для хранения констант, связанных с допустимой длиной полей.

    Наследует все константы из LengthBase.

    Атрибуты:
        MAX_EMAIL: Максимально допустимая длина email-адреса.
    """

    MAX_EMAIL: int = 100


class TextError(TextErrorBase):
    """Класс для хранения стандартных текстов ошибок приложения.

    Наследует все константы из TextErrorBase.

    Атрибуты:
        CAN_NOT_EMPTY_STRING: Сообщение об ошибке при пустом поле ввода.
    """

    CAN_NOT_EMPTY_STRING: str = 'Значение не может быть пустой строкой!'


class Title(TitleBase):
    """Класс для хранения заголовков полей.

    Наследует все константы из TitleBase.

    Атрибуты:
        EMAIL_NAME: Заголовок поля для ввода email-адреса получателя.
        SUBJECT_EMAIL: Заголовок поля для ввода темы письма.
        USER_MESSAGE: Заголовок поля для ввода сообщения пользователя.
    """

    EMAIL_NAME: str = 'Email получателя.'
    SUBJECT_EMAIL: str = 'Тема письма.'
    USER_MESSAGE: str = 'Сообщение пользователя.'
