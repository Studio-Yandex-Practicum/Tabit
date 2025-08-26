from datetime import datetime
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models import BaseTabitModel, SurveysStatus
from src.models.annotations import int_pk


class ResearchType(BaseTabitModel):
    """
    Тип однотипного опроса (research).

    Назначение:
    - Определяет структуру и параметры опроса.
    - Создается модератором или админом.

    Поля:
    - id: Идентификатор.
    - company_id: Идентификатор компании, для которой создан тип опроса.
    - title: Заголовок опроса.
    - description: Описание опроса.
    - questions: JSON с вопросами и их типами.
    - is_active: Активен ли тип опроса.
    - created_by: ID пользователя, создавшего тип опроса.
    - created_at: Дата создания.
    - updated_at: Дата последнего обновления.
    """

    id: Mapped[int_pk]
    company_id: Mapped[int] = mapped_column(
        ForeignKey('company.id', ondelete='CASCADE'),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    questions: Mapped[str] = mapped_column(Text, nullable=False)  # JSON строка с вопросами
    is_active: Mapped[bool] = mapped_column(default=True)
    created_by: Mapped[UUID] = mapped_column(
        ForeignKey('companyuser.id', ondelete='SET NULL'),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'company_id={self.company_id!r}, '
            f'title={self.title!r}, '
            f'is_active={self.is_active!r})'
        )


class ResearchInstance(BaseTabitModel):
    """
    Экземпляр однотипного опроса (research).

    Назначение:
    - Конкретный опрос, созданный на основе типа.
    - Связывает тип опроса с пользователем и его ответами.

    Поля:
    - id: Идентификатор.
    - research_type_id: Идентификатор типа опроса.
    - user_id: ID пользователя, проходящего опрос.
    - status: Статус прохождения опроса.
    - started_at: Дата начала прохождения.
    - completed_at: Дата завершения.
    - answers: JSON с ответами пользователя.
    """

    id: Mapped[int_pk]
    research_type_id: Mapped[int] = mapped_column(
        ForeignKey('researchtype.id', ondelete='CASCADE'),
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('companyuser.id', ondelete='CASCADE'),
        nullable=False,
    )
    status: Mapped[SurveysStatus] = mapped_column(
        Enum(SurveysStatus), default=SurveysStatus.IN_PROGRESS
    )
    started_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    completed_at: Mapped[datetime] = mapped_column(nullable=True)
    answers: Mapped[str] = mapped_column(Text, nullable=True)  # JSON строка с ответами

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'research_type_id={self.research_type_id!r}, '
            f'user_id={self.user_id!r}, '
            f'status={self.status!r})'
        )
