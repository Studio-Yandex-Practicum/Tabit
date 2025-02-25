"""
Константы для моделей компании, департамента и сотрудника отдела.
"""

ERROR_INVALID_PASSWORD: str = 'Пароль не соответвует требованиям.'
ERROR_USER_ALREADY_EXISTS: str = 'Пользователь с данным email уже существует.'
ERROR_USER_NOT_EXISTS: str = 'Пользователь с таким UUID не существует.'

TITLE_NAME_COMPANY: str = 'Название компании'
TITLE_LOGO_COMPANY: str = 'Логотип'
TITLE_LICENSE_ID_COMPANY: str = 'Ссылка на тип лицензии'
TITLE_START_LICENSE_TIME_COMPANY: str = 'Дата начала действия лицензии'
TITLE_SLUG_COMPANY: str = 'Slug компании'

TITLE_NAME_DEPARTMENT: str = 'Название отдела'
TITLE_SLUG_DEPARTMENT: str = 'Slug отдела'

TEST_ERROR_INVALID_CHARACTERS_NAME = 'Имя содержит недопустимые символы!'
TEST_ERROR_INVALID_CHARACTERS_SURNAME = 'Фамилия содержит недопустимые символы!'
TEST_ERROR_LICENSE_FIELDS: str = (
    'Поля начала действия лицензии и тип лицензии заполняются одновременно.'
)
TEST_ERROR_UNIQUE_NAME_SURNAME = 'Имя и фамилия не могут совпадать!'
