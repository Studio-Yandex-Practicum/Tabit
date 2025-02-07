from typing import Any, List, Optional

from pydantic import BaseModel, Field

from src.constants import DEFAULT_SKIP, DEFAULT_LIMIT


class CompanyFilterSchema(BaseModel):
    """
    Схема-фильтр компаний.

    Используется для обработки query-параметров:
    пагинация, сортировка и фильтрация списка компаний.
    """

    skip: int = Field(DEFAULT_SKIP, ge=0, title='Пропустить n объектов')
    limit: int = Field(DEFAULT_LIMIT, ge=1, title='Лимитировать список объектов')
    filters: Optional[dict[str, Any]] = None
    order_by: Optional[List[str]] = None
