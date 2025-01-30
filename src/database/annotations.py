"""Набор аннотаций для моделей."""

from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import mapped_column

from src.constants import (
    LENGTH_NAME_PROBLEM,
    LENGTH_NAME_USER,
    LENGTH_SMALL_NAME,
    LENGTH_FILE_LINK,
    LENGTH_SLUG,
    ZERO,
)

int_pk = Annotated[int, mapped_column(primary_key=True, unique=True)]
name_field = Annotated[str, mapped_column(String(LENGTH_NAME_USER))]
license_name_field = Annotated[str, mapped_column(String(LENGTH_NAME_USER))]
description = Annotated[Optional[str], mapped_column(Text, nullable=True)]
tag_name_field = Annotated[
    str, mapped_column(String(LENGTH_SMALL_NAME), unique=True, nullable=False)
]
url_link_field = Annotated[str, mapped_column(String(LENGTH_FILE_LINK))]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=datetime.now)]
owner = Annotated[Optional[UUID], mapped_column(ForeignKey('usertabit.id'), nullable=True)]
int_zero = Annotated[int, mapped_column(Integer, nullable=False, default=ZERO)]
nullable_timestamp = Annotated[Optional[DateTime], mapped_column(DateTime, nullable=True)]
name_problem = Annotated[str, mapped_column(String(LENGTH_NAME_PROBLEM), nullable=False)]
slug = Annotated[str, mapped_column(String(LENGTH_SLUG), nullable=False, unique=True)]
