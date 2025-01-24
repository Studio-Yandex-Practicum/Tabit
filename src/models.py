"""Базовые модели проекта."""

from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from src.constants import LENGTH_NAME_USER, LENGTH_SMALL_NAME, LENGTH_FILE_LINK, ZERO

int_pk = Annotated[int, mapped_column(primary_key=True, unique=True)]
name_field = Annotated[str, mapped_column(String(LENGTH_NAME_USER))]
description = Annotated[Optional[str], mapped_column(Text, nullable=True)]
tag_name_field = Annotated[
    str, mapped_column(String(LENGTH_SMALL_NAME), unique=True, nullable=False)
]
url_link_field = Annotated[str, mapped_column(String(LENGTH_FILE_LINK))]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=datetime.now)]
owner = Annotated[Optional[UUID], mapped_column(ForeignKey('usertabit.id'), nullable=True)]
int_zero = Annotated[int, mapped_column(Integer, nullable=False, default=ZERO)]
nullable_timestamp = Annotated[Optional[DateTime], mapped_column(DateTime, nullable=True)]


class BaseTabitModel(AsyncAttrs, DeclarativeBase):
    """Базовая модель проекта."""

    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class BaseUser(BaseTabitModel, SQLAlchemyBaseUserTableUUID):
    """Базовая модель пользователей. Абстрактная модель"""

    __abstract__ = True

    name: Mapped[name_field]
    surname: Mapped[name_field]
    patronymic: Mapped[name_field]
    phone_number: Mapped[str]

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'name={self.name!r}, '
            f'surname={self.surname!r}, '
            f'patronymic={self.patronymic!r})'
        )


class BaseTag(BaseTabitModel):
    """Базовая модель тэгов. Абстрактная модель"""

    __abstract__ = True

    id: Mapped[int_pk]
    name: Mapped[tag_name_field]

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id!r}, name={self.name!r})'


class BaseFileLink(BaseTabitModel):
    """Базовая модель файлов. Абстрактная модель"""

    __abstract__ = True

    id: Mapped[int_pk]
    file_path: Mapped[url_link_field]

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id!r}, file_path={self.file_path!r})'
