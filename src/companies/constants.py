"""
Константы для моделей компании, департамента и сотрудника отдела.
"""

import string

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
SHORT_SYMBOLS = string.ascii_letters
GENERATED_SLUG_SUFFIX_RANGE = 3
ATTEMPTS = 100
SLUG_NOT_GENERATED = (
    f'Сделано {ATTEMPTS} попыток, но сгенерировать slug не удалось. Попробуйте снова.'
)
# Фильтрация и сортировка для лицензии
FILTER_NAME_DESCRIPTION = 'Фильтр по названию компании'
SORTING_DESCRIPTION = (
    "Сортировка по полю (name, created_at, updated_at). '-' означает сортировку в обратном порядке"
)
