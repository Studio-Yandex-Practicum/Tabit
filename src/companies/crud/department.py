"""Модуль CRUD для отдела."""

from src.models import Department
from src.core.crud_base import CRUDBase


class CRUDCompanyDepartments(CRUDBase):
    """CRUD операций для модели отделов компании."""

    pass


company_departments_crud = CRUDCompanyDepartments(Department)
