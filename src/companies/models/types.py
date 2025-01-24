from typing import Annotated, Optional
from sqlalchemy.orm import mapped_column
from sqlalchemy import DateTime, Integer


id_pk = Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]

nullable_timestamp = Annotated[Optional[DateTime], mapped_column(DateTime, nullable=True)]
