"""Базовые модели проекта."""

from datetime import datetime
from typing import Annotated

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import String, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from src.constants import LENGTH_NAME_USER, LENGTH_SMALL_NAME
from src.database.database import Base

int_pk = Annotated[int, mapped_column(primary_key=True)]
name_field = Annotated[str, mapped_column(String(LENGTH_NAME_USER))]
tag_name_field = Annotated[str, mapped_column(String(LENGTH_SMALL_NAME))]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[
    datetime, mapped_column(server_default=func.now(), onupdate=datetime.now)
]


class BaseTabitModel(AsyncAttrs, Base):
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
