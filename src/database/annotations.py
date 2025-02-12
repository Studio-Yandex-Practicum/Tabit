"""Набор аннотаций для моделей."""

from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import mapped_column

from src.constants import (
    LENGTH_FILE_LINK,
    LENGTH_NAME_PROBLEM,
    LENGTH_NAME_USER,
    LENGTH_SLUG,
    LENGTH_SMALL_NAME,
    ZERO,
)

int_pk = Annotated[int, mapped_column(primary_key=True, unique=True)]
name_field = Annotated[str, mapped_column(String(LENGTH_NAME_USER))]
patronymic_field = Annotated[Optional[str], mapped_column(String(LENGTH_NAME_USER), nullable=True)]
license_name_field = Annotated[str, mapped_column(String(LENGTH_NAME_USER), unique=True)]
description = Annotated[Optional[str], mapped_column(Text, nullable=True)]
tag_name_field = Annotated[
    str, mapped_column(String(LENGTH_SMALL_NAME), unique=True, nullable=False)
]
url_link_field = Annotated[Optional[str], mapped_column(String(LENGTH_FILE_LINK), nullable=True)]
created_at = Annotated[
    datetime, mapped_column(type_=TIMESTAMP(timezone=True), server_default=func.now())
]
updated_at = Annotated[
    datetime,
    mapped_column(
        type_=TIMESTAMP(timezone=True), server_default=func.now(), onupdate=datetime.now
    ),
]
timestamp_nullable = Annotated[
    Optional[datetime],
    mapped_column(type_=TIMESTAMP(timezone=True), nullable=True),
]
owner = Annotated[UUID, mapped_column(ForeignKey('usertabit.id'), nullable=False)]
int_zero = Annotated[int, mapped_column(Integer, nullable=False, default=ZERO)]
name_problem = Annotated[str, mapped_column(String(LENGTH_NAME_PROBLEM), nullable=False)]
slug = Annotated[str, mapped_column(String(LENGTH_SLUG), nullable=False, unique=True)]
