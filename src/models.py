from datetime import date
import uuid

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from .database import BaseTabitModel, str_uniq, str_null_true, int_pk


class BaseUser(BaseTabitModel):
    """Base model is used for all users in Tabit app"""

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str]
    surname: Mapped[str]
    patronymic: Mapped[str]
    email: Mapped[str_uniq]
    phone_number: Mapped[str_null_true]
    hashed_password: Mapped[str]

    def __str__(self):
        return (
            f"{self.__class__.__name__}({self.id=}), "
            f"{self.name=}, "
            f"{self.surname=}"
        )

    def __repr__(self):
        return str(self)


class TabitAdminUser(BaseUser):
    """Tabit Admin User Model"""

    pass


class LicenseType(BaseUser):
    """License Type Model"""

    id: Mapped[int_pk]
    name: Mapped[str_uniq]
    license_term: Mapped[date]
