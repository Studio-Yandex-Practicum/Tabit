from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import (
    declarative_base,
    declared_attr,
    Mapped,
    mapped_column,
)


class PreBase:
    """Преднастройка базовой модели проекта."""

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(insert_default=func.now())


BaseTabitModel = declarative_base(
    cls=PreBase,
    name='BaseTabitModel',
)
