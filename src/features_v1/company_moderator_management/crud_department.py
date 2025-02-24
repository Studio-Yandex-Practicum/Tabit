"""Модуль CRUD для отдела."""

from src.models import Department
from src.core.crud_base import CRUDBase


class CRUDDepartments(CRUDBase):
    """CRUD операций для модели отделов компании."""

    pass


departments_crud = CRUDDepartments(Department)
