from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.annotations import description, int_pk, name_problem, owner
from src.database.models import BaseTabitModel
from src.problems.models.enums import ColorProblem, StatusProblem, TypeProblem

if TYPE_CHECKING:
    from src.companies.models import Company
    from src.problems.models import AssociationUserProblem, FileProblem, Meeting, MessageFeed, Task
    from src.users.models import UserTabit


class Problem(BaseTabitModel):
    """
    Модель проблемы.

    Назначение:
        Содержит информацию о проблеме, которую предстоит решить.

    Поля:
        id: Идентификатор.
        name: Название проблемы.
        description: Описание.
        company_id: Идентификатор компании, к которой относится проблема.
        color: Проблеме присваивается цвет.
        type: Проблема относится к определенному типу.
        status: Статус проблемы.
        owner_id: Автор проблемы. Внешний ключ.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        company - Company
        owner - UserTabit;
        meetings - Meeting: связь к назначенным встречам, для решения проблемы;
        tasks - Task: связь к задачам, для решения проблемы;
        messages - MessageFeed: связь к ленте сообщений;
        file - FileProblem: к проблеме могут быть прикреплены файлы.
    """

    id: Mapped[int_pk]
    name: Mapped[name_problem]
    description: Mapped[description]
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'))
    company: Mapped['Company'] = relationship(back_populates='problems')
    color: Mapped['ColorProblem']
    type: Mapped['TypeProblem']
    status: Mapped['StatusProblem']
    # TODO: Не думаю, что нужно удалять проблему, если будет удален пользователь, создавший её.
    # Но вот если удалят компанию - должна удалятся. Можно реализовать за счет связей.
    owner_id: Mapped[owner]
    owner: Mapped['UserTabit'] = relationship(back_populates='problem_owner')
    members: Mapped[List['AssociationUserProblem']] = relationship(
        back_populates='problem', cascade='all, delete-orphan'
    )
    meetings: Mapped[List['Meeting']] = relationship(
        back_populates='problem', cascade='all, delete-orphan'
    )
    tasks: Mapped[List['Task']] = relationship(
        back_populates='problem', cascade='all, delete-orphan'
    )
    messages: Mapped[List['MessageFeed']] = relationship(
        back_populates='problem', cascade='all, delete-orphan'
    )
    file: Mapped[List['FileProblem']] = relationship(
        back_populates='problem', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'name={self.name!r}, '
            f'owner_id={self.owner_id!r}, '
            f'type={self.type!r}, '
            f'status={self.status!r})'
        )
