"""Базовые модели проекта."""

from typing import Optional

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr

from src.database.annotations import (
    created_at,
    int_pk,
    name_field,
    patronymic_field,
    tag_name_field,
    updated_at,
    url_link_field,
)


class BaseTabitModel(AsyncAttrs, DeclarativeBase):
    """
    Базовая модель проекта. Абстрактная модель.

    Поля:
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.
    """

    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class BaseUser(BaseTabitModel, SQLAlchemyBaseUserTableUUID):  # type: ignore[misc]
    """
    Базовая модель пользователей. Абстрактная модель.

    Поля:
        id: Идентификационный номер пользователя - UUID.
        name: Имя пользователя.
        surname: Фамилия пользователя.
        patronymic: Отчество пользователя.
        phone_number: Номер телефона пользователя.
        email: Адрес электронной почты пользователя.
        hashed_password: Хэш пароля пользователя.
        is_active: bool - активен ли пользователь.
        is_superuser: bool - суперюзер ли пользователь.
        is_verified: bool - проверен ли пользователь.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.
    """

    __abstract__ = True

    name: Mapped[name_field]
    surname: Mapped[name_field]
    patronymic: Mapped[patronymic_field]
    phone_number: Mapped[Optional[str]]

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'name={self.name!r}, '
            f'surname={self.surname!r}, '
            f'patronymic={self.patronymic!r})'
        )


class BaseTag(BaseTabitModel):
    """
    Базовая модель тэгов. Абстрактная модель

    Поля:
        id: Идентификационный номер тэга.
        name: Имя тега.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.
    """

    __abstract__ = True

    id: Mapped[int_pk]
    name: Mapped[tag_name_field]

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id!r}, name={self.name!r})'


class BaseFileLink(BaseTabitModel):
    """
    Базовая модель файлов. Абстрактная модель

    Поля:
        id: Идентификационный номер записи.
        file_path: Путь до файла.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.
    """

    __abstract__ = True

    id: Mapped[int_pk]
    file_path: Mapped[url_link_field]

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id!r}, file_path={self.file_path!r})'
