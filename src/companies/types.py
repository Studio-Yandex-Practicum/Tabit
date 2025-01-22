from typing import Annotated, Optional
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text
from .constants import (
    COMPANY_NAME_LENGTH,
    DEPARTMENT_NAME_LENGTH,
    MAX_ADMINS_COUNT_DEFAULT,
    MAX_EMPLOYEES_COUNT_DEFAULT,
)


# Название компании должно быть уникальным во всей базе
company_name = Annotated[
    str, mapped_column(String(COMPANY_NAME_LENGTH), nullable=False, unique=True)
]

# Название департамента проверяется на уникальность только в пределах компании
department_name = Annotated[
    str, mapped_column(String(DEPARTMENT_NAME_LENGTH), nullable=False)
]

# Общие аннотации
id_pk = Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]
# Поле лицензии может быть пустым, если у компании нет лицензии
nullable_timestamp = Annotated[
    Optional[DateTime], mapped_column(DateTime, nullable=True)
]

# Внешние ключи
company_id = Annotated[int, mapped_column(ForeignKey('company.id'), nullable=False)]
department_id = Annotated[
    int, mapped_column(ForeignKey('department.id'), nullable=False)
]
user_id = Annotated[int, mapped_column(ForeignKey('usertabit.uuid'), nullable=True)]
# Поле лицензии может быть пустым, если компания пока без лицензии
license_id = Annotated[
    Optional[int], mapped_column(ForeignKey('licensetype.id'), nullable=True)
]

# Описание компании (опционально)
description = Annotated[str, mapped_column(Text, nullable=True)]

# Логотип компании: хранение URL или base64-кода изображения
logo = Annotated[str, mapped_column(Text, nullable=True)]

# Ограничения для компании
max_admins_count = Annotated[
    int, mapped_column(Integer, nullable=False, default=MAX_ADMINS_COUNT_DEFAULT)
]
max_employees_count = Annotated[
    int, mapped_column(Integer, nullable=False, default=MAX_EMPLOYEES_COUNT_DEFAULT)
]
