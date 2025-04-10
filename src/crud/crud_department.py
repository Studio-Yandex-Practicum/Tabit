"""Модуль CRUD для отдела."""

from src.crud.crud_base import CRUDBase
from src.models import Department


class CRUDDepartments(CRUDBase):
    """CRUD операций для модели отделов компании."""

    pass


department_crud = CRUDDepartments(Department)
