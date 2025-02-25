"""Модуль CRUD для компании."""

from src.core.crud_base import CRUDBase
from src.models import Company


class CRUDTabitCompany(CRUDBase):
    """CRUD операции для модели компании."""


tabit_company_crud = CRUDTabitCompany(Company)
