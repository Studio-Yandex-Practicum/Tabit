import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, TIMESTAMP, Text, ForeignKey
from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.dialects.postgresql import UUID


class PreBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP)


BaseTabitModel = declarative_base(cls=PreBase)


class BaseUser(BaseTabitModel):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String)
    surname: Mapped[str] = mapped_column(String)
    patronymic: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    phone_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String)


class BaseActivity(BaseTabitModel):
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)


class BaseFieldName(BaseTabitModel):
    name: Mapped[str] = mapped_column(String)


class LicenseType(BaseTabitModel):
    name: Mapped[str] = mapped_column(String)
    license_term: Mapped[datetime] = mapped_column(TIMESTAMP)


class BulletinBoard(BaseFieldName):
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)


class BaseLinkedTable(BaseTabitModel):
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("user.id"))
