"""Модуль CRUD для отдела."""

from src.companies.models import Department
from src.crud import CRUDBase


class CRUDCompanyDepartments(CRUDBase):
    """CRUD операций для модели отделов компании."""

    pass


company_departments_crud = CRUDCompanyDepartments(Department)
