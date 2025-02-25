"""Модуль CRUD для отдела."""

from src.core.crud_base import CRUDBase
from src.models import Department


class CRUDDepartments(CRUDBase):
    """CRUD операций для модели отделов компании."""

    pass


departments_crud = CRUDDepartments(Department)
