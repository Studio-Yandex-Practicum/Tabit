from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import BaseTag, Company, AssociationUserTags


class TagUser(BaseTag):
    """
    Модель тэгов пользователей.

    Назначение:
        Админ от компании может для сотрудников своей компании придумывать свои тэги.

    Поля:
        id: Идентификационный номер тэга.
        name: Имя тега.
        company_id: Идентификатор компании, в которой будет использоваться тэг.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        user - AssociationUserTags -> UserTabit;
        company - Company.
    """

    user: Mapped[List['AssociationUserTags']] = relationship(back_populates='tag')
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'))
    company: Mapped['Company'] = relationship(back_populates='tags_users')