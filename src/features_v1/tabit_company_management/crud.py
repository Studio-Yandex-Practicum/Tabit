"""Модуль CRUD для компании."""

from src.models import Company
from src.core.crud_base import CRUDBase


class CRUDTabitCompany(CRUDBase):
    """CRUD операции для модели компании."""


tabit_company_crud = CRUDTabitCompany(Company)
