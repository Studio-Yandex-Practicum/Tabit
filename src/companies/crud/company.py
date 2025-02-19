"""Модуль CRUD для компании."""

from src.companies.models import Company
from src.crud import CRUDBase


class CRUDCompany(CRUDBase):
    """CRUD операции для модели компании."""

    pass


company_crud = CRUDCompany(Company)
