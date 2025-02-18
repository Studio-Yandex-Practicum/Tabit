"""
Константы для моделей компании и департамента.
"""


ERROR_INVALID_PASSWORD = 'Пароль не соответвует требованиям.'
ERROR_USER_ALREADY_EXISTS = 'Пользователь с данным email уже существует.'
ERROR_USER_NOT_EXISTS = 'Пользователь с таким UUID не существует.'

title_name_company: str = 'Название компании'
title_logo_company: str = 'Логотип'
title_license_id_company: str = 'Ссылка на тип лицензии'
title_start_license_time: str = 'Дата начала действия лицензии'
title_slug_company: str = 'Slug компании'

TEST_ERROR_LICENSE_FIELDS: str = (
    'Поля начала действия лицензии и тип лицензии заполняются одновременно.'
)
