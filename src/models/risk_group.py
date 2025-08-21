"""Модели для групп риска."""

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import (
    BaseTabitModel,
    CommunicationType,
    CompanyUser,
    RiskGroupType,
    SociometricCategoryEnum
)
from src.models.annotations import int_pk, owner


class RiskGroup(BaseTabitModel):
    """
    Модель группы риска.

    Назначение:
        Содержит информацию о наличии пользователя в группе риска.

    Поля:
        id: Идентификатор.
        owner_id: Сотрудник компании. Внешний ключ.
        risk_group_type: Пользователю присваивается вид группы риска.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        user - CompanyUser.
    """

    id: Mapped[int_pk]
    user_id: Mapped[owner]
    user: Mapped['CompanyUser'] = relationship(back_populates='risk_group_user')
    risk_group_type: Mapped[RiskGroupType] = mapped_column(Enum(RiskGroupType))

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'user_id={self.user_id!r}, '
            f'reason={self.risk_group_type!r})'
        )


class Leadership(BaseTabitModel):
    """
    Модель лидерства.

    Назначение:
        Содержит информацию о наличии у пользователя лидерских качеств.

    Поля:
        id: Идентификатор.
        owner_id: Сотрудник компании. Внешний ключ.
        leadership_type: Пользователю присваивается вид лидерства.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        user - CompanyUser.
    """

    id: Mapped[int_pk]
    user_id: Mapped[owner]
    user: Mapped['CompanyUser'] = relationship(back_populates='leadership')
    leadership_type: Mapped[SociometricCategoryEnum] = mapped_column(Enum(SociometricCategoryEnum))

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'user_id={self.user_id!r}, '
            f'type_leadership={self.leadership_type})'
        )


class Communication(BaseTabitModel):
    """
    Модель коммуникационной нагрузки пользователей.

    Назначение:
        Содержит информацию о коммуникационных качествах пользователей.

    Поля:
        id: Идентификатор.
        owner_id: Сотрудник компании. Внешний ключ.
        communication_type: пользователю присваивается вид коммуникационной нагрузки.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        user - CompanyUser.
    """
    id: Mapped[int_pk]
    user_id: Mapped[owner]
    user: Mapped['CompanyUser'] = relationship(back_populates='communication')
    communication_type: Mapped[CommunicationType] = mapped_column(Enum(CommunicationType))

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'user_id={self.user_id!r}, '
            f'type_leadership={self.communication_type})'
        )
